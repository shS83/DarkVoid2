#pragma once
#include "runtime.hpp"
#include "scores.hpp"

namespace dv {
void draw_title(Runtime& renderer, double time);
void draw_controls(Runtime& renderer);
void draw_game(Runtime& renderer, const Model& game);
void draw_scores(Runtime& renderer, const Scores& scores, const std::string& name,
                 bool entering, double time, const std::string& error);
}
