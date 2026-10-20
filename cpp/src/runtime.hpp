#pragma once
#include "model.hpp"
#include <SDL.h>
#include <SDL_ttf.h>
#include <filesystem>
#include <map>
#include <memory>
#include <optional>

namespace dv {
void sdl_check(int result);
Color rainbow_color(Vec position, double time);
using Texture = std::unique_ptr<SDL_Texture, decltype(&SDL_DestroyTexture)>;
using Font = std::unique_ptr<TTF_Font, decltype(&TTF_CloseFont)>;
struct SdlGuard {
    SdlGuard();
    ~SdlGuard();
    SdlGuard(const SdlGuard&) = delete;
    SdlGuard& operator=(const SdlGuard&) = delete;
};
class Runtime {
public:
    Runtime(std::filesystem::path assets, bool headless, bool fullscreen);
    void load_assets();
    void begin();
    void present();
    void image(const Body& body, std::uint8_t alpha = 255, bool flash = false);
    void rect(Rect rect, Color color, bool outline = false);
    void line(Vec a, Vec b, Color color);
    void circle(Vec center, double radius, Color color);
    void text(const std::string& text, Vec position, int size, Color color = {},
              bool centered = true, const std::string& font = "MonaspiceXeNerdFontPropo-Light.otf",
              double max_width = width - 80, std::optional<double> rainbow_time = {},
              double zoom = 1);
    Vec text_size(const std::string& text, int size, const std::string& font);
    void clip(std::optional<Rect> bounds);
    void screenshot(const std::filesystem::path& path);
    Vec mouse() const;
    SDL_Window* window() const { return window_.get(); }
    Catalog catalog;
    const std::filesystem::path assets;
private:
    SdlGuard sdl_;
    std::unique_ptr<SDL_Window, decltype(&SDL_DestroyWindow)> window_{nullptr, SDL_DestroyWindow};
    std::unique_ptr<SDL_Renderer, decltype(&SDL_DestroyRenderer)> renderer_{nullptr, SDL_DestroyRenderer};
    std::unordered_map<std::string, Texture> textures_;
    std::unordered_map<std::string, Texture> flashes_;
    std::unordered_map<std::string, Texture> text_cache_;
    std::map<std::string, Font> fonts_;
    void load_image(const std::string& key);
    TTF_Font* font(const std::string& filename, int size);
};
class Audio {
public:
    Audio(std::filesystem::path assets, bool mute);
    ~Audio();
    Audio(const Audio&) = delete;
    Audio& operator=(const Audio&) = delete;
    void play(const std::string& name, double volume = 1);
    void music(const std::string& name);
    void pause(bool paused);
    void stop_effects();
    bool enabled() const { return device_ != 0; }
    static void verify(const std::filesystem::path& assets);
    static const std::vector<std::string>& music_names();
private:
    struct Clip { std::vector<float> samples; int channels = 0, rate = 0; };
    struct Voice { const Clip* clip = nullptr; double frame = 0, gain = 1; bool loop = false; };
    SDL_AudioDeviceID device_ = 0;
    std::filesystem::path assets_;
    std::map<std::string, Clip> clips_;
    std::unique_ptr<Clip> music_;
    std::array<Voice, 32> voices_{};
    Voice music_voice_;
    bool paused_ = false;
    std::size_t next_voice_ = 0;
    static Clip decode(const std::filesystem::path& path);
    static void callback(void* userdata, Uint8* stream, int length);
    static void mix(Voice& voice, float* output, int frames);
};
}
