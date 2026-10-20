#include "session.hpp"
#include "text_input.hpp"

namespace dv {
Session::Session(Model& model, Scores& table, bool playing)
    : game(model), scores(table), screen(playing ? Screen::Playing : Screen::Title) {
    sync_text_input();
}
void Session::sync_text_input() {
    const bool needed = console.open || (!console.active() && screen == Screen::Scores && entering);
    if (needed && !SDL_IsTextInputActive()) SDL_StartTextInput();
    else if (!needed && SDL_IsTextInputActive()) SDL_StopTextInput();
}
void Session::start() {
    game.reset();
    console = DeveloperConsole{};
    screen = Screen::Playing;
    entering = saved = false;
    name.clear();
    score_error.clear();
    cheat_keys_.clear();
    cheat_notice.clear();
    cheat_notice_time = 0;
    sync_text_input();
}
void Session::type_cheat(SDL_Keycode key) {
    if (key < SDLK_a || key > SDLK_z) return;
    cheat_keys_ += static_cast<char>(key);
    if (cheat_keys_.size() > 5) cheat_keys_.erase(0, cheat_keys_.size() - 5);
    if (cheat_keys_ == "iddqd") {
        game.player.godmode = !game.player.godmode;
        cheat_notice = game.player.godmode ? "GOD MODE: ON" : "GOD MODE: OFF";
    } else if (cheat_keys_ == "idkfa") {
        game.grant_unlimited_arsenal();
        cheat_notice = "SAY HELLO TO MY LITTLE FRIEND";
    } else return;
    cheat_notice_time = 3;
    cheat_keys_.clear();
}
void Session::save_score() {
    if (!entering || saved) return;
    try {
        const auto first = name.find_first_not_of(' ');
        const auto last = name.find_last_not_of(' ');
        const auto trimmed = first == std::string::npos ? "???" : name.substr(first, last - first + 1);
        scores.add({trimmed, game.score, game.stage, game.player.killer});
        saved = true;
        entering = false;
        score_error.clear();
    } catch (const std::exception& error) {
        score_error = error.what();
    }
    sync_text_input();
}
AppAction Session::handle_event(const SDL_Event& event) {
    if (event.type == SDL_QUIT) {
        running = false;
        return AppAction::None;
    }
    if (screen == Screen::Playing || screen == Screen::Scores) {
        if (console.handle_event(event, game)) {
            cheat_keys_.clear();
            // A successful warp can revive a finished game while its score screen is open.
            if (screen == Screen::Scores && !game.game_over) {
                screen = Screen::Playing;
                entering = saved = false;
                name.clear();
                score_error.clear();
            }
            sync_text_input();
            return AppAction::None;
        }
    }
    if (screen == Screen::Scores && entering && event.type == SDL_TEXTINPUT)
        append_text(name, event.text.text, 12);
    if (event.type != SDL_KEYDOWN) return AppAction::None;
    const auto key = event.key.keysym.sym;
    if (screen == Screen::Scores && entering && key == SDLK_BACKSPACE) {
        backspace(name);
        return AppAction::None;
    }
    if (event.key.repeat) return AppAction::None;
    if (key == SDLK_ESCAPE) {
        running = false;
        return AppAction::None;
    }
    if (key == SDLK_F11) return AppAction::ToggleFullscreen;
    if (screen == Screen::Title) {
        if ((key == SDLK_SPACE || key == SDLK_RETURN) && title_time > 6.2) {
            start();
            return AppAction::StartGame;
        }
        if (key == SDLK_F1) {
            before_controls_ = screen;
            screen = Screen::Controls;
            controls_time = 0;
        }
    } else if (screen == Screen::Controls) {
        if (key == SDLK_SPACE || key == SDLK_F1) screen = before_controls_;
    } else if (screen == Screen::Playing) {
        if (!game.paused && !game.game_over && !(event.key.keysym.mod & (KMOD_CTRL | KMOD_ALT | KMOD_GUI)))
            type_cheat(key);
        if ((key == SDLK_PAUSE || key == SDLK_p) && !game.game_over)
            game.paused = !game.paused;
        else if (key == SDLK_LALT && !game.paused) game.activate_shield();
        else if (key == SDLK_F1 && !game.game_over) {
            before_controls_ = screen;
            screen = Screen::Controls;
            controls_time = 0;
        }
        if (game.paused || screen != Screen::Playing) cheat_keys_.clear();
    } else if (screen == Screen::Scores) {
        if (entering) {
            if (key == SDLK_RETURN || key == SDLK_KP_ENTER) save_score();
        } else if (key == SDLK_SPACE) {
            start();
            return AppAction::StartGame;
        }
    }
    return AppAction::None;
}
bool Session::audio_paused() const {
    return console.active() || game.paused
        || (screen == Screen::Controls && before_controls_ == Screen::Playing);
}
void Session::update(double dt, const Input& input) {
    if (!running) return;
    total_time += dt;
    console.update(dt);
    sync_text_input();
    if (screen == Screen::Title) title_time += dt;
    else if (screen == Screen::Controls) controls_time += dt;
    else if (screen == Screen::Playing && !console.active()) {
        if (!game.paused) cheat_notice_time = std::max(0.0, cheat_notice_time - dt);
        game.update(dt, input);
        if (game.game_over && game.ending_time >= 5) {
            screen = Screen::Scores;
            entering = scores.qualifies(game.score);
            saved = false;
            name.clear();
            score_error.clear();
            cheat_keys_.clear();
            sync_text_input();
        }
    }
    for (const auto& message : game.messages) console.write(message);
    game.messages.clear();
}
}
