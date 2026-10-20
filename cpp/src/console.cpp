#include "console.hpp"
#include "text_input.hpp"
#include <cctype>
#include <sstream>
#include <stdexcept>

namespace dv {
void DeveloperConsole::toggle() {
    open = !open;
    if (open) cursor_timer = 0;
}
void DeveloperConsole::update(double dt) {
    if (open) cursor_timer = std::fmod(cursor_timer + dt, 1);
    progress = std::clamp(progress + (open ? dt : -dt) / .22, 0.0, 1.0);
}
void DeveloperConsole::write(const std::string& text) {
    std::istringstream stream(text);
    for (std::string line; std::getline(stream, line);) {
        output.push_back(line);
        if (output.size() > 200) output.pop_front();
    }
    scroll = 0;
}
void DeveloperConsole::execute(Model& game) {
    const auto first = input.find_first_not_of(" \t\r\n");
    const auto last = input.find_last_not_of(" \t\r\n");
    const auto command = first == std::string::npos ? "" : input.substr(first, last - first + 1);
    input.clear();
    cursor_timer = 0;
    if (command.empty()) return;
    write("> " + command);
    if (history.empty() || history.back() != command) history.push_back(command);
    history_index = history.size();
    draft.clear();
    auto lower = command;
    for (auto& c : lower) c = static_cast<char>(std::tolower(static_cast<unsigned char>(c)));
    if (lower == "clear") { output.clear(); return; }
    try {
        write(game.execute_console_command(command));
    } catch (const std::invalid_argument& error) {
        write("Error: " + std::string(error.what()));
    }
}
bool DeveloperConsole::handle_event(const SDL_Event& event, Model& game) {
    if (event.type == SDL_KEYDOWN && (event.key.keysym.sym == SDLK_BACKQUOTE
        || event.key.keysym.sym == 0x00a7 || event.key.keysym.scancode == SDL_SCANCODE_GRAVE)) {
        if (!event.key.repeat) toggle();
        return true;
    }
    if (!active()) return false;
    if (!open) return true;
    if (event.type == SDL_TEXTINPUT) {
        const auto before = input;
        append_text(input, event.text.text, 128, true);
        history_index = history.size();
        if (input != before) cursor_timer = 0;
    } else if (event.type == SDL_KEYDOWN) {
        cursor_timer = 0;
        switch (event.key.keysym.sym) {
        case SDLK_ESCAPE: if (!event.key.repeat) toggle(); break;
        case SDLK_RETURN: case SDLK_KP_ENTER: execute(game); break;
        case SDLK_BACKSPACE: backspace(input); break;
        case SDLK_UP:
            if (history_index == history.size()) draft = input;
            if (history_index > 0) --history_index;
            if (!history.empty()) input = history[history_index];
            break;
        case SDLK_DOWN:
            history_index = std::min(history.size(), history_index + 1);
            input = history_index == history.size() ? draft : history[history_index];
            break;
        case SDLK_PAGEUP: scroll += 5; break;
        case SDLK_PAGEDOWN: scroll = std::max(0, scroll - 5); break;
        default: break;
        }
    } else if (event.type == SDL_MOUSEWHEEL) {
        scroll = std::max(0, scroll + event.wheel.y * 3);
    }
    return true;
}
}
