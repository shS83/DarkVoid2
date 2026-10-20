#include "view.hpp"
#include <charconv>
#include <chrono>
#include <iostream>
#include <optional>
#include <thread>

namespace {
struct Options {
    std::filesystem::path assets, screenshot, scores;
    int frames = 0, stage = 1;
    std::uint32_t seed = std::random_device{}();
    bool headless = false, mute = false, fullscreen = false;
    bool start = false, skip_intro = false, boss = false, verify = false, help = false;
};
int number(const std::string& value, const std::string& option) {
    int result = 0;
    const auto parsed = std::from_chars(value.data(), value.data() + value.size(), result);
    if (parsed.ec != std::errc{} || parsed.ptr != value.data() + value.size() || result < 0)
        throw std::runtime_error(option + " expects a non-negative integer");
    return result;
}
Options parse(int argc, char* argv[]) {
    Options o;
    for (int i = 1; i < argc; ++i) {
        const std::string arg = argv[i];
        auto value = [&]() -> std::string {
            if (++i >= argc) throw std::runtime_error("Missing value for " + arg);
            return argv[i];
        };
        if (arg == "--help" || arg == "-h") o.help = true;
        else if (arg == "--assets") o.assets = value();
        else if (arg == "--screenshot") o.screenshot = value();
        else if (arg == "--scores") o.scores = value();
        else if (arg == "--frames") {
            o.frames = number(value(), arg);
            if (o.frames == 0) throw std::runtime_error("--frames must be positive");
        } else if (arg == "--stage") {
            o.stage = number(value(), arg);
            if (o.stage < 1 || o.stage > 5) throw std::runtime_error("--stage must be 1..5");
            o.start = o.skip_intro = true;
        } else if (arg == "--seed") o.seed = static_cast<std::uint32_t>(number(value(), arg));
        else if (arg == "--headless") o.headless = true;
        else if (arg == "--mute") o.mute = true;
        else if (arg == "--fullscreen") o.fullscreen = true;
        else if (arg == "--start") o.start = true;
        else if (arg == "--skip-intro") o.start = o.skip_intro = true;
        else if (arg == "--boss") o.boss = o.start = o.skip_intro = true;
        else if (arg == "--verify-assets") o.verify = true;
        else throw std::runtime_error("Unknown option: " + arg);
    }
    if (o.headless && o.frames == 0) o.frames = 120;
    if (!o.screenshot.empty() && o.frames == 0)
        throw std::runtime_error("--screenshot requires --frames or --headless");
    return o;
}
std::filesystem::path asset_path(const Options& options) {
    if (!options.assets.empty()) return std::filesystem::absolute(options.assets);
    // Prefer a portable layout next to the executable, then the checked-out assets.
    std::unique_ptr<char, decltype(&SDL_free)> base(SDL_GetBasePath(), SDL_free);
    if (base) {
        const auto sibling = std::filesystem::path(base.get()) / "assets";
        if (std::filesystem::is_directory(sibling)) return sibling;
    }
    return DARKVOID_ASSET_DIR;
}
std::filesystem::path score_path(const Options& options) {
    if (!options.scores.empty()) return options.scores;
    std::unique_ptr<char, decltype(&SDL_free)> path(SDL_GetPrefPath("shS83", "DarkVoid2-cpp"), SDL_free);
    if (!path) throw std::runtime_error(SDL_GetError());
    return std::filesystem::path(path.get()) / "highscores.json";
}
void append_name(std::string& name, const std::string& text) {
    auto length = [](const std::string& s) {
        return std::count_if(s.begin(), s.end(), [](unsigned char c) { return (c & 0xc0) != 0x80; });
    };
    for (std::size_t i = 0; i < text.size();) {
        const unsigned char c = static_cast<unsigned char>(text[i]);
        const std::size_t bytes = c < 0x80 ? 1 : c < 0xe0 ? 2 : c < 0xf0 ? 3 : 4;
        if (i + bytes > text.size()) break;
        if (c >= 32 && c != 127 && length(name) < 12) name.append(text, i, bytes);
        i += bytes;
    }
}
void backspace(std::string& name) {
    if (name.empty()) return;
    auto i = name.size() - 1;
    while (i > 0 && (static_cast<unsigned char>(name[i]) & 0xc0) == 0x80) --i;
    name.erase(i);
}
}

