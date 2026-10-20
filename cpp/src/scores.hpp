#pragma once
#include <filesystem>
#include <string>
#include <vector>

namespace dv {
struct Score { std::string name; int score = 0, level = 1; std::string killed_by; };
class Scores {
public:
    explicit Scores(std::filesystem::path path);
    bool qualifies(int score) const;
    void add(Score score);
    const std::vector<Score>& entries() const { return entries_; }
private:
    std::filesystem::path path_;
    std::vector<Score> entries_;
};
}
