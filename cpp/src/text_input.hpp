#pragma once
#include <algorithm>
#include <string>

namespace dv {
inline std::size_t text_length(const std::string& text) {
    return static_cast<std::size_t>(std::count_if(text.begin(), text.end(),
        [](unsigned char c) { return (c & 0xc0) != 0x80; }));
}
inline void append_text(std::string& destination, const std::string& text,
                        std::size_t limit, bool console = false) {
    auto length = text_length(destination);
    for (std::size_t i = 0; i < text.size() && length < limit;) {
        const unsigned char c = static_cast<unsigned char>(text[i]);
        const std::size_t bytes = c < 0x80 ? 1 : c < 0xe0 ? 2 : c < 0xf0 ? 3 : 4;
        if (i + bytes > text.size()) break;
        const auto character = text.substr(i, bytes);
        if (c >= 32 && c != 127 && !(console && (character == "§" || character == "`"))) {
            destination += character;
            ++length;
        }
        i += bytes;
    }
}
inline void backspace(std::string& text) {
    if (text.empty()) return;
    auto i = text.size() - 1;
    while (i > 0 && (static_cast<unsigned char>(text[i]) & 0xc0) == 0x80) --i;
    text.erase(i);
}
inline void remove_first_character(std::string& text) {
    if (text.empty()) return;
    std::size_t i = 1;
    while (i < text.size() && (static_cast<unsigned char>(text[i]) & 0xc0) == 0x80) ++i;
    text.erase(0, i);
}
}
