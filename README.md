*This activity has been created as part of the 42 curriculum by egjinaj, shajdar*

# 🎀 Hello Kitty Maze Game 🎀

## Description

This is a Hello Kitty themed maze reimagining of the classic Pac-Man game, built with Python and Pygame. The goal is to guide Hello Kitty through procedurally generated mazes, collecting all pacgums across 15 progressively challenging levels while avoiding ghost enemies.

Key features include:

- **Procedurally Generated Mazes** — Each level generates a unique maze using the A-Maze-ing package, with the "42" logo embedded in the center
- **Progressive Difficulty** — 15 levels of increasing challenge; Level 1 uses a fixed seed for consistency
- **Ghost AI** — Enemies with multiple behaviors: chasing, scattering, and fleeing when frightened by power pellets
- **Collectibles** — Pacgums (dots) and super-pacgums (power pellets) that trigger a frightened ghost state
- **Highscore System** — Persistent top-10 leaderboard with player names, scores, levels reached, and dates
- **Cheat Mode** — Developer tools for peer review: invincibility, level skip, ghost freeze, extra lives, speed boost
- **Pastel Pink Aesthetic** — Hekawaiillo Kitty-inspired characters and UI throughout

---

## Instructions

### Requirements

- Python 3.10 or higher
- pygame >= 2.1.0

### Installation

```bash
# Clone the repository
git clone <repository-url>
cd pacman-game

# Install dependencies
make install
```

### Running the Game

```bash
python3 pac-man.py config/game_config.json
```

Or via Makefile shortcut:

```bash
make run
```

Or via the installed console script:

```bash
hello-kitty-maze
```

### Controls

**Movement** — Arrow Keys or WASD (Up/W, Down/S, Left/A, Right/D)

**In-Game** — Space: Pause/Resume · M: Main Menu · Q: Quit

**Main Menu** — Space: Start · H: Highscores · I: Instructions · Q: Quit

### Cheat Mode (for peer review)

During gameplay:

- **I** — Toggle invincibility (ghosts cannot eat you)
- **N** — Skip to next level immediately
- **F** — Freeze all ghosts
- **L** — Add an extra life
- **T** — Toggle 2× speed boost

### Running Tests

```bash
make test
# or directly:
python3 -m unittest discover -s tests -v
```

---

## Configuration

### Config File Structure

Configuration is stored in `config/game_config.json`. The loader accepts standard JSON plus comment lines beginning with `#` or `//`. Invalid or missing values trigger a warning and fall back to safe defaults — the game will not crash on malformed config. Unknown keys are silently ignored.

```json
{
  "game_title": "🎀 Hello Kitty Maze 🎀",
  "game": {
    "width": 1200,
    "height": 900,
    "fps": 60,
    "num_levels": 15,
    "level_time_limit": 90,
    "first_level_seed": 42
  },
  "maze": {
    "width": 20,
    "height": 20,
    "cell_size": 32
  },
  "player": {
    "start_lives": 3,
    "speed": 5.0,
    "size": 18
  },
  "ghosts": {
    "count": 4,
    "speed": 3.0,
    "size": 20
  },
  "collectibles": {
    "pacgum_value": 10,
    "super_pacgum_value": 50,
    "super_pacgum_duration": 8.0
  }
}
```

### Default Values

| Key | Default | Description |
|---|---|---|
| `game.width` / `game.height` | 1200 × 900 | Window size in pixels |
| `game.fps` | 60 | Target frame rate |
| `game.num_levels` | 15 | Total number of levels |
| `game.level_time_limit` | 90 | Seconds per level |
| `game.first_level_seed` | 42 | Seed for Level 1 maze |
| `maze.width` / `maze.height` | 25 × 25 | Maze dimensions in cells |
| `maze.cell_size` | 30 | Cell size in pixels |
| `player.start_lives` | 3 | Starting lives |
| `player.speed` | 5.0 | Player speed (cells/sec) |
| `ghosts.count` | 4 | Number of ghosts |
| `ghosts.speed` | 3.0 | Ghost speed (cells/sec) |
| Highscore file | `config/highscores.json` | Persistent score storage |

---

## Highscore System

### How It Works

Highscores are stored in `config/highscores.json` as a sorted JSON list of the top 10 entries. Each entry contains:

- Player name (max 10 alphanumeric characters/spaces)
- Final score (non-negative integer)
- Level reached
- Date of achievement

