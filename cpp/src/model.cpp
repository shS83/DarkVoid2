#include "model.hpp"
#include <stdexcept>

namespace dv {
Vec Vec::unit(Vec fallback) const {
    const double n = length();
    return n > 0 ? *this * (1.0 / n) : fallback;
}
Vec Vec::rotated(double degrees) const {
    const double angle = degrees * pi / 180;
    return {x * std::cos(angle) - y * std::sin(angle),
            x * std::sin(angle) + y * std::cos(angle)};
}
bool Rect::overlaps(Rect b) const {
    return x < b.x + b.w && x + w > b.x && y < b.y + b.h && y + h > b.y;
}
Rect Rect::inset(double n) const {
    return {x + std::min(n, w / 2), y + std::min(n, h / 2),
            std::max(0.0, w - 2 * n), std::max(0.0, h - 2 * n)};
}
Rect Body::bounds() const {
    const double c = std::abs(std::cos(angle * pi / 180));
    const double s = std::abs(std::sin(angle * pi / 180));
    const double w = size.x * c + size.y * s, h = size.x * s + size.y * c;
    return {pos.x - w / 2, pos.y - h / 2, w, h};
}
Vec image_size(const Catalog& catalog, const std::string& image, double scale) {
    const auto& mask = catalog.at(image);
    return {mask.w * scale, mask.h * scale};
}
Rect visible_bounds(const Body& body, const Catalog& catalog) {
    if (body.image.empty()) return body.bounds();
    const auto& mask = catalog.at(body.image);
    const auto crop = mask.visible_bounds;
    if (crop.w <= 0 || crop.h <= 0) return body.bounds();
    const Vec scale{body.size.x / mask.w, body.size.y / mask.h};
    const Vec local_center{(crop.x + crop.w / 2) * scale.x - body.size.x / 2,
                           (crop.y + crop.h / 2) * scale.y - body.size.y / 2};
    return Body{"", body.pos + local_center.rotated(body.angle),
                {crop.w * scale.x, crop.h * scale.y}, body.angle}.bounds();
}
bool opaque_at(const Body& body, Vec point, const Catalog& catalog) {
    const Vec local = (point - body.pos).rotated(-body.angle) + body.size * 0.5;
    if (local.x < 0 || local.y < 0 || local.x >= body.size.x || local.y >= body.size.y)
        return false;
    if (body.image.empty()) return true;
    const auto& mask = catalog.at(body.image);
    const int x = static_cast<int>(local.x / body.size.x * mask.w);
    const int y = static_cast<int>(local.y / body.size.y * mask.h);
    return mask.alpha.at(static_cast<std::size_t>(y * mask.w + x)) > 127;
}
bool mask_collision(const Body& a, const Body& b, const Catalog& catalog) {
    const Rect ar = a.bounds(), br = b.bounds();
    if (!ar.overlaps(br)) return false;
    const int left = static_cast<int>(std::floor(std::max(ar.x, br.x)));
    const int top = static_cast<int>(std::floor(std::max(ar.y, br.y)));
    const int right = static_cast<int>(std::ceil(std::min(ar.x + ar.w, br.x + br.w)));
    const int bottom = static_cast<int>(std::ceil(std::min(ar.y + ar.h, br.y + br.h)));
    for (int y = top; y < bottom; ++y)
        for (int x = left; x < right; ++x) {
            const Vec point{x + 0.5, y + 0.5};
            if (opaque_at(a, point, catalog) && opaque_at(b, point, catalog)) return true;
        }
    return false;
}

namespace {
struct EnemySpec { const char* name; const char* image; Weapon weapon; double delay, timer; };
const std::array<EnemySpec, 11> enemy_specs{{
    {"Boyscout", "purplealus", Weapon::Orb, 1, .8},
    {"Turbo", "redhawk", Weapon::Pellet, 1, .8},
    {"Redhawk", "redalus", Weapon::Pellet, 1, .8},
    {"robotector", "robotector", Weapon::Orb, .8, .6},
    {"Bluehawk", "bluehawk", Weapon::Blue, 2, .8},
    {"John Dark Void", "turqoiseship", Weapon::Blue, 2, .8},
    {"the Lilac Thruster", "lilac-thrusters", Weapon::Blue, 2, .8},
    {"Some Drone", "grayship", Weapon::Orb, 1.4, 1},
    {"Blackhawk", "blackhawk", Weapon::Orb, 1.4, 1},
    {"The Wasp", "orangeship", Weapon::Pellet, 1.2, .8},
    {"Swamp Thing", "vihree-alus", Weapon::Pellet, 1.4, 1}
}};
const std::array<const char*, 5> boss_names{
    "Dark Crusader", "Eldritch Marauder", "Aural Alien", "Void Dreadnought", "Terrain Automaton"};
const std::array<const char*, 5> boss_images{
    "dark-crusader", "boss-2", "foobarhead1", "stage4_boss_void_dreadnought_full", "stage5_terrain_automaton"};
const std::array<int, 5> boss_hp{300, 400, 500, 750, 900};
const std::array<double, 5> boss_y{-200, -400, -300, -360, -300};
template<class T, class Predicate> void erase_if(std::vector<T>& items, Predicate predicate) {
    items.erase(std::remove_if(items.begin(), items.end(), predicate), items.end());
}
}

Model::Model(const Catalog& images, std::uint32_t seed) : catalog(images), rng_(seed) { reset(); }
double Model::random(double a, double b) { return std::uniform_real_distribution<double>(a, b)(rng_); }
int Model::random_int(int a, int b) { return std::uniform_int_distribution<int>(a, b)(rng_); }
bool Model::boss_present() const {
    return std::any_of(enemies.begin(), enemies.end(), [](const Enemy& e) { return e.boss && !e.dead; });
}
void Model::reset(int initial_stage, bool skip_intro) {
    if (initial_stage < 1 || initial_stage > 5) throw std::invalid_argument("Stage must be 1..5");
    stage = initial_stage;
    phase = stage == 5 ? Phase::Terrain : Phase::Space;
    score = 0; elapsed = stage_time = ending_time = phase_time = fade = 0;
    game_over = victory = paused = false;
    banner = 2.4;
    enemies.clear(); bullets.clear(); particles.clear(); pickups.clear(); explosions.clear();
    sounds.clear(); stars.clear(); ocean.clear();
    ocean_index_ = 1;
    enemy_timer_ = rock_timer_ = 0;
    enemy_delay_ = random(1.5, 10); rock_delay_ = random(5, 20);
    player = Player{};
    player.intro_active = !skip_intro;
    player.scale = skip_intro ? .12 : .65;
    player.body = {"ships/finnfighter.png", {width / 2, skip_intro ? 840.0 : height + 220},
                   image_size(catalog, "ships/finnfighter.png", player.scale), 0};
    for (int i = 0; i < 200; ++i)
        stars.push_back({{random(0, width), random(0, height)}, random(80, 420),
                        static_cast<double>(random_int(1, 3))});
    if (stage == 5) update_ocean(0);
}
void Model::emit(Vec pos, Vec velocity, Color color, double life, double size,
                 double drag, double gravity) {
    // Bound transient allocations during long bullet-heavy fights.
    if (particles.size() < 20000)
        particles.push_back({pos, velocity, color, life, life, size, gravity, drag});
}
void Model::burst(Vec pos, int count, Color color) {
    for (int i = 0; i < count; ++i)
        emit(pos, Vec{random(180, 1050), 0}.rotated(random(0, 360)),
             color, random(.25, .95), random(2, 5), .96, 100);
}
void Model::reset_powers() {
    player.spread = player.fast = player.rapid = player.piercing = false;
    player.rail_timer = 0;
}
void Model::apply_power(Power kind) {
    switch (kind) {
    case Power::Health: player.lives += 3; break;
    case Power::Shield: player.shields += 3 + std::min(stage - 1, 3); break;
    case Power::Spread:
        reset_powers(); player.spread = true; player.power_timer = 12; break;
    case Power::Speed: player.fast = true; player.power_timer = 12; break;
    case Power::Laser: player.rapid = true; player.power_timer = 12; break;
    case Power::Cannon:
        reset_powers(); player.rail_timer = player.power_timer = 12; break;
    case Power::Piercing: player.piercing = true; player.power_timer = 25; break;
    }
    sounds.push_back({"levelup.wav", .5});
}
bool Model::activate_shield() {
    if (game_over || transitioning() || player.intro_active || player.shields <= 0
        || player.shield_timer > 0) return false;
    --player.shields;
    player.shield_timer = 5;
    return true;
}
void Model::hit_player(const std::string& killer) {
    if (!player.alive || player.intro_active || player.invincible > 0) return;
    if (player.shield_timer > 0) {
        sounds.push_back({"ding.mp3", .5});
        return;
    }
    --player.lives;
    player.invincible = 2;
    player.killer = killer;
    burst(player.body.pos, 100);
    sounds.push_back({"clink.wav", .5});
    if (player.lives <= 0) {
        player.alive = false;
        explosions.push_back({player.body.pos, 0, false});
        burst(player.body.pos, 900);
        sounds.push_back({"explosion1-long.wav", .7});
        end_game(false);
    }
}
void Model::end_game(bool won) {
    if (game_over) return;
    game_over = true;
    victory = won;
    ending_time = 0;
    if (won) player.killer = "No-one";
    else sounds.push_back({"gameover.wav", .4});
}
void Model::player_bullet(Vec pos, Vec velocity, Weapon kind) {
    Body body;
    body.pos = pos;
    if (kind == Weapon::Main) {
        body.image = "laser.png";
        body.size = image_size(catalog, body.image);
    } else if (kind == Weapon::Rail) {
        body.image = "laser-red.png";
        body.size = {30, 120};
    } else {
        body.size = kind == Weapon::Tracer ? Vec{5, 24} : Vec{3, 14};
        body.angle = std::atan2(velocity.y, velocity.x) * 180 / pi + 90;
    }
    bullets.push_back({body, velocity, kind, "", 0, 0, true, player.piercing, false});
}
void Model::enemy_bullet(Vec pos, Vec velocity, Weapon kind, const std::string& owner) {
    Vec size = kind == Weapon::Blue ? Vec{18, 54} : Vec{46, 46};
    const double angle = kind == Weapon::Blue ? std::atan2(velocity.y, velocity.x) * 180 / pi + 90 : 0;
    bullets.push_back({{"", pos, size, angle}, velocity, kind, owner,
                       kind == Weapon::Blue ? 4.0 : 6.0, 0, false, false, false});
}
void Model::update_player(double dt, const Input& input) {
    if (player.intro_active) {
        player.intro += dt;
        if (player.intro < 2.45) {
            const double t = 1 - std::pow(1 - player.intro / 2.45, 3);
            player.body.pos = lerp({width / 2, height + 220}, {width / 2, 840}, t);
        } else {
            const double t = 1 - std::pow(1 - std::min(1.0, (player.intro - 2.45) / 2.10), 3);
            player.scale = .65 + (.12 - .65) * t;
            player.body.pos = {width / 2, 840};
            player.body.size = image_size(catalog, player.body.image, player.scale);
            if (t >= 1) { player.intro_active = false; player.invincible = 1.2; }
        }
        return;
    }
    player.invincible = std::max(0.0, player.invincible - dt);
    player.shield_timer = std::max(0.0, player.shield_timer - dt);
    player.rail_timer = std::max(0.0, player.rail_timer - dt);
    if (player.power_timer > 0) {
        player.power_timer = std::max(0.0, player.power_timer - dt);
        if (player.power_timer == 0) reset_powers();
    }
    const double speed = input.focus ? 180 : player.fast ? 700 : 500;
    player.body.pos += input.move.unit({0, 0}) * (speed * dt);
    player.body.pos.x = std::clamp(player.body.pos.x, 32.0, width - 32);
    player.body.pos.y = std::clamp(player.body.pos.y, 32.0, height - 32);
    player.fire_timer -= dt;
    const Vec muzzle = player.body.pos + Vec{0, -player.body.size.y / 2};
    if (input.rail && player.rail_timer > 0 && player.fire_timer <= 0) {
        player_bullet(muzzle, {0, -2000}, Weapon::Rail);
        sounds.push_back({"lasercont.wav", .3});
        player.fire_timer = .001;
    }
    if (input.fire && player.fire_timer <= 0) {
        if (player.spread) {
            player_bullet(muzzle, {0, -850}, Weapon::Main);
            player_bullet(muzzle + Vec{-10, 8}, {-180, -760}, Weapon::Main);
            player_bullet(muzzle + Vec{10, 8}, {180, -760}, Weapon::Main);
            player.fire_timer = .08;
        } else {
            player_bullet(muzzle, {0, -800}, Weapon::Main);
            player.fire_timer = player.rapid ? .001 : .10;
        }
        sounds.push_back({player.spread ? "lasersound.wav" : "lasersound2.wav", .4});
    }
    if (input.vulcan && !player.overheated) {
        player.heat = std::min(3.0, player.heat + .65 * dt);
        if (player.heat >= 3) player.overheated = true;
    } else {
        player.heat = std::max(0.0, player.heat - .35 * dt);
        if (player.overheated && player.heat <= .25) player.overheated = false;
    }
    player.vulcan_timer -= dt;
    player.sound_timer -= dt;
    if (input.vulcan && !player.overheated && player.vulcan_timer <= 0) {
        player.vulcan_timer = .05;
        player.vulcan_side *= -1;
        const Vec gun = player.body.pos + Vec{9.0 * player.vulcan_side, -36};
        const Vec direction = (input.aim - gun).unit().rotated(random(-3.5, 3.5));
        player_bullet(gun, direction * 1450, ++player.rounds % 5 == 0 ? Weapon::Tracer : Weapon::Vulcan);
        emit(gun, {}, {255, 240, 160, 255}, .055, 18);
        for (int i = 0; i < 4; ++i)
            emit(gun, direction.rotated(random(-35, 35)) * random(90, 260),
                 {255, 190, 40, 255}, random(.05, .15), random(2, 4), .88);
        if (random(0, 1) < .75)
            emit(gun, {-player.vulcan_side * random(80, 180), random(40, 120)},
                 {210, 160, 70, 255}, random(.25, .45), 4, 1, 420);
        if (player.sound_timer <= 0) {
            sounds.push_back({"m61continued.ogg", .11});
            player.sound_timer = 1;
        }
    }
    player.thruster_timer -= dt;
    if (player.thruster_timer <= 0) {
        player.thruster_timer = .008;
        for (double offset : {-34.0, -14.0, 14.0, 34.0}) {
            const Vec engine = player.body.pos + Vec{offset, 45};
            for (int i = 0; i < 8; ++i) {
                emit(engine, Vec{0, random(480, 720)}.rotated(random(-6, 6)),
                     {0, 0, 255, 255}, random(.12, .36), random(1, 4));
                emit(engine, Vec{0, random(180, 380)}.rotated(random(-6, 6)),
                     {100, 180, 255, 255}, random(.18, .38), random(2, 6));
            }
            if (random(0, 1) < .45)
                emit(engine, Vec{0, random(320, 700)}.rotated(random(-15, 15)),
                     {255, 140, 140, 255}, random(.12, .42), random(2, 6));
        }
    }
}
void Model::spawn_enemy() {
    if (boss_present()) return;
    for (int attempt = 0; attempt < 20; ++attempt) {
        Vec pos{random(50, width - 50), -60};
        bool overlaps = false;
        for (const auto& e : enemies)
            if (!e.dead && e.body.bounds().overlaps({pos.x - 42, pos.y - 42, 84, 84})) overlaps = true;
        if (overlaps) continue;
        const auto& spec = enemy_specs[static_cast<std::size_t>(random_int(0, 10))];
        Enemy enemy;
        enemy.name = spec.name;
        // The Python code randomizes the image independently of the weapon/name.
        const auto& visual = enemy_specs[static_cast<std::size_t>(random_int(0, 10))];
        const std::string image = std::string("ships/") + visual.image + ".png";
        enemy.body = {image, pos, image_size(catalog, image, .35), 180};
        enemy.weapon = spec.weapon; enemy.shot = spec.timer; enemy.delay = spec.delay;
        enemies.push_back(enemy);
        if (stage < 5 && random(0, 1) < .15) spawn_rock();
        return;
    }
}
void Model::spawn_rock() {
    Enemy rock;
    rock.rock = true; rock.name = "a Rock"; rock.hp = rock.max_hp = 3;
    const std::string image = "rocks/rock_" + std::to_string(random_int(1, 6)) + ".png";
    rock.body = {image, {random(-40, width + 40), -100},
                 image_size(catalog, image, random(.35, 1.05)), random(0, 360)};
    rock.velocity = {random(-30, 30), random(80, 130)};
    rock.spin = random(-75, 75);
    enemies.push_back(rock);
}
void Model::spawn_boss() {
    if (boss_present() || stage < 1 || stage > 5) return;
    const auto i = static_cast<std::size_t>(stage - 1);
    Enemy boss;
    boss.boss = boss.entering = true;
    boss.rank = std::clamp(stage, 1, 4);
    boss.name = boss_names[i];
    boss.hp = boss.max_hp = boss_hp[i];
    boss.body = {std::string("ships/bosses/") + boss_images[i] + ".png",
                 {width / 2, boss_y[i]}, {800, 800}, stage == 1 ? 180.0 : 0.0};
    enemies.push_back(boss);
}
void Model::boss_pattern(Enemy& e) {
    const int rank = e.rank;
    auto fire = [&](Vec pos, Vec velocity) { enemy_bullet(pos, velocity, Weapon::Orb, e.name); };
    auto aimed = [&](int count, double speed, double spread) {
        const Vec direction = (player.body.pos - e.body.pos).unit({0, 1});
        for (int i = 0; i < count; ++i)
            fire(e.body.pos, direction.rotated(-spread / 2 + spread * i / std::max(1, count - 1)) * speed);
    };
    auto radial = [&](int count, double speed, double offset) {
        for (int i = 0; i < count; ++i)
            fire(e.body.pos, Vec{speed, 0}.rotated(offset + 360.0 * i / count));
    };
    auto spiral = [&](int arms, double speed, double spin) {
        radial(arms, speed, e.phase_time * spin);
    };
    auto wall = [&](int columns, double speed, int gap, int gap_width) {
        for (int i = 0; i < columns; ++i)
            if (std::abs(i - gap) > gap_width)
                fire({width / (columns + 1) * (i + 1), e.body.pos.y + 120}, {random(-18, 18), speed});
    };
    auto next = [&] { e.pattern = std::min(4, e.pattern + 1);
                     e.phase_time = 0; e.shot = .4; e.secondary = 1; };
    switch (e.pattern) {
    case 0:
        if (e.phase_time > 2.5) next();
        break;
    case 1:
        if (e.shot <= 0) {
            e.shot = std::max(.48, .95 - rank * .08);
            radial(14 + rank * 5, 145 + rank * 35, e.phase_time * (28 + rank * 8));
        }
        if (e.secondary <= 0) {
            e.secondary = 1.35; aimed(3 + rank * 2, 170 + rank * 32, 28 + rank * 8);
        }
        if (e.phase_time > 9) next();
        break;
    case 2:
        if (e.shot <= 0) {
            e.shot = std::max(.18, .42 - rank * .045);
            spiral(2 + rank, 145 + rank * 28, 90 + rank * 24);
        }
        if (e.secondary <= 0) {
            e.secondary = 1.1; aimed(5 + rank, 170 + rank * 25, 24 + rank * 7);
        }
        if (e.phase_time > 10) next();
        break;
    case 3:
        if (e.shot <= 0) {
            e.shot = std::max(.5, 1.0 - rank * .08);
            const int columns = 12 + rank * 4;
            const int gap = static_cast<int>(std::round(
                (std::cos(e.phase_time * 70 * pi / 180) + 1) / 2 * (columns - 1)));
            wall(columns, 135 + rank * 30, gap, rank < 4 ? 2 : 1);
        }
        if (e.secondary <= 0) {
            e.secondary = std::max(.75, 1.25 - rank * .08);
            aimed(5 + rank * 2, 185 + rank * 28, 34 + rank * 8);
            if (rank >= 3)
                for (int i = 0; i < 4 + rank; ++i) {
                    fire({-16, 160.0 + i * 90}, {145.0 + rank * 22, 90.0 + i * 8});
                    fire({width + 16, 205.0 + i * 90}, {-145.0 - rank * 22, 90.0 + i * 8});
                }
        }
        if (e.phase_time > 11) next();
        break;
    default:
        if (e.shot <= 0) {
            e.shot = std::max(.28, .68 - rank * .08);
            radial(16 + rank * 6, 170 + rank * 38, e.phase_time * (65 + rank * 18));
            spiral(3 + rank, 145 + rank * 34, 150 + rank * 22);
        }
        if (e.secondary <= 0) {
            e.secondary = std::max(.65, 1.1 - rank * .08);
            aimed(7 + rank * 2, 210 + rank * 32, 48 + rank * 10);
            if (rank >= 4) wall(24, 250, static_cast<int>(e.phase_time * 3) % 24, 1);
        }
    }
}
void Model::update_enemies(double dt) {
    for (auto& e : enemies) {
        if (e.dead) continue;
        e.flash = std::max(0.0, e.flash - dt);
        e.shot -= dt; e.secondary -= dt; e.thruster -= dt; e.phase_time += dt;
        if (e.boss) {
            e.body.pos.y = std::min(250.0, e.body.pos.y + 120 * dt);
            e.entering = e.body.pos.y < 250;
            boss_pattern(e);
        } else {
            e.body.pos += e.velocity * dt;
            if (e.rock) e.body.angle += e.spin * dt;
            else {
                const Vec direction = (player.body.pos - e.body.pos).unit({0, 1});
                e.body.angle = std::atan2(direction.y, direction.x) * 180 / pi + 90;
                if (e.shot <= 0) {
                    enemy_bullet(e.body.pos, direction * (e.weapon == Weapon::Blue ? 520 : 240),
                                 e.weapon, e.name);
                    e.shot = e.delay;
                }
            }
            if (e.body.bounds().y > height + 80) e.dead = true;
        }
        if (!e.rock && e.thruster <= 0) {
            e.thruster = .04;
            const Vec rear = e.boss ? Vec{0, -1} : (e.body.pos - player.body.pos).unit();
            emit(e.body.pos + rear * (std::max(e.body.size.x, e.body.size.y) * .32),
                 rear.rotated(random(-25, 25)) * random(80, 180),
                 {255, 120, 40, 255}, random(.15, .35), random(2, 5));
        }
    }
}
void Model::clear_combat() {
    for (auto& enemy : enemies) enemy.dead = true;
    for (auto& bullet : bullets) bullet.dead = true;
    for (auto& pickup : pickups) pickup.dead = true;
}
void Model::damage_enemy(std::size_t index, int damage) {
    auto& e = enemies.at(index);
    if (e.dead || (e.boss && e.entering)) return;
    e.hp -= damage; e.flash = e.rock ? .05 : .005;
    if (!e.boss && !e.rock) {
        sounds.push_back({"clink.wav", .3});
        burst(e.body.pos, 50, {255, 220, 80, 255});
    }
    if (e.hp > 0) return;
    e.dead = true;
    explosions.push_back({e.body.pos, 0, e.boss});
    burst(e.body.pos, e.boss ? 250 : e.rock ? 1000 : 500);
    sounds.push_back({"explosion" + std::to_string(random_int(2, 3)) + ".wav", .6});
    score += e.boss ? 5000 : e.rock ? 50 : 100;
    if (e.boss) {
        stage_time = 0;
        if (stage == 5) { end_game(true); clear_combat(); }
        else if (stage == 4) start_transition();
        else { ++stage; banner = 2.4; }
    } else if (random(0, 1) < .15) {
        const auto kind = static_cast<Power>(random_int(0, 6));
        pickups.push_back({{"powerups/powerup-" + power_names[static_cast<std::size_t>(kind)] + ".png",
                            {random(24, width - 24), 0}, {46, 46}, 0}, kind});
    }
}
void Model::collide() {
    if (game_over || player.intro_active || transitioning()) return;
    for (std::size_t i = 0; i < enemies.size(); ++i) {
        if (enemies[i].dead) continue;
        for (auto& bullet : bullets) {
            if (bullet.dead || !bullet.friendly) continue;
            if (mask_collision(enemies[i].body, bullet.body, catalog)) {
                if (!bullet.piercing) bullet.dead = true;
                damage_enemy(i, 1);
                break;
            }
        }
        if (game_over || transitioning()) return;
    }
    if (player.invincible <= 0) {
        const double radius = std::max(1.0, (player.body.size.x - 96) / 2);
        for (auto& bullet : bullets) {
            if (bullet.dead || bullet.friendly) continue;
            if ((bullet.body.pos - player.body.pos).length() < radius + bullet.radius) {
                bullet.dead = true; hit_player(bullet.owner); break;
            }
        }
    }
    if (player.invincible <= 0 && player.alive)
        for (const auto& enemy : enemies)
            if (!enemy.dead && (enemy.boss ? visible_bounds(enemy.body, catalog).inset(9)
                                 : enemy.body.bounds().inset(enemy.rock ? 20 : 28))
                                  .overlaps(player.body.bounds())) {
                hit_player(enemy.name); break;
            }
    if (player.alive)
        for (auto& pickup : pickups)
            if (!pickup.dead && player.body.bounds().overlaps(pickup.body.bounds())) {
                apply_power(pickup.kind); pickup.dead = true;
            }
}
void Model::update_effects(double dt) {
    for (auto& p : particles) {
        p.life -= dt;
        p.velocity.y += p.gravity * dt;
        p.pos += p.velocity * dt;
        p.velocity = p.velocity * std::pow(p.drag, dt * 60);
    }
    erase_if(particles, [](const Particle& p) { return p.life <= 0; });
    for (auto& e : explosions) e.age += dt;
    erase_if(explosions, [](const Explosion& e) { return e.age >= 31 * .045; });
}
void Model::start_transition() {
    phase = Phase::BossExplosion; phase_time = fade = 0; banner = 0;
    transition_start = player.body.pos;
    clear_combat();
}
void Model::update_transition(double dt) {
    phase_time += dt;
    auto advance = [&](Phase next) { phase = next; phase_time = 0; };
    switch (phase) {
    case Phase::BossExplosion:
        if (phase_time >= 2) {
            earth = {width / 2, -image_size(catalog, "rocks/earth.png", .55).y / 2};
            banner = 1.4; advance(Phase::EarthEnter);
        }
        break;
    case Phase::EarthEnter:
        earth.y = std::min(height / 2, earth.y + 120 * dt);
        if (earth.y >= height / 2) { banner = 0; advance(Phase::ShipGrow); }
        break;
    case Phase::ShipGrow: {
        const double t = std::min(1.0, phase_time / .8);
        player.scale = .12 + (.22 - .12) * t;
        if (t >= 1) advance(Phase::ShipToEarth);
        break;
    }
    case Phase::ShipToEarth: {
        const double raw = std::min(1.0, phase_time / 2);
        const double t = raw * raw * (3 - 2 * raw);
        const Vec control{width * .28, height * .42};
        player.body.pos = lerp(lerp(transition_start, control, t), lerp(control, earth, t), t);
        const Vec tangent = (control - transition_start) * (2 * (1 - t)) + (earth - control) * (2 * t);
        player.body.angle = std::atan2(tangent.y, tangent.x) * 180 / pi + 90;
        player.scale = .22 + (.02 - .22) * t;
        if (raw >= 1) advance(Phase::FadeOut);
        break;
    }
    case Phase::FadeOut:
        fade = std::min(1.0, phase_time);
        if (fade >= 1) {
            stage = 5; stage_time = 0;
            player.body.pos = {width / 2, height - 120};
            player.body.angle = 0; player.scale = .12;
            update_ocean(0); advance(Phase::TerrainFadeIn);
        }
        break;
    case Phase::TerrainFadeIn:
        update_ocean(dt);
        fade = std::max(0.0, 1 - phase_time);
        if (phase_time >= 2) {
            banner = 2.4; stage_time = 0; enemy_timer_ = 0;
            advance(Phase::Terrain);
        }
        break;
    default: break;
    }
    player.body.size = image_size(catalog, player.body.image, player.scale);
}
void Model::update_ocean(double dt) {
    for (auto& chunk : ocean) chunk.y += 160 * dt;
    erase_if(ocean, [](const OceanChunk& c) { return c.y >= height; });
    double top = ocean.empty() ? height : std::min_element(ocean.begin(), ocean.end(),
        [](const OceanChunk& a, const OceanChunk& b) { return a.y < b.y; })->y;
    while (top > -height) {
        const auto key = "backgrounds/ocean/stage5_ocean_chunk_" + std::to_string(ocean_index_) + ".png";
        const Vec size = image_size(catalog, key);
        const double h = size.y * width * 1.15 / size.x;
        top -= h - 96;
        ocean.push_back({ocean_index_, top, h});
        ocean_index_ = ocean_index_ % 3 + 1;
    }
}
void Model::update(double dt, const Input& input) {
    if (paused || dt <= 0) return;
    elapsed += dt;
    if (!player.intro_active) banner = std::max(0.0, banner - dt);
    update_effects(dt);
    for (auto& star : stars) {
        star.pos.y += star.speed * dt;
        if (star.pos.y > height) star.pos = {random(0, width), random(-40, -5)};
    }
    if (game_over) { ending_time += dt; return; }
    if (transitioning()) { update_transition(dt); return; }
    if (phase == Phase::Terrain) update_ocean(dt);
    update_player(dt, input);
    if (player.intro_active) return;
    if (!boss_present()) {
        stage_time += dt; enemy_timer_ += dt; rock_timer_ += dt;
        const auto enemies_count = std::count_if(enemies.begin(), enemies.end(),
            [](const Enemy& e) { return !e.dead && !e.rock; });
        if (enemy_timer_ >= enemy_delay_ && enemies_count < 6 + (stage - 1) * 2) {
            enemy_timer_ = 0;
            enemy_delay_ = phase == Phase::Terrain ? random(.35, 1.7) : random(.4, 3);
            spawn_enemy();
        }
        const auto rocks_count = std::count_if(enemies.begin(), enemies.end(),
            [](const Enemy& e) { return !e.dead && e.rock; });
        if (stage < 5 && rock_timer_ >= rock_delay_ && rocks_count < 6 + (stage - 1) * 2) {
            rock_timer_ = 0; rock_delay_ = random(.4, 3.2); spawn_rock();
        }
        if (stage_time >= 30) spawn_boss();
    }
    update_enemies(dt);
    for (auto& bullet : bullets) {
        bullet.body.pos += bullet.velocity * dt;
        const Rect r = bullet.body.bounds();
        if (r.y > height + 80 || r.y + r.h < -80 || r.x > width + 80 || r.x + r.w < -80)
            bullet.dead = true;
        if (!bullet.dead && bullet.kind == Weapon::Pellet) {
            bullet.trail_timer -= dt;
            if (bullet.trail_timer <= 0) {
                bullet.trail_timer = .04;
                for (int i = 0; i < 8; ++i)
                    emit(bullet.body.pos, Vec{0, random(80, 180)}.rotated(random(-25, 25)),
                         {180, 255, 0, 255}, random(.15, .35), random(2, 5));
            }
        }
    }
    for (auto& pickup : pickups) {
        pickup.life -= dt; pickup.glitter -= dt; pickup.body.pos.y += 120 * dt;
        if (pickup.life <= 0 || pickup.body.pos.y > height + 24) pickup.dead = true;
        if (!pickup.dead && pickup.glitter <= 0) {
            pickup.glitter = .025;
            for (int i = 0; i < 8; ++i)
                emit(pickup.body.pos + Vec{random(-32, 32), random(-32, 32)}, {0, -20},
                     {255, static_cast<std::uint8_t>(random_int(120, 255)),
                           static_cast<std::uint8_t>(random_int(120, 255)), 255},
                     random(.25, .55), random(2, 4), 1);
        }
    }
    collide();
    erase_if(enemies, [](const Enemy& e) { return e.dead; });
    erase_if(bullets, [](const Bullet& b) { return b.dead; });
    erase_if(pickups, [](const Pickup& p) { return p.dead; });
}
} // namespace dv
