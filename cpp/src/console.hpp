#pragma once
#include "model.hpp"
#include <SDL.h>
#include <deque>

namespace dv {
class DeveloperConsole {
public:
    bool open = false;
    double progress = 0, cursor_timer = 0;
    std::string input, draft;
    std::vector<std::string> history;
    std::deque<std::string> output;
    std::size_t history_index = 0;
    int scroll = 0;

    bool active() const { return open || progress > 0; }
    void toggle();
    void update(double dt);
    void write(const std::string& text);
    void execute(Model& game);
    bool handle_event(const SDL_Event& event, Model& game);
};
}
