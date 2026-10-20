#include "model.hpp"
#include <charconv>
#include <cctype>
#include <sstream>
#include <stdexcept>

namespace dv {
std::string Model::execute_console_command(const std::string& command) {
    std::istringstream stream(command);
    std::vector<std::string> parts;
    for (std::string part; stream >> part;) {
        for (auto& c : part) c = static_cast<char>(std::tolower(static_cast<unsigned char>(c)));
        parts.push_back(part);
    }
    if (parts.empty()) return "";
    if (parts == std::vector<std::string>{"help"})
        return "god | impulse 9 | warp <stage> | powerup <type> | clear\n"
               "Powerups: shield, speed, health, spread, laser, cannon, piercing";
    if (parts[0] == "god") {
        if (parts.size() != 1) throw std::invalid_argument("Usage: god");
        player.godmode = !player.godmode;
        return std::string("God mode ") + (player.godmode ? "ON" : "OFF");
    }
    if (parts[0] == "impulse") {
        if (parts != std::vector<std::string>{"impulse", "9"})
            throw std::invalid_argument("Usage: impulse 9");
        constexpr std::array<Power, 4> weapons{Power::Spread, Power::Laser, Power::Cannon, Power::Piercing};
        const auto kind = weapons[static_cast<std::size_t>(random_int(0, 3))];
        apply_power(kind);
        player.vulcan_unlimited = true;
        player.heat = player.vulcan_timer = 0;
        player.overheated = false;
        return "Weapon upgrade: " + power_names[static_cast<std::size_t>(kind)]
            + "\nVulcan cooling disabled";
    }
    if (parts[0] == "powerup") {
        const auto kind = parts.size() == 2
            ? std::find(power_names.begin(), power_names.end(), parts[1]) : power_names.end();
        if (kind == power_names.end())
            throw std::invalid_argument("Usage: powerup <shield|speed|health|spread|laser|cannon|piercing>");
        const int shields = player.shields;
        apply_power(static_cast<Power>(kind - power_names.begin()));
        if (*kind == "shield")
            return "Shield charges: +" + std::to_string(player.shields - shields)
                + " (total " + std::to_string(player.shields) + ")";
        return "Powerup granted: " + *kind;
    }
    if (parts[0] == "warp") {
        if (parts.size() != 2) throw std::invalid_argument("Usage: warp <stage>");
        int target = 0;
        const auto& value = parts[1];
        const auto parsed = std::from_chars(value.data(), value.data() + value.size(), target);
        if (parsed.ec != std::errc{} || parsed.ptr != value.data() + value.size())
            throw std::invalid_argument("Stage must be an integer");
        warp_to_stage(target);
        return "STAGE " + std::to_string(target);
    }
    throw std::invalid_argument("Unknown command. Type help for commands.");
}
}
