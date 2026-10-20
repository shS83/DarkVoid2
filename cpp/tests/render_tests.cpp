#include "view.hpp"
#include <fstream>
#include <iostream>
#include <stdexcept>

int main(int argc, char* argv[]) {
    try {
        if (argc != 3) throw std::runtime_error("Expected assets and artifact directory");
        SDL_setenv("SDL_VIDEODRIVER", "dummy", 1);
        SDL_setenv("SDL_AUDIODRIVER", "dummy", 1);
        const std::filesystem::path output(argv[2]);
        std::filesystem::create_directories(output);
        dv::Runtime runtime(argv[1], true, false);
        runtime.load_assets();
        dv::Model game(runtime.catalog, 83);
        dv::Audio audio(runtime.assets, false);
        if (!audio.enabled()) throw std::runtime_error("Dummy audio device did not open");
        audio.music("1000 Handz - Announcement.mp3");
        audio.play("lasersound2.wav");
        audio.play("m61continued.ogg", .11);
        audio.pause(true);
        audio.pause(false);
        auto save = [&](const std::string& name) {
            runtime.screenshot(output / (name + ".png"));
            runtime.present();
        };
        runtime.begin(); dv::draw_title(runtime, 8); save("title");
        runtime.begin(); dv::draw_controls(runtime); save("controls");
        game.reset(1, true);
        game.player.invincible = 10000;
        dv::Input input; input.fire = true; input.vulcan = true;
        input.aim = {dv::width / 2, 250};
        for (int i = 0; i < 2100; ++i) {
            game.update(1.0 / 60, input);
            game.sounds.clear();
        }
        // Capture the sprites between damage flashes so their actual art is reviewable.
        for (auto& enemy : game.enemies) enemy.flash = 0;
        runtime.begin(); dv::draw_game(runtime, game); save("space-boss");
        game.paused = true;
        runtime.begin(); dv::draw_game(runtime, game); save("pause");
        game.reset(5, true);
        game.spawn_boss();
        game.player.invincible = 10000;
        for (int i = 0; i < 480; ++i) {
            game.update(1.0 / 60, input);
            game.sounds.clear();
        }
        game.apply_power(dv::Power::Shield); game.activate_shield();
        for (auto& enemy : game.enemies) enemy.flash = 0;
        runtime.begin(); dv::draw_game(runtime, game); save("terrain-boss");
        game.end_game(true);
        runtime.begin(); dv::draw_game(runtime, game); save("victory");
        game.reset(1, true);
        game.player.lives = 1; game.hit_player("The Wasp");
        runtime.begin(); dv::draw_game(runtime, game); save("game-over");
        const auto score_file = output / "render-test-scores.json";
        { std::ofstream empty(score_file); empty << "[]"; }
        dv::Scores scores(score_file);
        for (int i = 0; i < 10; ++i)
            scores.add({"Pilot" + std::to_string(i + 1), 30000 - i * 2000,
                        std::max(1, 5 - i / 2), "Terrain Automaton"});
        runtime.begin();
        dv::draw_game(runtime, game);
        dv::draw_scores(runtime, scores, "shS", true, 1, "");
        save("high-scores");
        audio.stop_effects();
        SDL_Delay(50); // Let the dummy audio callback process a buffer before destruction.
        std::cout << "Rendered eight scenes and exercised audio playback/pause/shutdown.\n";
    } catch (const std::exception& error) {
        std::cerr << error.what() << '\n'; return 1;
    }
    return 0;
}