When a game session ends (win or loss), the player is prompted to enter their name. If the score qualifies for the top 10, it is automatically written to the file. The file is created automatically if it does not exist, and scores persist between sessions.

### Why This Approach

A flat JSON file was chosen over a database for simplicity and portability — no external dependencies are needed, the file is human-readable, and it is trivially included in the repository. A top-10 cap keeps the file small and the leaderboard competitive. Sorting on write (rather than on read) means display is always O(1).

---

## Maze Generation

### How the A-Maze-ing Package Is Used

The external `mazegenerator` package is used **without modification**. Integration is handled entirely through an adapter layer:

**`src/game/maze_adapter.py`** wraps `MazeGenerator` and provides:

- Game-specific collision detection methods (wall checks in all four directions)
- Conversion of bit-encoded cell values into playable corridor data
- A fallback maze builder that activates if the external generator raises an error or does not return within the expected time — the adapter logs a warning and builds a simple but fully playable maze instead of crashing

**Generator configuration used in-game:**

- Depth-first search procedural generation
- Seed-based reproduction (`first_level_seed = 42` for Level 1; random seeds for Levels 2–15)
- Imperfect maze mode (`perfect=False`) to produce Pac-Man-style looping corridors
- Automatic "42" logo embedding in the maze center

**Bit-encoding scheme (per cell):**

```
Bit 1 (value 1)  — Wall to North
Bit 2 (value 2)  — Wall to East
Bit 4 (value 4)  — Wall to South
Bit 8 (value 8)  — Wall to West
All bits set (15) — Completely enclosed cell
```

---

## Implementation

### Technical Summary

The game is a modular Python application with clear separation between game logic, rendering, and utilities.

**Game Logic Layer (`src/game/`)**

- `game_engine.py` — Central orchestrator; owns the game loop and coordinates all subsystems
- `player.py` — Character state, movement, and collision response
- `ghost.py` — Per-ghost AI state machine (chase, scatter, frightened, respawn)
- `collectible.py` — Item placement, collection detection, and effect triggering
- `level_manager.py` — Level sequencing, win/loss detection, and difficulty scaling
- `maze_adapter.py` — Wraps the external MazeGenerator; provides wall queries and fallback logic

**Rendering Layer (`src/ui/`)**

- `menu.py` — All Pygame rendering: game world, HUD, menus, and screens
- `assets.py` — Asset loading, caching, and configuration; generates geometric sprites at runtime

**Utility Layer (`src/utils/`)**

- `constants.py` — Derived constants and computed values
- `highscore.py` — JSON-backed persistent score storage with atomic writes

**Entry Point**

`pac-man.py` (at repo root) — Parses the config path argument, initialises `GameApplication`, and starts the main loop.

### Module Relationships

```
GameApplication (main loop)
├── GameEngine (orchestrator)
│   ├── Player
│   ├── LevelManager
│   │   └── Level
│   │       ├── MazeAdapter  ←→  mazegenerator (external package)
│   │       ├── CollectibleManager
│   │       └── GhostManager
│   └── HighscoreManager
├── GameDisplay
└── AssetManager
```

---

## General Software Architecture

### High-Level Overview

```
┌─────────────────────────────────────────────┐
│         Application Layer                   │
│         GameApplication (main loop,         │
│         config loading, event dispatch)     │
└────────────┬────────────────┬───────────────┘
             │                │
┌────────────▼──────┐  ┌──────▼───────────────┐
│  Game Logic Layer │  │  Presentation Layer  │
│  GameEngine       │  │  GameDisplay         │
│  ├─ Player        │  │  ├─ Menu systems     │
│  ├─ GhostManager  │  │  ├─ HUD              │
│  ├─ Collectibles  │  │  └─ AssetManager     │
│  ├─ LevelManager  │  └──────────────────────┘
│  └─ Highscores    │
└────────────┬──────┘
             │
┌────────────▼──────────────────┐
│  Game World Layer             │
│  MazeAdapter                  │
│  └─ mazegenerator (external)  │
└───────────────────────────────┘
```

### Design Patterns

