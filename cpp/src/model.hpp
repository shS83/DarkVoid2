#pragma once

#include <algorithm>
#include <array>
#include <cmath>
#include <cstdint>
#include <random>
#include <string>
#include <unordered_map>
#include <vector>

namespace dv {
constexpr double width = 1920, height = 1080;
constexpr double pi = 3.14159265358979323846;
struct Vec {
    double x = 0, y = 0;
    Vec operator+(Vec b) const { return {x + b.x, y + b.y}; }
    Vec operator-(Vec b) const { return {x - b.x, y - b.y}; }
    Vec operator*(double s) const { return {x * s, y * s}; }
    Vec& operator+=(Vec b) { x += b.x; y += b.y; return *this; }
    double length() const { return std::hypot(x, y); }
    Vec unit(Vec fallback = {0, -1}) const;
    Vec rotated(double degrees) const;
};
inline Vec lerp(Vec a, Vec b, double t) { return a + (b - a) * t; }
struct Rect {
    double x = 0, y = 0, w = 0, h = 0;
    bool overlaps(Rect b) const;
    Rect inset(double n) const;
};
struct Color { std::uint8_t r = 255, g = 255, b = 255, a = 255; };
struct Mask {
    int w = 0, h = 0;
    std::vector<std::uint8_t> alpha;
    Rect visible_bounds;
};
using Catalog = std::unordered_map<std::string, Mask>;
struct Body {
    std::string image;
    Vec pos, size;
    double angle = 0; // Clockwise screen-space degrees.
    Rect bounds() const;
};
bool opaque_at(const Body& body, Vec point, const Catalog& catalog);
bool mask_collision(const Body& a, const Body& b, const Catalog& catalog);
Rect visible_bounds(const Body& body, const Catalog& catalog);
Vec image_size(const Catalog& catalog, const std::string& image, double scale = 1);

enum class Power { Health, Speed, Spread, Laser, Cannon, Shield, Piercing };
const std::array<std::string, 7> power_names{
    "health", "speed", "spread", "laser", "cannon", "shield", "piercing"};
enum class Weapon { Main, Rail, Vulcan, Tracer, Orb, Pellet, Blue };
enum class Phase { Space, BossExplosion, EarthEnter, ShipGrow, ShipToEarth,
                   FadeOut, TerrainFadeIn, Terrain };
struct Input {
    Vec move, aim{width / 2, 0};
    bool fire = false, vulcan = false, rail = false, focus = false;
};
struct Player {
    Body body;
    int lives = 3, shields = 0, vulcan_side = -1, rounds = 0;
    double intro = 0, scale = 0.65, invincible = 0, fire_timer = 0;
    double power_timer = 0, rail_timer = 0, shield_timer = 0;
    double heat = 0, vulcan_timer = 0, sound_timer = 0, thruster_timer = 0;
    bool alive = true, intro_active = true, overheated = false;
    bool spread = false, fast = false, rapid = false, piercing = false;
    bool godmode = false, vulcan_unlimited = false;
    bool arsenal_unlimited = false;
    std::string killer = "No-one";
};
struct Bullet {
    Body body;
    Vec velocity;
    Weapon kind = Weapon::Main;
    std::string owner;
    double radius = 6, trail_timer = 0;
    bool friendly = false, piercing = false, dead = false;
};
struct Enemy {
    Body body;
    Vec velocity{0, 80};
    std::string name;
    Weapon weapon = Weapon::Orb;
    int hp = 5, max_hp = 5, rank = 1, pattern = 0;
    double shot = 0.8, delay = 1, secondary = 1.2, phase_time = 0;
    double flash = 0, spin = 0, thruster = 0;
    bool boss = false, rock = false, entering = false, dead = false;
};
struct Pickup {
    Body body;
    Power kind = Power::Health;
    double life = 15, glitter = 0;
    bool dead = false;
};
struct Particle {
    Vec pos, velocity;
    Color color;
    double life = 0, max_life = 0, size = 2, gravity = 0, drag = 1;
};
struct Explosion { Vec pos; double age = 0; bool boss = false; };
struct Star { Vec pos; double speed = 0, size = 1; };
struct OceanChunk { int image = 1; double y = 0, h = 0; };
struct SoundEvent { std::string name; double volume = 1; };

class Model {
public:
    explicit Model(const Catalog& catalog, std::uint32_t seed = std::random_device{}());
    void reset(int initial_stage = 1, bool skip_intro = false);
    void warp_to_stage(int target);
    std::string execute_console_command(const std::string& command);
    void grant_unlimited_arsenal();
    void update(double dt, const Input& input);
    void apply_power(Power kind);
    bool activate_shield();
    void hit_player(const std::string& killer);
    void spawn_enemy();
    void spawn_rock();
    void spawn_boss();
    void damage_enemy(std::size_t index, int damage);
    void end_game(bool won);
    void collide();
    double random(double a, double b);
    int random_int(int a, int b);

    const Catalog& catalog;
    Player player;
    std::vector<Enemy> enemies;
    std::vector<Bullet> bullets;
    std::vector<Pickup> pickups;
    std::vector<Particle> particles;
    std::vector<Explosion> explosions;
    std::vector<Star> stars;
    std::vector<OceanChunk> ocean;
    std::vector<SoundEvent> sounds;
    std::vector<std::string> messages;
    Phase phase = Phase::Space;
    int stage = 1, score = 0;
    double elapsed = 0, stage_time = 0, banner = 2.4, ending_time = 0;
    double phase_time = 0, fade = 0;
    Vec earth, transition_start;
    bool game_over = false, victory = false, paused = false;
    bool boss_present() const;
    bool transitioning() const { return phase != Phase::Space && phase != Phase::Terrain; }
private:
    std::mt19937 rng_;
    double enemy_timer_ = 0, enemy_delay_ = 1.5;
    double rock_timer_ = 0, rock_delay_ = 5;
    int ocean_index_ = 1;
    void update_player(double dt, const Input& input);
    void update_enemies(double dt);
    void update_effects(double dt);
    void update_transition(double dt);
    void update_ocean(double dt);
    void reset_powers();
    void start_transition();
    void boss_pattern(Enemy& enemy);
    void enemy_bullet(Vec pos, Vec velocity, Weapon kind, const std::string& owner);
    void player_bullet(Vec pos, Vec velocity, Weapon kind);
    void emit(Vec pos, Vec velocity, Color color, double life, double size,
              double drag = 0.93, double gravity = 0);
    void burst(Vec pos, int count, Color color = {});
    void clear_combat();
};
} // namespace dv
