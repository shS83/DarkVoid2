#pragma once
#include "runtime.hpp"
#include "scores.hpp"
#include "session.hpp"

namespace dv {
void draw_title(Runtime& renderer, double time);
void draw_controls(Runtime& renderer, double time = 0);
void draw_game(Runtime& renderer, const Model& game, bool show_ending = true, bool show_pause = true);
void draw_console(Runtime& renderer, DeveloperConsole& console);
void draw_session(Runtime& renderer, Session& session);
void draw_scores(Runtime& renderer, const Scores& scores, const std::string& name,
                 bool entering, double time, const std::string& error);
}
