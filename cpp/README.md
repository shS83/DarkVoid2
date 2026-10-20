# Dark Void 2 — C++ edition

A standalone C++17 port of the active Python game (`main.py` → `darkvoid2.py`
→ `game.py`). The original Python source, launch scripts, dependencies, assets
and high-score files are preserved. All C++ source and build output live here.
The executable does not launch or embed Python.

Updated against the Python fixes in commit `ddc029d` (2026-10-01), including
the last-stage ending fix, developer console, animated rainbow controls and
restart flow. This edition also adds the requested `iddqd` / `idkfa` cheats.

## Build and play

From the repository root:

```sh
cmake -S cpp -B cpp/build -DCMAKE_BUILD_TYPE=Release
cmake --build cpp/build --parallel
./cpp/build/darkvoid2
```

Alternatively, `./cpp/run.sh` builds and starts the game. Subsequent runs can
launch the executable directly.

Required development libraries:

- C++17 compiler, CMake 3.16+, pkg-config
- SDL2 2.0.18+ and SDL2_ttf
- libpng 1.6+ for the existing PNG images
- libsndfile 1.1+ with MP3/Vorbis support for WAV, OGG and MP3 audio
- nlohmann/json 3.2+ for high scores

The port uses libraries already installed on the development machine;
SDL2_image and SDL2_mixer are not required. The build currently uses pkg-config.
Linux is the tested platform; Windows/macOS builds have not been verified.

The game retains its 1920 × 1080 logical playfield. It starts in a resizable
1280 × 720 window with proportional scaling and letterboxing. Mouse aiming is
converted to logical coordinates. Use `--fullscreen` or F11 for fullscreen.

Assets are read from the original `../assets` directory, recorded at configure
time. You can launch the executable from another working directory. To move it
to another machine, place `assets/` beside the executable or pass
`--assets /path/to/DarkVoid2/assets`. The required shared libraries must also be
available on the destination machine.

## Controls

| Action | Input |
| --- | --- |
| Start | Space or Enter after the title introduction |
| Controls | F1; Space or F1 returns |
| Movement | WASD or arrows |
| Main gun / spread gun | Space or left mouse button |
| Mouse-aimed Vulcan cannon | Right or middle mouse button |
| Railgun after cannon pickup | Left Ctrl |
| Activate a shield charge | Left Alt |
| Focus movement | Left Shift |
| Pause / resume | Pause or P |
| Toggle fullscreen | F11 |
| Developer console | § or backtick (the physical key below Escape) |
| Quit | Escape or window close |
| Save high-score name | Enter |
| Restart after high-score entry | Space |

## Cheats and developer console

Type these codes directly while playing, with the console closed. Enter is
not required. Each code displays a message that zooms in and fades out over
three seconds.

| Code | Effect |
| --- | --- |
| `iddqd` | Toggle invulnerability; displays `GOD MODE: ON` or `GOD MODE: OFF` |
| `idkfa` | Displays `SAY HELLO TO MY LITTLE FRIEND`; grants a permanent Left Ctrl railgun, a Vulcan that never overheats, and triple shot for the main gun |

The `idkfa` weapons survive power-up expiry, other pickups and stage changes.
Starting a new game resets all cheats and developer powers. Codes entered in
the console, controls, pause or high-score entry do not trigger gameplay cheats.

Press § / backtick to open the console, then type a command and press Enter:

| Command | Effect |
| --- | --- |
| `help` | List commands and power-up types |
| `god` | Toggle invulnerability |
| `impulse 9` | Grant one random timed weapon upgrade and a permanently cool Vulcan |
| `warp 1` … `warp 5` | Jump to a stage, keeping score and inventory; revive a dead player |
| `powerup shield` | Grant shield charges; also accepts `speed`, `health`, `spread`, `laser`, `cannon`, `piercing` |
| `clear` | Clear console output |

The console slides up over the lower half of the screen with a half-opacity
background. Gameplay and audio pause until it finishes closing. Escape closes
the console; an existing manual pause stays in effect. Up/Down recall commands;
Page Up/Down and the mouse wheel scroll output. The console also reports
collected power-ups and shield charges.

After death or victory, the game reaches high-score entry in every stage.
Space starts a fresh game directly from the score table, retaining the ship
introduction without replaying the opening title sequence.

## Port coverage

