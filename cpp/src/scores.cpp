#include "scores.hpp"
#include <nlohmann/json.hpp>
#include <algorithm>
#include <fstream>
#include <stdexcept>

namespace dv {
Scores::Scores(std::filesystem::path path) : path_(std::move(path)) {
    std::ifstream file(path_);
    if (!file) return;
    const auto json = nlohmann::json::parse(file, nullptr, false);
    if (!json.is_array()) return;
    for (const auto& entry : json) {
        if (!entry.is_object() || !entry.contains("name") || !entry["name"].is_string()
            || !entry.contains("score") || !entry["score"].is_number_integer()
            || !entry.contains("level") || !entry["level"].is_number_integer()) continue;
        try {
            entries_.push_back({entry["name"].get<std::string>(), entry["score"].get<int>(),
                entry["level"].get<int>(), entry.value("killed_by", "the Illithids")});
        } catch (const nlohmann::json::exception&) { /* Ignore malformed rows. */ }
    }
    std::stable_sort(entries_.begin(), entries_.end(),
        [](const Score& a, const Score& b) { return a.score > b.score; });
    if (entries_.size() > 10) entries_.resize(10);
}
bool Scores::qualifies(int score) const {
    return entries_.size() < 10 || score > entries_.back().score;
}
void Scores::add(Score score) {
    auto updated = entries_;
    updated.push_back(std::move(score));
    std::stable_sort(updated.begin(), updated.end(),
        [](const Score& a, const Score& b) { return a.score > b.score; });
    if (updated.size() > 10) updated.resize(10);
    nlohmann::json json = nlohmann::json::array();
    for (const auto& entry : updated) {
        json.push_back({{"name", entry.name}, {"score", entry.score},
                       {"level", entry.level}, {"killed_by", entry.killed_by}});
    }
    if (!path_.parent_path().empty()) std::filesystem::create_directories(path_.parent_path());
    auto temporary = path_;
    temporary += ".tmp";
    {
        std::ofstream file(temporary, std::ios::trunc);
        file << json.dump(4) << '\n';
        file.close();
        if (!file) throw std::runtime_error("Could not write scores: " + temporary.string());
    }
    std::filesystem::rename(temporary, path_);
    entries_ = std::move(updated);
}
}
