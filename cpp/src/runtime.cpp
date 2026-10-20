#include "runtime.hpp"
#include <png.h>
#include <sndfile.h>
#include <cstring>
#include <iostream>
#include <limits>
#include <stdexcept>

namespace dv {
void sdl_check(int result) {
    if (result < 0) throw std::runtime_error(SDL_GetError());
}
SdlGuard::SdlGuard() {
    sdl_check(SDL_Init(SDL_INIT_VIDEO | SDL_INIT_TIMER));
    if (TTF_Init() < 0) {
        const std::string error = TTF_GetError();
        SDL_Quit();
        throw std::runtime_error(error);
    }
}
SdlGuard::~SdlGuard() { TTF_Quit(); SDL_Quit(); }
Runtime::Runtime(std::filesystem::path path, bool headless, bool fullscreen) : assets(std::move(path)) {
    SDL_SetHint(SDL_HINT_RENDER_SCALE_QUALITY, "1");
    const Uint32 flags = headless ? SDL_WINDOW_HIDDEN : SDL_WINDOW_RESIZABLE;
    window_.reset(SDL_CreateWindow("Dark Void 2 - The Avoided (C++)",
        SDL_WINDOWPOS_CENTERED, SDL_WINDOWPOS_CENTERED, 1280, 720,
        flags | (fullscreen ? static_cast<Uint32>(SDL_WINDOW_FULLSCREEN_DESKTOP) : 0U)));
    if (!window_) throw std::runtime_error(SDL_GetError());
    if (!headless)
        renderer_.reset(SDL_CreateRenderer(window_.get(), -1, SDL_RENDERER_ACCELERATED));
    if (!renderer_) renderer_.reset(SDL_CreateRenderer(window_.get(), -1, SDL_RENDERER_SOFTWARE));
    if (!renderer_) throw std::runtime_error(SDL_GetError());
    sdl_check(SDL_RenderSetLogicalSize(renderer_.get(), static_cast<int>(width), static_cast<int>(height)));
    sdl_check(SDL_SetRenderDrawBlendMode(renderer_.get(), SDL_BLENDMODE_BLEND));
}
void Runtime::load_image(const std::string& key) {
    const auto path = assets / key;
    png_image png{};
    png.version = PNG_IMAGE_VERSION;
    if (!png_image_begin_read_from_file(&png, path.string().c_str())) {
        const std::string error = png.message;
        png_image_free(&png);
        throw std::runtime_error("Could not load " + path.string() + ": " + error);
    }
    png.format = PNG_FORMAT_RGBA;
    std::vector<std::uint8_t> pixels(PNG_IMAGE_SIZE(png));
    if (!png_image_finish_read(&png, nullptr, pixels.data(), 0, nullptr)) {
        const std::string error = png.message;
        png_image_free(&png);
        throw std::runtime_error("Could not decode " + path.string() + ": " + error);
    }
    const int w = static_cast<int>(png.width), h = static_cast<int>(png.height);
    png_image_free(&png);
    Mask mask{w, h, std::vector<std::uint8_t>(static_cast<std::size_t>(w) * h), {}};
    int min_x = w, min_y = h, max_x = -1, max_y = -1;
    for (int y = 0; y < h; ++y)
        for (int x = 0; x < w; ++x) {
            const auto i = static_cast<std::size_t>(y) * w + x;
            mask.alpha[i] = pixels[i * 4 + 3];
            if (mask.alpha[i] >= 24) {
                min_x = std::min(min_x, x); max_x = std::max(max_x, x);
                min_y = std::min(min_y, y); max_y = std::max(max_y, y);
            }
        }
    if (max_x >= min_x && max_y >= min_y)
        mask.visible_bounds = {static_cast<double>(min_x), static_cast<double>(min_y),
                               static_cast<double>(max_x - min_x + 1),
                               static_cast<double>(max_y - min_y + 1)};
    auto texture = [&](const std::vector<std::uint8_t>& rgba) {
        Texture result(SDL_CreateTexture(renderer_.get(), SDL_PIXELFORMAT_RGBA32,
                                          SDL_TEXTUREACCESS_STATIC, w, h), SDL_DestroyTexture);
        if (!result) throw std::runtime_error(SDL_GetError());
        sdl_check(SDL_UpdateTexture(result.get(), nullptr, rgba.data(), w * 4));
        sdl_check(SDL_SetTextureBlendMode(result.get(), SDL_BLENDMODE_BLEND));
        return result;
    };
    textures_.emplace(key, texture(pixels));
    if (key.rfind("ships/", 0) == 0 || key.rfind("rocks/rock_", 0) == 0) {
        for (std::size_t i = 0; i < mask.alpha.size(); ++i)
            pixels[i * 4] = pixels[i * 4 + 1] = pixels[i * 4 + 2] = 255;
        flashes_.emplace(key, texture(pixels));
    }
    catalog.emplace(key, std::move(mask));
}
void Runtime::load_assets() {
    std::vector<std::string> images{
        "ships/finnfighter.png", "laser.png", "laser-red.png", "rocks/earth.png",
        "balls/metallipallo_3.png", "backgrounds/space_background.png", "backgrounds/stimu_wallpaper.png"
    };
    for (const std::string name : {"purplealus", "redhawk", "redalus", "robotector", "bluehawk",
          "turqoiseship", "lilac-thrusters", "grayship", "blackhawk", "orangeship", "vihree-alus"})
        images.push_back("ships/" + name + ".png");
    for (const std::string name : {"dark-crusader", "boss-2", "foobarhead1",
          "stage4_boss_void_dreadnought_full", "stage5_terrain_automaton"})
        images.push_back("ships/bosses/" + name + ".png");
    for (const auto& name : power_names) images.push_back("powerups/powerup-" + name + ".png");
    for (int i = 1; i <= 6; ++i) images.push_back("rocks/rock_" + std::to_string(i) + ".png");
    for (int i = 1; i <= 31; ++i) images.push_back("explosions/exp_" + std::to_string(i) + ".png");
    for (int i = 1; i <= 3; ++i)
        images.push_back("backgrounds/ocean/stage5_ocean_chunk_" + std::to_string(i) + ".png");
    for (const auto& key : images) load_image(key);
}
void Runtime::begin() {
    sdl_check(SDL_SetRenderDrawColor(renderer_.get(), 0, 0, 0, 255));
    sdl_check(SDL_RenderClear(renderer_.get()));
}
void Runtime::present() { SDL_RenderPresent(renderer_.get()); }
void Runtime::image(const Body& body, std::uint8_t alpha, bool flash) {
    SDL_Texture* texture = flash && flashes_.count(body.image)
        ? flashes_.at(body.image).get() : textures_.at(body.image).get();
    sdl_check(SDL_SetTextureAlphaMod(texture, alpha));
    SDL_FRect target{static_cast<float>(body.pos.x - body.size.x / 2),
                     static_cast<float>(body.pos.y - body.size.y / 2),
                     static_cast<float>(body.size.x), static_cast<float>(body.size.y)};
    sdl_check(SDL_RenderCopyExF(renderer_.get(), texture, nullptr, &target,
                               body.angle, nullptr, SDL_FLIP_NONE));
}
void Runtime::rect(Rect r, Color color, bool outline) {
    if (outline) {
        // Filled edges remain visible at fractional logical-to-window scales.
        rect({r.x, r.y, r.w, 2}, color);
        rect({r.x, r.y + r.h - 2, r.w, 2}, color);
        rect({r.x, r.y, 2, r.h}, color);
        rect({r.x + r.w - 2, r.y, 2, r.h}, color);
        return;
    }
    sdl_check(SDL_SetRenderDrawColor(renderer_.get(), color.r, color.g, color.b, color.a));
    const SDL_FRect rect{static_cast<float>(r.x), static_cast<float>(r.y),
                         static_cast<float>(r.w), static_cast<float>(r.h)};
    sdl_check(SDL_RenderFillRectF(renderer_.get(), &rect));
}
void Runtime::line(Vec a, Vec b, Color color) {
    sdl_check(SDL_SetRenderDrawColor(renderer_.get(), color.r, color.g, color.b, color.a));
    sdl_check(SDL_RenderDrawLineF(renderer_.get(), static_cast<float>(a.x), static_cast<float>(a.y),
                                 static_cast<float>(b.x), static_cast<float>(b.y)));
}
void Runtime::circle(Vec pos, double radius, Color color) {
    for (int y = -static_cast<int>(radius); y <= static_cast<int>(radius); ++y) {
        const double x = std::sqrt(std::max(0.0, radius * radius - y * y));
        line({pos.x - x, pos.y + y}, {pos.x + x, pos.y + y}, color);
    }
}
TTF_Font* Runtime::font(const std::string& filename, int size) {
    const std::string font_key = filename + ":" + std::to_string(size);
    if (!fonts_.count(font_key)) {
        Font font(TTF_OpenFont((assets / "fonts" / filename).string().c_str(), size), TTF_CloseFont);
        if (!font) throw std::runtime_error(TTF_GetError());
        fonts_.emplace(font_key, std::move(font));
    }
    return fonts_.at(font_key).get();
}
Vec Runtime::text_size(const std::string& text, int size, const std::string& filename) {
    int w = 0, h = 0;
    if (TTF_SizeUTF8(font(filename, size), text.c_str(), &w, &h) < 0)
        throw std::runtime_error(TTF_GetError());
    return {static_cast<double>(w), static_cast<double>(h)};
}
void Runtime::clip(std::optional<Rect> bounds) {
    if (!bounds) {
        sdl_check(SDL_RenderSetClipRect(renderer_.get(), nullptr));
        return;
    }
    const SDL_Rect rect{static_cast<int>(bounds->x), static_cast<int>(bounds->y),
                        static_cast<int>(bounds->w), static_cast<int>(bounds->h)};
    sdl_check(SDL_RenderSetClipRect(renderer_.get(), &rect));
}
Color rainbow_color(Vec position, double time) {
    double hue = std::fmod(position.x + position.y - std::floor(time * 300), 512.0) / 512.0;
    if (hue < 0) hue += 1;
    const double sector = hue * 6;
    const double x = 1 - std::abs(std::fmod(sector, 2.0) - 1);
    double r = 0, g = 0, b = 0;
    if (sector < 1) { r = 1; g = x; }
    else if (sector < 2) { r = x; g = 1; }
    else if (sector < 3) { g = 1; b = x; }
    else if (sector < 4) { g = x; b = 1; }
    else if (sector < 5) { r = x; b = 1; }
    else { r = 1; b = x; }
    auto channel = [](double c) { return static_cast<std::uint8_t>(std::lround((.35 + .65 * c) * 255)); };
    return {channel(r), channel(g), channel(b), 255};
}
void Runtime::text(const std::string& label, Vec pos, int size, Color color,
                   bool centered, const std::string& filename, double max_width,
                   std::optional<double> rainbow_time, double zoom) {
    if (label.empty()) return;
    const std::string font_key = filename + ":" + std::to_string(size);
    const std::string key = font_key + ":" + label;
    if (!text_cache_.count(key)) {
        if (text_cache_.size() > 512) text_cache_.clear();
        std::unique_ptr<SDL_Surface, decltype(&SDL_FreeSurface)> surface(
            TTF_RenderUTF8_Blended(font(filename, size), label.c_str(), {255, 255, 255, 255}),
            SDL_FreeSurface);
        if (!surface) throw std::runtime_error(TTF_GetError());
        Texture texture(SDL_CreateTextureFromSurface(renderer_.get(), surface.get()), SDL_DestroyTexture);
        if (!texture) throw std::runtime_error(SDL_GetError());
        text_cache_.emplace(key, std::move(texture));
    }
    auto* texture = text_cache_.at(key).get();
    int w = 0, h = 0;
    sdl_check(SDL_QueryTexture(texture, nullptr, nullptr, &w, &h));
    const double scale = std::min(zoom, max_width / w);
    SDL_FRect target{static_cast<float>(pos.x - (centered ? w * scale / 2 : 0)),
                     static_cast<float>(pos.y - (centered ? h * scale / 2 : 0)),
                     static_cast<float>(w * scale), static_cast<float>(h * scale)};
    sdl_check(SDL_SetTextureColorMod(texture, color.r, color.g, color.b));
    sdl_check(SDL_SetTextureAlphaMod(texture, color.a));
    if (rainbow_time) {
        sdl_check(SDL_SetTextureColorMod(texture, 255, 255, 255));
        sdl_check(SDL_SetTextureAlphaMod(texture, 255));
        std::vector<SDL_Vertex> vertices;
        std::vector<int> indices;
        // Tint the cached white glyph mask; a fixed mesh avoids per-frame font rasterization.
        constexpr float step = 16;
        auto vertex = [&](float x, float y) {
            auto tint = rainbow_color({target.x + x, target.y + y}, *rainbow_time);
            return SDL_Vertex{{target.x + x, target.y + y}, {tint.r, tint.g, tint.b, color.a},
                              {x / target.w, y / target.h}};
        };
        for (float y = 0; y < target.h; y += step)
            for (float x = 0; x < target.w; x += step) {
                const float right = std::min(x + step, target.w);
                const float bottom = std::min(y + step, target.h);
                const int first = static_cast<int>(vertices.size());
                vertices.insert(vertices.end(), {vertex(x, y), vertex(right, y),
                                                 vertex(right, bottom), vertex(x, bottom)});
                indices.insert(indices.end(), {first, first + 1, first + 2, first, first + 2, first + 3});
            }
        sdl_check(SDL_RenderGeometry(renderer_.get(), texture, vertices.data(),
            static_cast<int>(vertices.size()), indices.data(), static_cast<int>(indices.size())));
        return;
    }
    sdl_check(SDL_RenderCopyF(renderer_.get(), texture, nullptr, &target));
}
Vec Runtime::mouse() const {
    int x = 0, y = 0;
    SDL_GetMouseState(&x, &y);
    float logical_x = 0, logical_y = 0;
    SDL_RenderWindowToLogical(renderer_.get(), x, y, &logical_x, &logical_y);
    return {logical_x, logical_y};
}
void Runtime::screenshot(const std::filesystem::path& path) {
    int w = 0, h = 0;
    sdl_check(SDL_GetRendererOutputSize(renderer_.get(), &w, &h));
    std::vector<std::uint8_t> pixels(static_cast<std::size_t>(w) * h * 4);
    sdl_check(SDL_RenderReadPixels(renderer_.get(), nullptr, SDL_PIXELFORMAT_RGBA32, pixels.data(), w * 4));
    png_image png{};
    png.version = PNG_IMAGE_VERSION; png.width = w; png.height = h; png.format = PNG_FORMAT_RGBA;
    if (!png_image_write_to_file(&png, path.string().c_str(), 0, pixels.data(), 0, nullptr))
        throw std::runtime_error("Screenshot: " + std::string(png.message));
}

namespace {
const std::vector<std::string> effects{
    "lasersound2.wav", "lasersound.wav", "lasercont.wav", "m61continued.ogg", "ding.mp3",
    "levelup.wav", "clink.wav", "explosion1-long.wav", "explosion2.wav", "explosion3.wav", "gameover.wav"
};
}
const std::vector<std::string>& Audio::music_names() {
    static const std::vector<std::string> names{
        "1000 Handz - Reps.mp3", "1000 Handz - Announcement.mp3", "1000 Handz - No Option.mp3",
        "Colorcast - Coffee Break.mp3", "Colorcast - Drown.mp3", "Colorcast - Need.mp3",
        "Jahzzar - Forest Pan.mp3", "Jahzzar - Pink Fluid.mp3",
        "Lightning Traveler - Celestial Drift.mp3", "Lightning Traveler - Eclipse Horizon.mp3",
        "Lightning Traveler - Event Horizon.mp3", "Lightning Traveler - Lunar Echo.mp3",
        "Ov Moi Omm - The Dictator’s Transmission (YSMHB).mp3"
    };
    return names;
}
Audio::Clip Audio::decode(const std::filesystem::path& path) {
    SF_INFO info{};
    std::unique_ptr<SNDFILE, decltype(&sf_close)> file(sf_open(path.string().c_str(), SFM_READ, &info), sf_close);
    if (!file) throw std::runtime_error("Audio " + path.string() + ": " + sf_strerror(nullptr));
    if (info.frames <= 0 || info.channels < 1 || info.channels > 8 || info.samplerate <= 0
        || info.frames > 100000000)
        throw std::runtime_error("Unsupported audio dimensions: " + path.string());
    Clip clip{std::vector<float>(static_cast<std::size_t>(info.frames) * info.channels),
              info.channels, info.samplerate};
    const auto frames = sf_readf_float(file.get(), clip.samples.data(), info.frames);
    if (frames <= 0) throw std::runtime_error("Empty audio: " + path.string());
    clip.samples.resize(static_cast<std::size_t>(frames) * info.channels);
    return clip;
}
Audio::Audio(std::filesystem::path path, bool mute) : assets_(std::move(path)) {
    if (mute) return;
    if (SDL_InitSubSystem(SDL_INIT_AUDIO) < 0) {
        std::cerr << "Audio disabled: " << SDL_GetError() << '\n'; return;
    }
    // Decode before opening the device so constructor failure cannot leave a callback running.
    for (const auto& name : effects) clips_.emplace(name, decode(assets_ / "audio" / name));
    SDL_AudioSpec wanted{};
    wanted.freq = 48000; wanted.format = AUDIO_F32SYS; wanted.channels = 2; wanted.samples = 1024;
    wanted.callback = callback; wanted.userdata = this;
    device_ = SDL_OpenAudioDevice(nullptr, 0, &wanted, nullptr, 0);
    if (!device_) { std::cerr << "Audio disabled: " << SDL_GetError() << '\n'; return; }
    SDL_PauseAudioDevice(device_, 0);
}
Audio::~Audio() { if (device_) SDL_CloseAudioDevice(device_); }
void Audio::play(const std::string& name, double volume) {
    if (!device_) return;
    const auto found = clips_.find(name);
    if (found == clips_.end()) return;
    SDL_LockAudioDevice(device_);
    auto* voice = &voices_[next_voice_++ % voices_.size()];
    for (auto& candidate : voices_) if (!candidate.clip) { voice = &candidate; break; }
    *voice = {&found->second, 0, volume, false};
    SDL_UnlockAudioDevice(device_);
}
void Audio::music(const std::string& name) {
    if (!device_) return;
    auto clip = std::make_unique<Clip>(decode(assets_ / "audio" / name));
    SDL_LockAudioDevice(device_);
    music_.swap(clip);
    music_voice_ = {music_.get(), 0, .2, true};
    SDL_UnlockAudioDevice(device_);
}
void Audio::pause(bool paused) {
    if (!device_) return;
    SDL_LockAudioDevice(device_);
    paused_ = paused;
    SDL_UnlockAudioDevice(device_);
}
void Audio::stop_effects() {
    if (!device_) return;
    SDL_LockAudioDevice(device_);
    for (auto& voice : voices_) voice.clip = nullptr;
    SDL_UnlockAudioDevice(device_);
}
void Audio::mix(Voice& voice, float* output, int frames) {
    if (!voice.clip) return;
    const auto& clip = *voice.clip;
    const auto count = clip.samples.size() / static_cast<std::size_t>(clip.channels);
    for (int i = 0; i < frames; ++i) {
        auto index = static_cast<std::size_t>(voice.frame);
        if (index >= count) {
            if (!voice.loop) { voice.clip = nullptr; break; }
            voice.frame = std::fmod(voice.frame, static_cast<double>(count));
            index = static_cast<std::size_t>(voice.frame);
        }
        const auto next = index + 1 < count ? index + 1 : voice.loop ? 0 : index;
        const float fraction = static_cast<float>(voice.frame - static_cast<double>(index));
        for (int channel = 0; channel < 2; ++channel) {
            const auto ch = static_cast<std::size_t>(std::min(channel, clip.channels - 1));
            const auto channels = static_cast<std::size_t>(clip.channels);
            const float a = clip.samples[index * channels + ch];
            const float b = clip.samples[next * channels + ch];
            output[i * 2 + channel] += (a + (b - a) * fraction) * static_cast<float>(voice.gain);
        }
        voice.frame += static_cast<double>(clip.rate) / 48000;
    }
}
void Audio::callback(void* userdata, Uint8* stream, int length) {
    auto& self = *static_cast<Audio*>(userdata);
    std::memset(stream, 0, static_cast<std::size_t>(length));
    if (self.paused_) return;
    auto* output = reinterpret_cast<float*>(stream);
    const int frames = length / static_cast<int>(sizeof(float) * 2);
    mix(self.music_voice_, output, frames);
    for (auto& voice : self.voices_) mix(voice, output, frames);
    for (int i = 0; i < frames * 2; ++i) output[i] = std::clamp(output[i], -1.0F, 1.0F);
}
void Audio::verify(const std::filesystem::path& assets) {
    for (const auto& name : effects) decode(assets / "audio" / name);
    for (const auto& name : music_names()) decode(assets / "audio" / name);
}
} // namespace dv