- **Adapter Pattern** — `MazeAdapter` decouples game code from the external `MazeGenerator` API; all maze queries go through the adapter, so the external package could be swapped without touching game logic
- **Manager Pattern** — `GhostManager`, `CollectibleManager`, and `LevelManager` each own a category of entities, reducing coupling in `GameEngine`
- **State Pattern** — The game cycles through explicit states: `Menu`, `Playing`, `Paused`, `GameOver`, `Victory`; each state determines which input handlers and render paths are active
- **Observer Pattern** — Input events and collision events are dispatched to registered handlers rather than polled in a monolithic loop

### Code Quality Choices

- Type hints throughout for IDE support and self-documentation
- Docstrings on all public modules, classes, and functions
- No modification of the external maze generator package
- Geometric sprite rendering (no external art assets required to run)

---

## Project Management

You're editing the README directly in VS Code — that's the raw markdown view, not a preview. The tables are actually fine, the issue is you need to paste the new Project Management section into your README replacing the old one.
Share your current README file and I'll give you the exact full file with the fix already in it, ready to save.
Or, paste this block directly into your README replacing everything from ## Project Management onwards:
markdown## Project Management

### Team

| Member | Role |
|--------|------|
| Seva | Maze adapter, player movement, collectibles, HUD, cheat mode, highscore manager |
| Elena | Game engine, ghost AI, level progression, config loader, menus & screens, README |

### Timeline

| Phase | Days | Description | Owner |
|-------|------|-------------|-------|
| 1 — Setup & planning | Day 1 | Git repo setup, requirement review, module ownership split | Both |
| 2 — Architecture & maze integration | Days 2–3 | MazeAdapter, game engine skeleton, maze bit-encoding verification | Seva / Elena |
| 3 — Core gameplay | Days 4–6 | Player, ghost AI, collectibles, level progression, highscore manager, config loader | Seva / Elena |
| 4 — UI & polish | Days 7–8 | All menus, HUD, highscore screen, name entry, cheat mode | Elena / Seva |
| 5 — Testing, docs & submission | Days 9–10 | Unit tests, manual playthrough, README, final cleanup and push | Both

### Development Approach

The project was developed in five sequential phases:

1. **Architecture Design** — Module structure, dependency graph, external integration points
2. **Core Systems** — Game engine, state machine, player and ghost foundations, maze adapter
3. **Game Features** — Collectibles, scoring, ghost AI behaviours, level progression
4. **User Interface** — Pygame renderer, menu stack, HUD, all screens (pause, game over, victory, highscores, name entry)
5. **Polish & Testing** — Cheat mode, persistent highscores, bug fixes, peer-review checklist


---

## Resources

### Documentation & References

- [Pygame Documentation](https://www.pygame.org/docs/)
- [Pac-Man Game Design — Wikipedia](https://en.wikipedia.org/wiki/Pac-Man)
- [Understanding Pac-Man Ghost Behavior](https://gameinternals.com/understanding-pac-man-ghost-behavior)
- [Maze Generation Algorithms](https://en.wikipedia.org/wiki/Maze_generation_algorithm)
- [Ghost AI Pathfinding — GameDev Stack Exchange](https://gamedev.stackexchange.com/questions/53023/how-do-ghosts-find-the-player-in-pac-man)
- [Python `json` module](https://docs.python.org/3/library/json.html)

### AI Usage

AI assistance (Claude) was used for the following tasks:

- **Configuration management** — Designing the JSON config schema and the tolerant loader (comment stripping, default fallbacks)
- **Documentation** — Drafting and structuring this README and in-code docstrings

All AI-generated code was reviewed, tested, and integrated manually. No AI was used for the maze generation logic itself (handled entirely by the provided external package).

---

## Directory Structure

```
pacman-game/
├── pac-man.py                          # Entry point
├── config/
│   ├── game_config.json                # Default configuration
│   └── highscores.json                 # Persistent highscores
├── src/
│   ├── game/
│   │   ├── game_engine.py
│   │   ├── player.py
│   │   ├── ghost.py
│   │   ├── collectible.py
│   │   ├── level_manager.py
│   │   └── maze_adapter.py
│   ├── ui/
│   │   ├── menu.py
│   │   └── assets.py
│   └── utils/
│       ├── constants.py
│       └── highscore.py
├── assets/
│   ├── sprites/
│   └── fonts/
├── tests/
├── docs/
│   └── project_management/
├── mazegenerator-00001-py3-none-any/   # External package (unmodified)
├── requirements.txt
├── setup.py
├── Makefile
└── README.md
```
