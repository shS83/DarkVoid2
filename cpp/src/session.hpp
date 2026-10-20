#pragma once
#include "console.hpp"
#include "scores.hpp"

namespace dv {
enum class Screen { Title, Controls, Playing, Scores };
enum class AppAction { None, StartGame, ToggleFullscreen };

// Shared by the SDL loop and event-driven regression tests.
class Session {
public:
    Session(Model& game, Scores& scores, bool playing = false);
    AppAction handle_event(const SDL_Event& event);
    void update(double dt, const Input& input = {});
    bool audio_paused() const;

    Model& game;
    Scores& scores;
    DeveloperConsole console;
    Screen screen = Screen::Title;
    bool running = true, entering = false, saved = false;
    std::string name, score_error;
    double title_time = 0, total_time = 0, controls_time = 0;
    std::string cheat_notice;
    double cheat_notice_time = 0;
private:
    Screen before_controls_ = Screen::Title;
    std::string cheat_keys_;
    void start();
    void save_score();
    void sync_text_input();
    void type_cheat(SDL_Keycode key);
};
}