int main(int argc, char* argv[]) {
    try {
        const Options options = parse(argc, argv);
        if (options.help) {
            std::cout <<
                "Dark Void 2 - C++ edition\n"
                "  --assets DIR       use an explicit assets directory\n"
                "  --fullscreen       start in desktop fullscreen (F11 toggles)\n"
                "  --mute             disable audio\n"
                "  --start            skip title, retain ship introduction\n"
                "  --skip-intro       start playing immediately\n"
                "  --stage 1..5       start a selected stage without intro\n"
                "  --boss             spawn the selected stage's boss immediately\n"
                "  --seed N           reproducible simulation random seed\n"
                "  --scores FILE      separate JSON high-score file\n"
                "  --frames N         exit after N frames\n"
                "  --headless         dummy video/audio, fixed timestep, no frame limiter\n"
                "                     (defaults to 120 frames)\n"
                "  --screenshot PNG   save the final frame before exiting\n"
                "  --verify-assets    decode all required images, effects and music, then exit\n";
            return 0;
        }
        if (options.headless) {
            SDL_setenv("SDL_VIDEODRIVER", "dummy", 1);
            SDL_setenv("SDL_AUDIODRIVER", "dummy", 1);
        }
        dv::Runtime runtime(asset_path(options), options.headless, options.fullscreen);
        runtime.load_assets();
        if (options.verify) {
            dv::Audio::verify(runtime.assets);
            // Font rendering is part of asset validation, too.
            runtime.begin();
            dv::draw_title(runtime, 8);
            dv::draw_controls(runtime);
            std::cout << "All " << runtime.catalog.size() << " images, 11 sound effects, 13 music tracks and fonts decoded.\n";
            return 0;
        }
        dv::Audio audio(runtime.assets, options.mute);
        dv::Scores scores(score_path(options));
        dv::Model game(runtime.catalog, options.seed);
        game.reset(options.stage, options.skip_intro);
        if (options.boss) game.spawn_boss();
        enum class Screen { Title, Controls, Playing, Scores };
        Screen screen = options.start ? Screen::Playing : Screen::Title;
        Screen before_controls = screen;
        bool running = true, entering = false, saved = false, was_paused = false;
        std::string name, score_error;
        double title_time = 0, total_time = 0;
        auto play_game_music = [&]() {
            const auto& names = dv::Audio::music_names();
            audio.music(names[static_cast<std::size_t>(game.random_int(0, static_cast<int>(names.size()) - 1))]);
        };
        if (options.start) play_game_music();
        else audio.music("1000 Handz - Announcement.mp3");
        auto start = [&]() {
            game.reset();
            screen = Screen::Playing;
            entering = saved = false;
            name.clear(); score_error.clear();
            audio.stop_effects(); audio.pause(false);
            play_game_music();
        };
        auto save_score = [&]() {
            if (!entering || saved) return;
            try {
                const auto first = name.find_first_not_of(' ');
                const auto last = name.find_last_not_of(' ');
                const auto trimmed = first == std::string::npos ? "???" : name.substr(first, last - first + 1);
                scores.add({trimmed, game.score, game.stage, game.player.killer});
                saved = true; entering = false; score_error.clear();
                SDL_StopTextInput();
            } catch (const std::exception& error) {
                score_error = error.what();
                std::cerr << "Score save failed: " << error.what() << '\n';
            }
        };
        using Clock = std::chrono::steady_clock;
        auto previous = Clock::now();
        std::uint64_t frames = 0;
        while (running) {
            const auto frame_start = Clock::now();
            const double dt = options.headless ? 1.0 / 60.0
                : std::clamp(std::chrono::duration<double>(frame_start - previous).count(), 0.0, .05);
            previous = frame_start;
            total_time += dt;
            SDL_Event event;
            while (SDL_PollEvent(&event)) {
                if (event.type == SDL_QUIT) running = false;
                if (screen == Screen::Scores && entering && event.type == SDL_TEXTINPUT)
                    append_name(name, event.text.text);
                if (event.type != SDL_KEYDOWN || event.key.repeat) continue;
                const auto key = event.key.keysym.sym;
                if (key == SDLK_ESCAPE) { running = false; continue; }
                if (key == SDLK_F11) {
                    const bool fullscreen = SDL_GetWindowFlags(runtime.window()) & SDL_WINDOW_FULLSCREEN_DESKTOP;
                    dv::sdl_check(SDL_SetWindowFullscreen(runtime.window(),
                        fullscreen ? 0U : static_cast<Uint32>(SDL_WINDOW_FULLSCREEN_DESKTOP)));
                }
                if (screen == Screen::Title) {
                    if ((key == SDLK_SPACE || key == SDLK_RETURN) && title_time > 6.2) start();
                    else if (key == SDLK_F1) {
                        before_controls = screen; screen = Screen::Controls;
                    }
                } else if (screen == Screen::Controls) {
                    if (key == SDLK_SPACE || key == SDLK_F1) {
                        screen = before_controls;
                        if (screen == Screen::Playing) {
                            game.paused = was_paused; audio.pause(was_paused);
                        }
                    }
                } else if (screen == Screen::Playing) {
                    if ((key == SDLK_PAUSE || key == SDLK_p) && !game.game_over) {
                        game.paused = !game.paused; audio.pause(game.paused);
                    } else if (key == SDLK_LALT && !game.paused) game.activate_shield();
                    else if (key == SDLK_F1 && !game.game_over) {
                        was_paused = game.paused; game.paused = true; audio.pause(true);
                        before_controls = screen; screen = Screen::Controls;
                    }
                } else if (screen == Screen::Scores) {
                    if (entering) {
                        if (key == SDLK_BACKSPACE) backspace(name);
                        else if (key == SDLK_RETURN || key == SDLK_KP_ENTER) save_score();
                    } else if (key == SDLK_SPACE) {
                        screen = Screen::Title; title_time = 0; audio.stop_effects();
                        audio.pause(false); audio.music("1000 Handz - Announcement.mp3");
                    }
                }
            }
            if (!running) break;
            if (screen == Screen::Title) title_time += dt;
            else if (screen == Screen::Playing) {
                dv::Input input;
                const auto* keys = SDL_GetKeyboardState(nullptr);
                const Uint32 mouse = SDL_GetMouseState(nullptr, nullptr);
                input.move = {
                    static_cast<double>((keys[SDL_SCANCODE_D] || keys[SDL_SCANCODE_RIGHT])
                                      - (keys[SDL_SCANCODE_A] || keys[SDL_SCANCODE_LEFT])),
                    static_cast<double>((keys[SDL_SCANCODE_S] || keys[SDL_SCANCODE_DOWN])
                                      - (keys[SDL_SCANCODE_W] || keys[SDL_SCANCODE_UP]))};
                input.aim = runtime.mouse();
                input.fire = keys[SDL_SCANCODE_SPACE] || (mouse & SDL_BUTTON_LMASK);
                input.vulcan = mouse & (SDL_BUTTON_RMASK | SDL_BUTTON_MMASK);
                input.focus = keys[SDL_SCANCODE_LSHIFT];
                input.rail = keys[SDL_SCANCODE_LCTRL];
                game.update(dt, input);
                for (const auto& sound : game.sounds) audio.play(sound.name, sound.volume);
                game.sounds.clear();
                if (game.game_over && game.ending_time >= 5) {
                    screen = Screen::Scores;
                    entering = scores.qualifies(game.score);
                    saved = false; name.clear();
                    if (entering) SDL_StartTextInput();
                }
            }
            runtime.begin();
            switch (screen) {
            case Screen::Title: dv::draw_title(runtime, title_time); break;
            case Screen::Controls: dv::draw_controls(runtime); break;
            case Screen::Playing: dv::draw_game(runtime, game); break;
            case Screen::Scores:
                dv::draw_game(runtime, game);
                dv::draw_scores(runtime, scores, name, entering, total_time, score_error);
                break;
            }
            ++frames;
            if (options.frames > 0 && frames >= static_cast<std::uint64_t>(options.frames)) {
                if (!options.screenshot.empty()) runtime.screenshot(options.screenshot);
                running = false;
            }
            runtime.present();
            if (!options.headless)
                std::this_thread::sleep_until(frame_start + std::chrono::microseconds(16667));
        }
        SDL_StopTextInput();
        if (options.headless)
            std::cout << "Rendered " << frames << " frames; stage " << game.stage
                      << "; score " << game.score << "; lives " << game.player.lives << ".\n";
    } catch (const std::exception& error) {
        std::cerr << "Dark Void 2: " << error.what() << '\n';
        return 1;
    }
    return 0;
}
