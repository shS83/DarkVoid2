#include "view.hpp"
#include <png.h>
#include <fstream>
#include <iostream>
#include <stdexcept>

namespace {
void require(bool condition, const std::string& message) {
    if (!condition) throw std::runtime_error(message);
}
std::vector<std::uint8_t> pixels(const std::filesystem::path& path) {
    png_image png{};
    png.version = PNG_IMAGE_VERSION;
    if (!png_image_begin_read_from_file(&png, path.string().c_str()))
        throw std::runtime_error(png.message);
    png.format = PNG_FORMAT_RGBA;
    std::vector<std::uint8_t> result(PNG_IMAGE_SIZE(png));
    if (!png_image_finish_read(&png, nullptr, result.data(), 0, nullptr)) {
        const std::string error = png.message;
        png_image_free(&png);
        throw std::runtime_error(error);
    }
    png_image_free(&png);
    return result;
}
struct Difference {
    int left = 1280, right = 0, top = 720, bottom = 0;
    std::uint64_t energy = 0;
};
Difference difference(const std::vector<std::uint8_t>& a, const std::vector<std::uint8_t>& b) {
    require(a.size() == b.size(), "Screenshot dimensions agree");
    Difference result;
    for (std::size_t i = 0; i < a.size(); i += 4) {
        int amount = 0;
        for (int c = 0; c < 3; ++c) amount += std::abs(int(a[i + c]) - int(b[i + c]));
        result.energy += amount;
        if (amount < 20) continue;
        const int x = static_cast<int>(i / 4 % 1280), y = static_cast<int>(i / 4 / 1280);
        result.left = std::min(result.left, x); result.right = std::max(result.right, x);
        result.top = std::min(result.top, y); result.bottom = std::max(result.bottom, y);
    }
    return result;
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
        runtime.begin(); dv::draw_controls(runtime, 1); save("controls-moving");
        require(difference(pixels(output / "controls.png"), pixels(output / "controls-moving.png")).energy > 100000,
                "Rainbow gradient moves through rendered controls");
        for (int x = 0; x < 512; ++x) {
            const auto color = dv::rainbow_color({double(x), 20}, 0);
            require(std::min({color.r, color.g, color.b}) >= 85
                && std::max({color.r, color.g, color.b}) - std::min({color.r, color.g, color.b}) >= 160,
                "Rainbow retains saturated bright colors throughout the spectrum");
            const auto moved = dv::rainbow_color({double(x) + 150, 170}, 1);
            require(color.r == moved.r && color.g == moved.g && color.b == moved.b,
                    "Rainbow moves from upper left to lower right");
        }
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
        dv::draw_game(runtime, game, false);
        dv::draw_scores(runtime, scores, "shS", true, 1, "");
        save("high-scores");
        game.reset(1, true);
        game.banner = 0;
        dv::Session session(game, scores, true);
        for (const auto* code : {"iddqd", "idkfa"}) {
            for (const char letter : std::string(code)) {
                SDL_Event event{}; event.type = SDL_KEYDOWN; event.key.keysym.sym = letter;
                session.handle_event(event);
            }
            const std::string prefix = code;
            session.cheat_notice_time = 0;
            runtime.begin(); dv::draw_session(runtime, session); save(prefix + "-baseline");
            session.cheat_notice_time = 3;
            runtime.begin(); dv::draw_session(runtime, session); save(prefix + "-small");
            session.cheat_notice_time = 2;
            runtime.begin(); dv::draw_session(runtime, session); save(prefix + "-zoom");
            session.cheat_notice_time = .1;
            runtime.begin(); dv::draw_session(runtime, session); save(prefix + "-fade");
            const auto base = pixels(output / (prefix + "-baseline.png"));
            const auto small = difference(base, pixels(output / (prefix + "-small.png")));
            const auto zoom = difference(base, pixels(output / (prefix + "-zoom.png")));
            const auto fade = difference(base, pixels(output / (prefix + "-fade.png")));
            require(zoom.right - zoom.left > small.right - small.left
                && zoom.bottom - zoom.top > small.bottom - small.top, "Cheat notice visibly zooms");
            require(fade.energy < zoom.energy / 3 && fade.energy > 0, "Cheat notice visibly fades");
            session.update(.2);
            runtime.begin(); dv::draw_session(runtime, session); save(prefix + "-finished");
            require(session.cheat_notice_time == 0, "Cheat notice animation ends");
        }
        session.console.toggle();
        session.console.update(.3);
        session.console.write("> warp 5");
        session.console.write("STAGE 5");
        session.console.input = "god";
        runtime.begin();
        runtime.rect({0, 0, dv::width, dv::height}, {200, 100, 50, 255});
        dv::draw_console(runtime, session.console);
        save("console-panel");
        const auto panel = pixels(output / "console-panel.png");
        const auto pixel = [&](int x, int y, int channel) { return panel[(y * 1280 + x) * 4 + channel]; };
        require(pixel(1275, 358, 0) == 200 && std::abs(pixel(1275, 362, 0) - 100) <= 1
            && std::abs(pixel(1275, 362, 1) - 50) <= 1 && std::abs(pixel(1275, 362, 2) - 25) <= 1,
            "Console covers lower half at half opacity");
        runtime.begin(); dv::draw_session(runtime, session); save("developer-console");
        audio.stop_effects();
        SDL_Delay(50); // Let the dummy audio callback process a buffer before destruction.
        std::cout << "Rendered gameplay, controls, console and cheat animations; "
                     "verified gradient motion, zoom, fade, panel opacity and audio playback.\n";
    } catch (const std::exception& error) {
        std::cerr << error.what() << '\n'; return 1;
    }
    return 0;
}
