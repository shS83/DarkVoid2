#include "view.hpp"
#include <fstream>
#include <iostream>
#include <stdexcept>

namespace {
void require(bool condition, const std::string& message) {
    if (!condition) throw std::runtime_error(message);
}
SDL_Event key(SDL_Keycode code, SDL_Scancode scan = SDL_SCANCODE_UNKNOWN, bool repeat = false) {
    SDL_Event event{};
    event.type = SDL_KEYDOWN;
    event.key.keysym.sym = code;
    event.key.keysym.scancode = scan;
    event.key.repeat = repeat;
    return event;
}
void type(dv::Session& session, const std::string& text) {
    for (const unsigned char c : text) session.handle_event(key(c));
}
void text(dv::Session& session, const std::string& input) {
    SDL_Event event{};
    event.type = SDL_TEXTINPUT;
    SDL_strlcpy(event.text.text, input.c_str(), sizeof(event.text.text));
    session.handle_event(event);
}
void command(dv::Session& session, const std::string& input) {
    text(session, input);
    session.handle_event(key(SDLK_RETURN));
}
void advance(dv::Session& session, double seconds, const dv::Input& input = {}) {
    for (int i = 0; i < static_cast<int>(std::ceil(seconds * 60)); ++i) {
        session.update(1.0 / 60, input);
        session.game.sounds.clear();
    }
}
std::filesystem::path empty_scores(const std::filesystem::path& path) {
    std::ofstream file(path);
    file << "[]";
    return path;
}
struct Fixture {
    dv::Model game;
    dv::Scores scores;
    dv::Session session;
    Fixture(const dv::Catalog& catalog, const std::filesystem::path& file)
        : game(catalog, 83), scores(empty_scores(file)), session(game, scores, true) {
        game.reset(1, true);
    }
};
void test_console(Fixture& f) {
    auto& s = f.session;
    auto& g = f.game;
    for (auto event : {key(0x00a7), key(SDLK_BACKQUOTE), key(0, SDL_SCANCODE_GRAVE)}) {
        s.handle_event(event);
        require(s.console.open && SDL_IsTextInputActive(), "Console toggle starts text input");
        const double elapsed = g.elapsed;
        dv::Input held; held.fire = held.rail = held.vulcan = true; held.move = {1, 1};
        advance(s, .3, held);
        require(s.audio_paused() && g.elapsed == elapsed, "Console freezes gameplay and pauses audio");
        s.handle_event(key(SDLK_LALT));
        require(g.player.shield_timer == 0, "Console consumes gameplay keys");
        s.handle_event(key(SDLK_ESCAPE));
        s.update(.1, held);
        require(s.running && s.console.active() && g.elapsed == elapsed,
                "Escape closes console; simulation stays frozen during slide");
        s.update(.15);
        require(!s.console.active() && !s.audio_paused() && g.elapsed > elapsed,
                "Simulation and audio resume after slide");
    }
    s.handle_event(key(SDLK_PAUSE));
    s.handle_event(key(SDLK_BACKQUOTE));
    advance(s, .3);
    s.handle_event(key(SDLK_ESCAPE));
    advance(s, .3);
    require(g.paused && s.audio_paused(), "Manual pause survives console");
    s.handle_event(key(SDLK_PAUSE));
    s.handle_event(key(SDLK_BACKQUOTE));
    text(s, "§`");
    require(s.console.input.empty(), "Opening characters do not enter command");
    command(s, "GoD");
    require(g.player.godmode, "Case-insensitive console command");
    text(s, "warp 5");
    s.handle_event(key(SDLK_UP));
    require(s.console.input == "GoD", "History up");
    s.handle_event(key(SDLK_DOWN));
    require(s.console.input == "warp 5", "History down restores draft");
    s.handle_event(key(SDLK_RETURN));
    require(g.stage == 5 && g.phase == dv::Phase::Terrain && g.player.godmode,
            "Warp preserves inventory and changes world");
    command(s, "warp 99");
    require(g.stage == 5 && s.console.output.back().rfind("Error:", 0) == 0,
            "Invalid command leaves game intact");
    command(s, "powerup shield");
    require(g.player.shields == 6, "Terrain shield grant");
    for (const auto& power : dv::power_names) command(s, "powerup " + power);
    require(g.player.shields == 12 && g.player.lives == 6, "All powerup command types");
    s.console.update(.6);
    text(s, "x");
    require(s.console.cursor_timer == 0, "Typing resets cursor blink");
    s.handle_event(key(SDLK_BACKSPACE));
    for (int i = 0; i < 10; ++i) text(s, "abcdefghijklmnopqrst");
    require(s.console.input.size() == 128, "Console input is bounded");
    s.console.input.clear();
    command(s, "clear");
    require(s.console.output.empty() && !s.console.history.empty(), "Clear preserves command history");
    for (int i = 0; i < 250; ++i) s.console.write(std::to_string(i));
    require(s.console.output.size() == 200, "Console output is bounded");
    SDL_Event quit{}; quit.type = SDL_QUIT;
    s.handle_event(quit);
    require(!s.running && f.scores.entries().empty(), "Quit works in console without saving a score");
}
void test_commands(Fixture& f) {
    auto& g = f.game;
    for (const auto* input : {"warp", "warp -1", "warp 6", "warp 5abc", "warp 9999999999999",
                              "god on", "impulse 8", "powerup", "powerup unknown", "powerup shield extra"}) {
        bool rejected = false;
        try { g.execute_console_command(input); }
        catch (const std::invalid_argument&) { rejected = true; }
        require(rejected && g.stage == 1 && !g.player.godmode && g.player.shields == 0,
                std::string("Reject malformed command before mutation: ") + input);
    }
    g.player.heat = 3; g.player.overheated = true;
    g.execute_console_command("impulse 9");
    require(g.player.vulcan_unlimited && !g.player.overheated && g.player.heat == 0,
            "Impulse resets overheat immediately");
    require(g.player.spread || g.player.rapid || g.player.rail_timer > 0 || g.player.piercing,
            "Impulse grants a weapon upgrade");
    g.player.godmode = true;
    dv::Input input; input.vulcan = true;
    advance(f.session, 14, input);
    require(g.player.vulcan_unlimited && g.player.heat == 0 && g.player.rounds > 100,
            "Unlimited Vulcan survives timed power expiration");
    g.score = 4321;
    for (int stage = 1; stage <= 5; ++stage) {
        g.spawn_boss();
        g.end_game(false);
        g.player.lives = 0;
        g.warp_to_stage(stage);
        require(g.stage == stage && g.enemies.empty() && g.bullets.empty() && g.explosions.empty(),
                "Warp clears old combat and effects");
        require(g.player.alive && g.player.lives == 3 && !g.game_over && g.score == 4321,
                "Warp restores dead player and retains score");
        require(g.player.vulcan_unlimited && g.player.godmode, "Warp retains developer powers");
        g.spawn_boss();
        require(g.boss_present(), "Warp resets selected stage boss");
    }
}
void test_cheats(Fixture& f) {
    auto& s = f.session;
    auto& g = f.game;
    type(s, "iddqd");
    require(g.player.godmode && s.cheat_notice == "GOD MODE: ON" && s.cheat_notice_time == 3,
            "IDDQD enables god mode and animated notice");
    g.hit_player("test");
    require(g.player.lives == 3, "God mode blocks direct damage");
    dv::Bullet bullet;
    bullet.body = {"", g.player.body.pos, {46, 46}, 0}; bullet.owner = "test";
    g.bullets.push_back(bullet);
    dv::Enemy enemy;
    enemy.body = {"", g.player.body.pos, {100, 100}, 0}; enemy.name = "test";
    g.enemies.push_back(enemy);
    g.collide();
    require(g.player.lives == 3 && g.player.killer == "No-one", "God mode blocks bullets and body damage");
    type(s, "iddqd");
    require(!g.player.godmode && s.cheat_notice == "GOD MODE: OFF", "IDDQD toggles off");
    g.hit_player("test");
    require(g.player.lives == 2, "Damage resumes after god mode is disabled");
    g.warp_to_stage(1);
    g.player.heat = 3; g.player.overheated = true;
    type(s, "idkfa");
    require(s.cheat_notice == "SAY HELLO TO MY LITTLE FRIEND" && g.player.arsenal_unlimited,
            "IDKFA grants permanent arsenal and requested text");
    require(g.player.spread && g.player.vulcan_unlimited && g.player.heat == 0 && !g.player.overheated,
            "IDKFA grants triple shot and cool Vulcan immediately");
    g.player.godmode = true;
    dv::Input input; input.vulcan = true;
    advance(s, 30, input);
    require(g.player.rounds > 400 && g.player.heat == 0 && !g.player.overheated,
            "IDKFA Vulcan keeps firing without heat");
    require(s.cheat_notice_time == 0, "Notice disappears after animation");
    for (const auto power : {dv::Power::Spread, dv::Power::Cannon, dv::Power::Speed, dv::Power::Piercing}) {
        g.apply_power(power);
        advance(s, 26);
        require(g.player.spread && g.player.arsenal_unlimited && g.player.vulcan_unlimited,
                "Timed pickups and expiry cannot remove permanent arsenal");
    }
    g.warp_to_stage(5);
    require(g.player.arsenal_unlimited, "Permanent arsenal survives warp");
    input = {}; input.rail = true;
    s.update(1.0 / 60, input);
    require(g.bullets.size() == 1 && g.bullets[0].kind == dv::Weapon::Rail,
            "CTRL fires railgun after timers expire and warp");
    g.bullets.clear(); g.player.fire_timer = 0;
    input = {}; input.fire = true;
    s.update(1.0 / 60, input);
    require(g.bullets.size() == 3, "Normal gun remains triple shot");
    // Console text and paused input must not activate gameplay cheats.
    g.player.godmode = false;
    s.handle_event(key(SDLK_BACKQUOTE));
    type(s, "iddqd");
    text(s, "iddqd");
    require(!g.player.godmode && s.console.input == "iddqd", "Console input does not trigger cheats");
    advance(s, .3);
    s.handle_event(key(SDLK_ESCAPE)); advance(s, .3);
    s.handle_event(key(SDLK_PAUSE)); type(s, "iddqd");
    require(!g.player.godmode, "Paused input does not trigger cheats");
    s.handle_event(key(SDLK_PAUSE));
    type(s, "id");
    s.handle_event(key(SDLK_d, SDL_SCANCODE_UNKNOWN, true));
    type(s, "qd");
    require(!g.player.godmode, "Key auto-repeat does not complete a cheat");
}
void test_ending(Fixture& f) {
    auto& s = f.session;
    auto& g = f.game;
    g.warp_to_stage(4);
    g.player.godmode = true;
    g.spawn_boss();
    g.enemies[0].entering = false;
    g.damage_enemy(0, 10000);
    g.damage_enemy(0, 10000);
    require(g.phase == dv::Phase::BossExplosion && g.score == 5000 && !g.game_over,
            "Fourth boss dies once and starts Earth transition");
    advance(s, 15);
    require(g.phase == dv::Phase::Terrain && g.stage == 5, "Earth transition reaches terrain");
    advance(s, 30);
    require(g.boss_present(), "Terrain boss spawns naturally");
    // Kill the final boss through the real collision path.
    auto boss = std::find_if(g.enemies.begin(), g.enemies.end(), [](const dv::Enemy& e) { return e.boss; });
    require(boss != g.enemies.end(), "Final boss exists");
    const auto index = static_cast<std::size_t>(boss - g.enemies.begin());
    boss->entering = false; boss->hp = 1;
    dv::Bullet shot;
    shot.friendly = true; shot.body = boss->body; shot.body.image.clear();
    g.bullets.push_back(shot);
    g.collide();
    g.damage_enemy(index, 10000);
    require(g.victory && g.stage == 5 && g.score == 10000 && !g.player.alive,
            "Final boss awards score once and stops player in stage five");
    require(std::all_of(g.enemies.begin(), g.enemies.end(), [](const auto& e) { return e.dead; })
        && std::all_of(g.bullets.begin(), g.bullets.end(), [](const auto& b) { return b.dead; }),
        "Ending clears combat safely");
    dv::Input input; input.fire = input.rail = input.vulcan = true;
    const int rounds = g.player.rounds;
    advance(s, 5.1, input);
    require(s.screen == dv::Screen::Scores && s.entering && SDL_IsTextInputActive(),
            "Terrain victory reaches name entry");
    require(g.player.rounds == rounds, "Ending cannot keep firing");
    s.handle_event(key(SDLK_SPACE));
    require(s.entering && s.screen == dv::Screen::Scores, "Space does not restart during name entry");
    text(s, "abcdefghijklmnop");
    require(s.name == "abcdefghijkl", "Pasted name is clipped to twelve characters");
    s.handle_event(key(SDLK_RETURN));
    s.handle_event(key(SDLK_RETURN));
    require(f.scores.entries().size() == 1 && f.scores.entries()[0].level == 5
        && f.scores.entries()[0].killed_by == "No-one" && f.scores.entries()[0].score == 10000,
        "Stage five score saved exactly once with victory attribution");
    g.grant_unlimited_arsenal();
    const auto action = s.handle_event(key(SDLK_SPACE));
    require(action == dv::AppAction::StartGame && s.screen == dv::Screen::Playing,
            "Restart goes directly to gameplay without title replay");
    require(g.stage == 1 && g.score == 0 && g.player.intro_active && g.player.scale > .12
        && !g.player.godmode && !g.player.vulcan_unlimited && !g.player.arsenal_unlimited,
        "Restart resets cheats and progress while retaining ship intro");
    g.warp_to_stage(5); g.player.invincible = 0; g.player.lives = 1;
    g.hit_player("Terrain Automaton"); advance(s, 5.1);
    require(s.entering && !g.victory, "Terrain death also reaches name entry");
    s.handle_event(key(SDLK_BACKQUOTE)); command(s, "warp 3");
    require(s.screen == dv::Screen::Playing && !s.entering && g.stage == 3 && g.player.alive,
            "Console warp revives player from score entry");
    advance(s, .3); s.handle_event(key(SDLK_ESCAPE)); advance(s, .3);
    g.player.invincible = 0; g.player.lives = 1;
    g.hit_player("The Wasp"); advance(s, 5.1);
    s.handle_event(key(SDLK_BACKQUOTE)); advance(s, .3);
    s.handle_event(key(SDLK_ESCAPE)); advance(s, .3);
    require(SDL_IsTextInputActive(), "Closing console restores high-score text input");
    text(s, "TEST"); s.handle_event(key(SDLK_RETURN));
    require(f.scores.entries().size() == 2 && f.scores.entries()[1].killed_by == "The Wasp",
            "Fatal hit owner survives name entry");
}
void test_controls(Fixture& f) {
    auto& s = f.session;
    s.handle_event(key(SDLK_PAUSE));
    s.handle_event(key(SDLK_F1));
    const double before = f.game.elapsed;
    advance(s, 1);
    require(s.screen == dv::Screen::Controls && s.controls_time > 0
        && f.game.elapsed == before && s.audio_paused(), "Controls animate while gameplay is paused");
    s.handle_event(key(SDLK_SPACE));
    require(f.game.paused, "Controls preserve manual pause");
    s.handle_event(key(SDLK_F1)); s.handle_event(key(SDLK_ESCAPE));
    require(!s.running && f.scores.entries().empty(), "Controls Escape quits without saving");
}
}
int main(int argc, char* argv[]) {
    try {
        if (argc != 3) throw std::runtime_error("Expected assets and artifact directory");
        SDL_setenv("SDL_VIDEODRIVER", "dummy", 1);
        SDL_setenv("SDL_AUDIODRIVER", "dummy", 1);
        const std::filesystem::path output(argv[2]);
        std::filesystem::create_directories(output);
        dv::Runtime runtime(argv[1], true, false);
        runtime.load_assets();
        for (const auto& test : std::vector<std::pair<std::string, void(*)(Fixture&)>>{
                {"console", test_console}, {"commands", test_commands}, {"cheats", test_cheats},
                {"ending-and-restart", test_ending}, {"controls", test_controls}}) {
            Fixture fixture(runtime.catalog, output / (test.first + "-scores.json"));
            test.second(fixture);
            std::cout << "PASS: " << test.first << '\n';
        }
    } catch (const std::exception& error) {
        std::cerr << "FAIL: " << error.what() << '\n';
        return 1;
    }
    return 0;
}