| Python feature | C++ implementation |
| --- | --- |
| Wallpaper, title animation, Japanese subtitle, controls | `main.cpp`, `view.cpp` |
| Ship introduction, movement, focus and invulnerability | `model.cpp` |
| Main/spread/rapid fire, railgun, aimed Vulcan, heat and tracers | `model.cpp` |
| All seven power-ups, timed shield and pickup glitter | `model.cpp`, `view.cpp` |
| Eleven enemy selections, three enemy projectile types, rotating asteroids | `model.cpp` |
| Five named bosses, original HP and rank-scaled attack formulas | `model.cpp` |
| Radial, spiral, moving lane gap, pincer and desperation patterns | `model.cpp` |
| Stars, thrusters, debris, muzzle effects, 31-frame explosions | `model.cpp`, `view.cpp` |
| Fourth-boss explosion, Earth approach, curved ship flight and terrain fade | `model.cpp` |
| Three scrolling ocean chunks and fifth-stage boss | `model.cpp`, `view.cpp` |
| Score, lives, shields, heat, boss health, pause and ending overlays | `view.cpp` |
| Death/victory, name entry, top ten and restart | `main.cpp`, `scores.cpp` |
| Original sound effects and thirteen music choices | `runtime.cpp` |
| Animated console, history, commands, pause and stage warp | `console.cpp`, `commands.cpp`, `session.cpp` |
| Rainbow instructions, zooming/fading cheat messages | `runtime.cpp`, `view.cpp` |
| Typed cheats and permanent weapon upgrades | `session.cpp`, `model.cpp` |

Unused alternate engines and experiments under Python `core/`, `magic/` and
unused `systems/` modules remain in Python. They are not dependencies of the
active game's C++ port.

This is a gameplay port, not a pixel-identical emulation of Pygame. Text
rasterization, particle shapes, glow blending, random sequences and audio mixing
can differ. Player shots use alpha-mask collisions against scaled/rotated
images; enemy shots retain their small circular hit radii. Image-mask sampling
uses nearest source pixels instead of Pygame's transformed surface masks.
Transient particles are capped at 20,000.

### Ending behavior and port differences

- Speed pickups change movement speed; focus temporarily overrides it.
- Vulcan cooldown is decremented once per update and fires at its configured
  0.05-second interval. Heat uses the configured 0.65/s rise and 0.35/s cooling,
  without the Python version's extra shot-dependent increment.
- Death and victory advance to high scores in the terrain stage as well as
  space. Winning ends at stage five, awards the boss reward once and stops all
  combat. These paths follow the updated Python ending fixes.
- The terrain boss timer is reset explicitly after the Earth transition.
- A fatal hit records the actual bullet/enemy owner.
- Normal random drops include piercing, which was otherwise only reachable
  through Python debug spawning.
- Pause resumes music at its previous position; Escape closes without silently
  inserting a score under a hard-coded name.
- High scores display all ten stored entries.

These changes leave the Python implementation untouched.

## Scores

C++ scores use SDL's per-user application directory, independent of the Python
table. On Linux the usual location is:

```text
~/.local/share/shS83/DarkVoid2-cpp/highscores.json
```

`XDG_DATA_HOME` can change that base directory. Use `--scores /path/to/file.json`
to choose another table. Saving uses a temporary file followed by a rename.
The existing Python `highscores.json` is not imported or modified automatically.

## Verification and development

```sh
ctest --test-dir cpp/build --output-on-failure
./cpp/build/darkvoid2 --headless --verify-assets
./cpp/build/darkvoid2 --headless --stage 5 --boss --frames 480 --mute \
    --screenshot /tmp/darkvoid2-terrain.png
```

CTest covers movement, intro, all weapons, cooldown/heat, power expiry, shield
charges, invulnerability, alpha/rotation collision, scoring, every boss phase,
the Earth transition, terrain boss spawning, death/victory and JSON persistence.
SDL event tests cover console commands/history, pause and text-input routing,
both cheats, permanent weapons, the final-boss collision → name entry → saved
stage-five score → fresh-game sequence, and revival through warp.
Rendering checks cover the moving rainbow, cheat zoom/fade and console opacity;
audio runs through SDL's dummy device. Scene screenshots and isolated test
scores are in `build/test-artifacts/`. Tests do not use the player's score table.
The model tests use synthetic opaque masks plus explicit transparency tests;
the rendering tests use the real image files.

The asset verifier decodes all required images and all audio tracks. Dummy
audio tests do not verify the audible balance on a physical sound device.

For AddressSanitizer and UndefinedBehaviorSanitizer:

```sh
cmake -S cpp -B cpp/build/sanitize -DCMAKE_BUILD_TYPE=Debug -DDARKVOID_SANITIZERS=ON
cmake --build cpp/build/sanitize --parallel
ctest --test-dir cpp/build/sanitize --output-on-failure
```

`--help` lists all options, including `--start`, `--skip-intro`, `--stage 1..5`,
`--boss`, `--seed`, `--frames`, `--headless` and `--screenshot`.
Headless runs use fixed 1/60-second updates without waiting for real time.
They run for 120 frames by default.

The renderer uses [SDL2](https://wiki.libsdl.org/SDL2/FrontPage), font rendering
uses SDL2_ttf, PNG decoding uses [libpng](https://www.libpng.org/pub/png/libpng.html),
and audio decoding uses [libsndfile](https://libsndfile.github.io/libsndfile/api.html).
