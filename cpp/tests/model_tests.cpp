#include "model.hpp"
#include "scores.hpp"
#include <chrono>
#include <fstream>
#include <functional>
#include <iostream>
#include <stdexcept>

namespace {
void require(bool condition, const std::string& message) {
    if (!condition) throw std::runtime_error(message);
}
void near(double actual, double expected, const std::string& message) {
    require(std::abs(actual - expected) < .0001, message);
}
dv::Catalog make_catalog() {
    dv::Catalog catalog;
    auto add = [&](const std::string& name, int w, int h) {
        catalog.emplace(name, dv::Mask{w, h, std::vector<std::uint8_t>(
            static_cast<std::size_t>(w) * h, 255)});
    };
    add("ships/finnfighter.png", 1194, 1205);
    add("laser.png", 10, 20); add("laser-red.png", 30, 120);
    add("rocks/earth.png", 543, 543);
    for (const std::string name : {"purplealus", "redhawk", "redalus", "robotector", "bluehawk",
          "turqoiseship", "lilac-thrusters", "grayship", "blackhawk", "orangeship", "vihree-alus"})
        add("ships/" + name + ".png", 400, 400);
    for (const std::string name : {"dark-crusader", "boss-2", "foobarhead1",
          "stage4_boss_void_dreadnought_full", "stage5_terrain_automaton"})
        add("ships/bosses/" + name + ".png", 128, 128);
    for (int i = 1; i <= 6; ++i) add("rocks/rock_" + std::to_string(i) + ".png", 100, 100);
    for (int i = 1; i <= 3; ++i)
        add("backgrounds/ocean/stage5_ocean_chunk_" + std::to_string(i) + ".png", 192, 108);
    return catalog;
}
void advance(dv::Model& g, double seconds, const dv::Input& input = {}) {
    const int frames = static_cast<int>(std::ceil(seconds * 60));
    for (int i = 0; i < frames; ++i) {
        g.update(1.0 / 60, input);
        g.sounds.clear();
    }
}
void test_movement(const dv::Catalog& catalog) {
    dv::Model g(catalog, 1);
    g.reset(1, true);
    const auto start = g.player.body.pos;
    dv::Input input; input.move = {1, 1};
    g.update(.1, input);
    near((g.player.body.pos - start).length(), 50, "Diagonal movement must be normalized");
    auto previous = g.player.body.pos;
    input.focus = true;
    g.update(.1, input);
    near((g.player.body.pos - previous).length(), 18, "Focus speed");
    g.apply_power(dv::Power::Speed);
    previous = g.player.body.pos;
    input.focus = false;
    g.update(.1, input);
    near((g.player.body.pos - previous).length(), 70, "Speed pickup must affect actual movement");
    g.player.body.pos = {dv::width - 33, dv::height - 33};
    g.update(.1, input);
    near(g.player.body.pos.x, dv::width - 32, "Horizontal boundary");
    near(g.player.body.pos.y, dv::height - 32, "Vertical boundary");
    g.paused = true;
    const auto elapsed = g.elapsed;
    g.update(1, input);
    near(g.elapsed, elapsed, "Pause freezes simulation");
    g.reset();
    advance(g, 4.6);
    require(!g.player.intro_active, "Ship intro must complete");
    near(g.player.scale, .12, "Intro final scale");
    near(g.player.body.pos.y, 840, "Intro target");
}
void test_weapons(const dv::Catalog& catalog) {
    dv::Model g(catalog, 2);
    g.reset(1, true);
    dv::Input input; input.fire = true;
    g.update(1.0 / 60, input);
    require(g.bullets.size() == 1, "Main gun creates one shot");
    near(g.bullets[0].velocity.y, -800, "Main bullet velocity");
    g.update(1.0 / 60, input);
    require(g.bullets.size() == 1, "Main gun respects cooldown");
    g.reset(1, true); g.apply_power(dv::Power::Spread);
    g.update(1.0 / 60, input);
    require(g.bullets.size() == 3, "Spread creates three shots");
    near(g.bullets[1].velocity.x, -180, "Spread left velocity");
    g.reset(1, true); g.apply_power(dv::Power::Cannon);
    input.fire = false; input.rail = true;
    g.update(1.0 / 60, input);
    require(g.bullets.size() == 1 && g.bullets[0].kind == dv::Weapon::Rail, "Railgun pickup");
    near(g.bullets[0].velocity.y, -2000, "Railgun velocity");
    g.reset(1, true); input.rail = false; input.vulcan = true;
    input.aim = g.player.body.pos + dv::Vec{500, 0};
    g.update(1.0 / 60, input);
    require(g.bullets.size() == 1 && g.bullets[0].velocity.x > 1300, "Vulcan aims at cursor");
    g.player.invincible = 1000;
    advance(g, 4.7, input);
    require(g.player.overheated, "Sustained fire overheats Vulcan");
    input.vulcan = false;
    advance(g, 8.5, input);
    require(!g.player.overheated && g.player.heat <= .25, "Vulcan recovers after cooling");
}
void test_power_and_hits(const dv::Catalog& catalog) {
    dv::Model g(catalog, 3);
    g.reset(1, true);
    g.apply_power(dv::Power::Health);
    require(g.player.lives == 6, "Health adds three lives");
    g.apply_power(dv::Power::Shield);
    require(g.player.shields == 3 && g.activate_shield(), "Shield pickup and activation");
    require(!g.activate_shield() && g.player.shields == 2, "Active shield cannot consume another charge");
    g.hit_player("test");
    require(g.player.lives == 6, "Shield blocks damage");
    g.update(5.1, {});
    g.hit_player("test");
    require(g.player.lives == 5 && g.player.killer == "test", "Shield expiry and killer attribution");
    g.hit_player("other");
    require(g.player.lives == 5, "Invincibility prevents double hit");
    g.apply_power(dv::Power::Piercing);
    require(g.player.piercing, "Piercing enabled");
    g.player.invincible = 1000;
    g.update(25.1, {});
    require(!g.player.piercing && g.player.power_timer == 0, "Power expiration");
    for (auto power : {dv::Power::Speed, dv::Power::Spread, dv::Power::Laser, dv::Power::Cannon}) {
        g.apply_power(power);
        g.update(12.1, {});
        require(!g.player.fast && !g.player.spread && !g.player.rapid && g.player.rail_timer == 0,
                "Temporary powers reset");
    }
    g.player.lives = 1; g.player.invincible = 0;
    g.hit_player("Terrain Automaton");
    require(g.game_over && !g.victory && !g.player.alive, "Death ends game");
    advance(g, 5.1);
    require(g.ending_time >= 5, "Death advances to high score timing in every phase");
}
void test_collisions(const dv::Catalog& catalog) {
    dv::Model g(catalog, 4);
    g.reset(1, true);
    dv::Enemy enemy;
    enemy.body = {"", {500, 500}, {100, 100}, 0};
    enemy.hp = 1;
    g.enemies.push_back(enemy);
    dv::Bullet bullet;
    bullet.body = {"laser.png", {500, 500}, {10, 20}, 0}; bullet.friendly = true;
    g.bullets.push_back(bullet);
    g.collide();
    require(g.enemies[0].dead && g.score == 100 && g.bullets[0].dead, "Hit destroys enemy and scores");
    g.reset(1, true);
    enemy.hp = 2; g.enemies.push_back(enemy); bullet.piercing = true;
    g.bullets.push_back(bullet);
    g.collide();
    require(g.enemies[0].hp == 1 && !g.bullets[0].dead, "Piercing bullet survives hit");
    dv::Catalog masks;
    masks.emplace("hollow", dv::Mask{4, 4, std::vector<std::uint8_t>(16, 0), {0, 0, 1, 1}});
    masks.at("hollow").alpha[0] = 255;
    dv::Body body{"hollow", {2, 2}, {4, 4}, 0};
    require(!dv::mask_collision(body, {"", {2.5, 2.5}, {1, 1}, 0}, masks),
            "Transparent pixels must not collide");
    require(dv::mask_collision(body, {"", {.5, .5}, {1, 1}, 0}, masks),
            "Opaque pixels must collide");
    body.angle = 180;
    require(dv::mask_collision(body, {"", {3.5, 3.5}, {1, 1}, 0}, masks),
            "Collision mask follows rotation");
    const auto visible = dv::visible_bounds(body, masks);
    near(visible.x, 3, "Visible bounds exclude transparent border after rotation");
    near(visible.y, 3, "Visible bounds rotate around sprite center");
    g.reset(5, true);
    bullet = {};
    bullet.body = {"", g.player.body.pos, {46, 46}, 0};
    bullet.owner = "The Wasp";
    g.bullets.push_back(bullet);
    g.player.lives = 1;
    g.collide();
    require(g.game_over && g.player.killer == "The Wasp", "Enemy bullet death records owner in terrain");
}
void test_bosses(const dv::Catalog& catalog) {
    dv::Model g(catalog, 5);
    for (int stage = 1; stage <= 5; ++stage) {
        g.reset(stage, true);
        g.player.invincible = 10000;
        g.spawn_boss();
        const int hp = g.enemies[0].hp;
        g.damage_enemy(0, 1);
        require(g.enemies[0].hp == hp, "Entering bosses are invulnerable");
        advance(g, 5.6);
        require(!g.enemies[0].entering && !g.bullets.empty(), "Boss arrives and fires radial pattern");
        require(g.enemies[0].rank == std::min(stage, 4), "Boss rank scaling");
        advance(g, 7);
        require(g.enemies[0].pattern == 2, "Boss spiral phase");
        advance(g, 10);
        require(g.enemies[0].pattern == 3, "Boss maze phase");
        advance(g, 12);
        require(g.enemies[0].pattern == 4, "Boss desperation phase");
        g.damage_enemy(0, 10000);
        require(g.score == 5000, "Boss reward");
        if (stage < 4) require(g.stage == stage + 1, "Next space stage");
        if (stage == 4) {
            require(g.phase == dv::Phase::BossExplosion, "Fourth boss starts Earth transition");
            advance(g, 15);
            require(g.stage == 5 && g.phase == dv::Phase::Terrain, "Earth sequence reaches terrain");
            require(!g.ocean.empty() && g.player.body.angle == 0, "Terrain map and ship restored");
            near(g.player.scale, .12, "Ship scale restored after transition");
            advance(g, 30);
            require(g.boss_present(), "Terrain boss spawns after transition");
        }
        if (stage == 5) {
            require(g.victory && g.game_over && g.stage == 5, "Final boss gives victory in stage five");
            advance(g, 5.1);
            require(g.ending_time >= 5, "Victory must reach high score timing");
        }
    }
}
void test_scores() {
    const auto path = std::filesystem::temp_directory_path() /
        ("darkvoid-score-test-" + std::to_string(std::chrono::steady_clock::now().time_since_epoch().count()));
    std::filesystem::create_directory(path);
    const auto file = path / "scores.json";
    dv::Scores scores(file);
    require(scores.qualifies(0), "Empty table accepts score");
    for (int i = 0; i < 12; ++i) scores.add({"pilot", i * 100, 5, "No-one"});
    dv::Scores loaded(file);
    require(loaded.entries().size() == 10 && loaded.entries()[0].score == 1100,
            "Scores persist sorted and limited to ten");
    require(!loaded.qualifies(200) && loaded.qualifies(201), "High score qualification boundary");
    {
        std::ofstream malformed(file);
        malformed << "{ invalid";
    }
    dv::Scores corrupt(file);
    require(corrupt.entries().empty(), "Malformed JSON handled");
    std::filesystem::remove_all(path);
}
}
int main() {
    try {
        const auto catalog = make_catalog();
        const std::vector<std::pair<std::string, std::function<void()>>> tests{
            {"movement and introduction", [&] { test_movement(catalog); }},
            {"weapons and heat", [&] { test_weapons(catalog); }},
            {"powerups, shield, damage and death", [&] { test_power_and_hits(catalog); }},
            {"collision masks and scoring", [&] { test_collisions(catalog); }},
            {"all five bosses, transitions and victory", [&] { test_bosses(catalog); }},
            {"persistent high scores", test_scores}
        };
        for (const auto& test : tests) { test.second(); std::cout << "PASS: " << test.first << '\n'; }
    } catch (const std::exception& error) {
        std::cerr << "FAIL: " << error.what() << '\n'; return 1;
    }
    return 0;
}
