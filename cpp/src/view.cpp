#include "view.hpp"
#include "text_input.hpp"
#include <iomanip>
#include <sstream>

namespace dv {
namespace {
std::uint8_t alpha(double value) { return static_cast<std::uint8_t>(std::clamp(value, 0.0, 255.0)); }
constexpr Vec center{width / 2, height / 2};
const std::string title_font = "GoMonoNerdFontPropo-Bold.ttf";
const std::string gothic_font = "VL-Gothic-Regular.ttf";
void bar(Runtime& r, Rect bounds, double ratio, Color color) {
    r.rect(bounds, {20, 20, 30, 220});
    r.rect(bounds, {220, 220, 255, 255}, true);
    r.rect({bounds.x + 3, bounds.y + 3, (bounds.w - 6) * std::clamp(ratio, 0.0, 1.0), bounds.h - 6}, color);
}
}
void draw_title(Runtime& r, double time) {
    r.image({"backgrounds/stimu_wallpaper.png", center, {width, height}, 0});
    if (time < 5) return;
    r.rect({0, 0, width, height}, {0, 0, 0, alpha((time - 5) / 1.2 * 255)});
    const double fade = std::clamp((time - 6.2) / 1.2, 0.0, 1.0);
    if (fade <= 0) return;
    r.text("DARK VOID 2", {width / 2, height / 2 - 120}, 150,
           {alpha(175 + std::sin(time * 2.4) * 50), 20, 30, alpha(255 * fade)}, true, title_font);
    r.text("THE AVOIDED", {width / 2, height / 2 + 24}, 72,
           {255, 255, 255, alpha(230 * fade)}, true, title_font);
    r.text("ダーク ヴォイド 2", {width / 2, height / 2 + 100}, 42,
           {120, 210, 255, alpha(210 * fade)}, true, gothic_font);
    const std::array<Vec, 4> corners{{{190, 170}, {width - 190, height - 190},
                                     {260, height - 210}, {width - 300, 180}}};
    for (std::size_t i = 0; i < corners.size(); ++i)
        r.text("ダーク ヴォイド 2", corners[i], 32,
               {60, 110, 170, alpha((90 + std::sin(time * 1.6 + i) * 45) * fade)}, true, gothic_font);
    if (fade >= 1)
        r.text("press SPACE to avoid or F1 for controls", {width / 2, height - 120}, 42,
               {210, 230, 255, alpha(150 + std::sin(time * 4) * 80)}, true, gothic_font);
}
void draw_controls(Runtime& r, double time) {
    r.text("Control instructions", {width / 2, 180}, 72, {}, true, title_font);
    const std::array<const char*, 11> lines{
        "WASD or Arrows - Move the ship",
        "SPACE or Left mouse button - Fire main gun",
        "Right or Middle mouse button - Aim and fire Vulcan cannon",
        "Left CTRL - Railgun (requires cannon power-up)",
        "Left ALT - Activate shield (requires shield power-up)",
        "Left SHIFT - Focus movement",
        "Pause or P - Pause / resume",
        "F11 - Toggle fullscreen",
        "§ / ` - Developer console (type help for commands)",
        "SPACE or F1 - Return",
        "ESC - Quit"
    };
    for (std::size_t i = 0; i < lines.size(); ++i)
        r.text(lines[i], {width / 2, 300.0 + i * 58}, 34, {}, true, gothic_font, width - 120, time);
}
void draw_game(Runtime& r, const Model& g, bool show_ending, bool show_pause) {
    if (g.phase == Phase::Terrain || g.phase == Phase::TerrainFadeIn) {
        for (const auto& chunk : g.ocean)
            r.image({"backgrounds/ocean/stage5_ocean_chunk_" + std::to_string(chunk.image) + ".png",
                     {width / 2, chunk.y + chunk.h / 2}, {width * 1.15, chunk.h}, 0});
    } else {
        r.image({"backgrounds/space_background.png", center, {width, height}, 0});
        for (const auto& star : g.stars)
            r.rect({star.pos.x, star.pos.y, star.size, star.size}, {220, 220, 255, 255});
    }
    if (g.phase == Phase::EarthEnter || g.phase == Phase::ShipGrow
        || g.phase == Phase::ShipToEarth || g.phase == Phase::FadeOut)
        r.image({"rocks/earth.png", g.earth, image_size(g.catalog, "rocks/earth.png", .55), 0});
    for (const auto& e : g.enemies) if (!e.dead) r.image(e.body, 255, e.flash > 0);
    for (const auto& p : g.pickups) if (!p.dead) r.image(p.body);
    for (const auto& b : g.bullets) {
        if (b.dead) continue;
        if (!b.body.image.empty()) r.image(b.body);
        else if (b.kind == Weapon::Blue || b.kind == Weapon::Vulcan || b.kind == Weapon::Tracer) {
            const Vec half = Vec{0, b.body.size.y / 2}.rotated(b.body.angle);
            const Color color = b.kind == Weapon::Blue ? Color{80, 200, 255, 180}
                : b.kind == Weapon::Tracer ? Color{255, 120, 20, 255} : Color{255, 230, 170, 255};
            const Vec side = Vec{1, 0}.rotated(b.body.angle);
            for (int i = -static_cast<int>(b.body.size.x / 2); i <= static_cast<int>(b.body.size.x / 2); ++i)
                r.line(b.body.pos - half + side * i, b.body.pos + half + side * i, color);
            r.line(b.body.pos - half, b.body.pos + half, {230, 255, 255, 255});
        } else {
            // Draw translucent halo rings from outside inward.
            for (int radius = 22; radius > 6; radius -= 3)
                r.circle(b.body.pos, radius, {255, 120, 10, 15});
            r.circle(b.body.pos, 7, {255, 245, 110, 255});
            r.circle(b.body.pos, 5, {255, 90, 40, 255});
            r.circle(b.body.pos + Vec{-1, -1}, 3, {255, 255, 230, 255});
        }
    }
    if (g.player.alive && !g.victory) {
        const bool flash = g.player.invincible > 0 && static_cast<int>(g.elapsed * 12) % 2 == 0;
        r.image(g.player.body, g.player.invincible > 0 && !flash ? 140 : 255, flash);
        if (g.player.shield_timer > 0)
            r.image({"balls/metallipallo_3.png", g.player.body.pos, {210, 210}, g.elapsed * 180},
                    alpha(95 + 45 * std::sin(g.elapsed * 12)));
    }
    for (const auto& p : g.particles) {
        Color color = p.color; color.a = alpha(255 * p.life / p.max_life);
        r.rect({p.pos.x - p.size / 2, p.pos.y - p.size / 2, p.size, p.size}, color);
    }
    for (const auto& e : g.explosions) {
        const int frame = std::clamp(static_cast<int>(e.age / .045) + 1, 1, 31);
        const double size = e.boss ? 640 : 320;
        r.image({"explosions/exp_" + std::to_string(frame) + ".png", e.pos, {size, size}, 0});
    }
    if (!g.game_over) {
        r.text("STAGE " + std::to_string(g.stage), {16, 14}, 20, {255, 200, 255, 255}, false);
        r.text("SCORE " + std::to_string(g.score), {16, 50}, 20, {}, false);
        r.text("ENERGY", {16, 85}, 20, {220, 220, 255, 255}, false);
        for (int i = 0; i < std::min(g.player.lives, 20); ++i) {
            const double x = 16 + i * 24;
            r.line({x, 150}, {x + 10, 130}, {120, 220, 255, 255});
            r.line({x + 10, 130}, {x + 20, 150}, {120, 220, 255, 255});
            r.line({x, 150}, {x + 20, 150}, {120, 220, 255, 255});
        }
        if (g.player.lives > 20) r.text("x" + std::to_string(g.player.lives), {16, 155}, 20, {}, false);
        if (g.player.shields > 0 || g.player.shield_timer > 0) {
            r.text("SHIELDS LEFT " + std::to_string(g.player.shields), {16, 185}, 20,
                   {255, 200, 255, 255}, false);
            if (g.player.shield_timer > 0)
                r.text("SHIELD ACTIVE", {16, 220}, 20, {100, 150, 255, 255}, false);
        }
        const double ratio = g.player.heat / 3;
        const Color heat{alpha(80 + 350 * ratio), alpha(ratio < .5 ? 220 : 400 - 360 * ratio), 40, 255};
        bar(r, {width - 330, 50, 300, 24}, ratio, heat);
        std::string label = g.player.vulcan_unlimited ? "VULCAN UNLIMITED"
            : g.player.overheated ? "VULCAN OVERHEATED" : ratio > 0
            ? "VULCAN HEAT " + std::to_string(static_cast<int>(ratio * 100)) + "%" : "VULCAN READY";
        r.text(label, {width - 180, 30}, 20);
        if (g.player.power_timer > 0)
            r.text("POWER " + std::to_string(static_cast<int>(std::ceil(g.player.power_timer))) + "s",
                   {width - 180, 105}, 20, {150, 220, 255, 255});
        for (const auto& e : g.enemies) {
            if (!e.boss || e.dead) continue;
            const double health = static_cast<double>(e.hp) / e.max_hp;
            const Color color = health > .6 ? Color{180, 40, 220, 255}
                : health > .3 ? Color{255, 140, 40, 255} : Color{220, 40, 40, 255};
            bar(r, {(width - 520) / 2, height - 42, 520, 24}, health, color);
            r.text(e.name, {width / 2, height - 62}, 20);
        }
    }
    if (g.banner > 0 && !g.player.intro_active && !g.game_over) {
        const auto a = alpha(230 * std::min(1.0, g.banner / .35));
        r.rect({0, height / 2 - 70, width, 140}, {95, 95, 220, a});
        r.rect({0, height / 2 - 60, width, 120}, {255, 255, 255, a});
        r.text(g.phase == Phase::EarthEnter ? "ADVANCING TO TERRAIN" : "STAGE " + std::to_string(g.stage),
               center, 96, {0, 0, 0, a}, true, "JetBrainsMonoNerdFont-SemiBold.ttf");
    }
    if (g.game_over && show_ending) {
        r.rect({0, 0, width, height}, {0, 0, 0, 150});
        r.rect({0, height / 2 - 170, width, 340},
               g.victory ? Color{20, 60, 90, 210} : Color{0, 0, 0, 220});
        r.text(g.victory ? "MISSION COMPLETE" : "YOU DIED", {width / 2, height / 2 - 20}, 128,
               g.victory ? Color{220, 255, 255, 255} : Color{255, 40, 40, 255});
        r.text(g.victory ? "DARK VOID HAS BEEN SILENCED" : "You were humiliated by " + g.player.killer,
               {width / 2, height / 2 + 100}, g.victory ? 48 : 28);
    }
    if (g.paused && show_pause) {
        r.rect({0, 0, width, height}, {0, 0, 0, 140});
        r.text("PAUSED", center, 96);
        r.text("P / Pause to continue  |  F1 for controls", {width / 2, height / 2 + 110}, 28);
    }
    if (g.fade > 0) r.rect({0, 0, width, height}, {0, 0, 0, alpha(g.fade * 255)});
}
void draw_console(Runtime& r, DeveloperConsole& console) {
    if (!console.active()) return;
    const std::string font = "JetBrainsMonoNerdFont-SemiBold.ttf";
    constexpr int size = 24;
    const auto cell = r.text_size("M", size, font);
    const double line_height = cell.y + 3;
    const double panel_height = height / 2;
    const double eased = console.progress * console.progress * (3 - 2 * console.progress);
    const double top = height - std::round(panel_height * eased);
    r.rect({0, top, width, panel_height}, {0, 0, 0, 128});
    r.clip(Rect{0, top, width, panel_height});
    const double prompt_y = top + panel_height - line_height - 16;
    const double text_x = 24 + r.text_size("> ", size, font).x;
    auto visible = console.input;
    while (!visible.empty() && r.text_size("> " + visible + "_", size, font).x > width - 48)
        remove_first_character(visible);
    auto line = [&](const std::string& text, double y) {
        if (text.rfind("> ", 0) == 0) {
            r.text("> ", {24, y}, size, {0, 255, 0, 255}, false, font);
            r.text(text.substr(2), {text_x, y}, size, {}, false, font);
        } else r.text(text, {24, y}, size, {}, false, font);
    };
    line("> " + visible, prompt_y);
    if (console.open && console.cursor_timer < .5)
        r.text("_", {text_x + r.text_size(visible, size, font).x, prompt_y}, size, {}, false, font);
    const auto columns = static_cast<std::size_t>(std::max(1.0, (width - 48) / cell.x));
    std::vector<std::string> wrapped;
    for (const auto& text : console.output) {
        std::string part;
        std::size_t count = 0;
        for (const unsigned char c : text) {
            if ((c & 0xc0) != 0x80 && ++count > columns) {
                wrapped.push_back(part);
                part.clear();
                count = 1;
            }
            part += static_cast<char>(c);
        }
        wrapped.push_back(part);
    }
    const int visible_lines = std::max(0, static_cast<int>((panel_height - 48) / line_height) - 1);
    console.scroll = std::clamp(console.scroll, 0, std::max(0, static_cast<int>(wrapped.size()) - visible_lines));
    const int end = static_cast<int>(wrapped.size()) - console.scroll;
    for (int i = 0; i < visible_lines && end - i - 1 >= 0; ++i)
        line(wrapped[static_cast<std::size_t>(end - i - 1)], prompt_y - (i + 1) * line_height);
    r.clip({});
}
void draw_session(Runtime& r, Session& session) {
    switch (session.screen) {
    case Screen::Title: draw_title(r, session.title_time); break;
    case Screen::Controls: draw_controls(r, session.controls_time); break;
    case Screen::Playing:
        draw_game(r, session.game, true, !session.console.active());
        if (session.cheat_notice_time > 0 && !session.game.game_over) {
            const double age = 3 - session.cheat_notice_time;
            const double zoom = .55 + .5 * (1 - std::exp(-age * 3));
            const auto opacity = alpha(255 * std::min(1.0, session.cheat_notice_time / 1.2));
            r.text(session.cheat_notice, {width / 2, height * .42}, 82,
                   {255, 220, 90, opacity}, true, title_font, width - 100, {}, zoom);
        }
        break;
    case Screen::Scores:
        draw_game(r, session.game, false, false);
        draw_scores(r, session.scores, session.name, session.entering,
                    session.total_time, session.score_error);
        break;
    }
    draw_console(r, session.console);
}
void draw_scores(Runtime& r, const Scores& scores, const std::string& name,
                  bool entering, double time, const std::string& error) {
    r.rect({0, 0, width, height}, {0, 0, 0, 185});
    r.rect({width / 2 - 430, 75, 860, 930}, {10, 8, 20, 245});
    r.rect({width / 2 - 430, 75, 860, 930}, {190, 160, 255, 255}, true);
    r.text("HIGH SCORES", {width / 2, 135}, 56, {255, 230, 150, 255});
    int row = 0;
    for (const auto& entry : scores.entries()) {
        std::ostringstream line;
        line << std::setw(2) << std::setfill('0') << row + 1 << ". " << std::setfill(' ')
             << std::left << std::setw(12) << entry.name << std::right << std::setw(9)
             << entry.score << "  STAGE " << entry.level;
        const double y = 215 + row * 62;
        r.text(line.str(), {width / 2, y}, 22, row == 0 ? Color{255, 220, 120, 255} : Color{});
        r.text("killed by " + entry.killed_by, {width / 2, y + 27}, 16, {170, 150, 210, 255});
        ++row;
    }
    if (entering) {
        r.text("ENTER YOUR NAME", {width / 2, 860}, 22, {255, 230, 120, 255});
        r.rect({width / 2 - 180, 888, 360, 48}, {120, 220, 255, 255}, true);
        r.text(name + (static_cast<int>(time * 2.5) % 2 == 0 ? "_" : ""), {width / 2, 912}, 26,
               {120, 220, 255, 255});
        r.text("ENTER to save", {width / 2, 965}, 20, {170, 170, 210, 255});
    } else
        r.text("PRESS ESC TO QUIT OR SPACE TO RESTART", {width / 2, 965}, 20, {170, 170, 210, 255});
    if (!error.empty()) r.text(error, {width / 2, 1040}, 20, {255, 100, 100, 255});
}
}
