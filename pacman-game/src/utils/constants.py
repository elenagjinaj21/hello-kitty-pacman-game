"""Game constants and configuration values."""
from pathlib import Path

# Game paths
GAME_ROOT = Path(__file__).parent.parent.parent
ASSETS_DIR = GAME_ROOT / "assets"
CONFIG_DIR = GAME_ROOT / "config"

# Window settings
WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 1100
FPS = 60

# Colors (Pastel Pink Kawaii Theme)
COLOR_BACKGROUND = (255, 240, 245)  # Misty rose
COLOR_WALL = (255, 192, 203)  # Light pink
COLOR_WALL_DARK = (255, 182, 193)  # Lighter pink
COLOR_CORRIDOR = (255, 250, 250)  # Snow
COLOR_TEXT = (220, 105, 150)  # Pale violet red
COLOR_TEXT_DARK = (200, 65, 130)  # Dark pink
COLOR_HIGHLIGHT = (255, 215, 215)  # Pink highlight
COLOR_SHADOW = (255, 160, 170)  # Darker pink

# Pacgum settings
PACGUM_VALUE = 10
PACGUM_SIZE = 2

# Super-pacgum settings
SUPER_PACGUM_VALUE = 50
SUPER_PACGUM_SIZE = 5
SUPER_PACGUM_DURATION = 8.0  # Seconds

# Ghost settings
GHOST_SPEED = 3.0  # Maze cells per second
GHOST_SIZE = 20
GHOST_VALUES = [200, 400, 800, 1600]  # Points for eating ghosts in sequence
GHOST_RESPAWN_TIME = 5.0  # Seconds
GHOST_NAMES = ["Miyako", "Kiki", "Lala", "Roru"]  # Cute ghost names
GHOST_COLORS = [
    (255, 80, 120),   # Red-pink
    (80, 140, 255),   # Blue
    (80, 200, 140),   # Green
    (255, 190, 70),   # Gold
]

# Player settings
PLAYER_SPEED = 5.0  # Maze cells per second
PLAYER_START_LIVES = 3
PLAYER_SIZE = 18

# Level settings
NUM_LEVELS = 15
LEVEL_TIME_LIMIT = 90  # Seconds
FIRST_LEVEL_SEED = 42
MAZE_EXTRA_CONNECTION_CHANCE = 0.35

# Scoring
PACGUM_POINTS = 10
SUPER_PACGUM_POINTS = 50

# Directions
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)
DIRECTIONS = [UP, DOWN, LEFT, RIGHT]
DIRECTION_MAP = {
    "UP": UP,
    "DOWN": DOWN,
    "LEFT": LEFT,
    "RIGHT": RIGHT,
}

# Maze rendering
MAZE_WIDTH = 25
MAZE_HEIGHT = 25
CELL_SIZE = 40
CORRIDOR_THRESHOLD = 14  # Bit value for open corridor

# Cheat mode keys
CHEAT_INVINCIBLE = "i"
CHEAT_SKIP_LEVEL = "n"
CHEAT_FREEZE_GHOSTS = "f"
CHEAT_EXTRA_LIVES = "l"
CHEAT_SPEED_UP = "t"

# Game states
STATE_MENU = "menu"
STATE_PLAYING = "playing"
STATE_PAUSED = "paused"
STATE_LEVEL_COMPLETE = "level_complete"
STATE_GAME_OVER = "game_over"
STATE_VICTORY = "victory"

# Highscore file
HIGHSCORE_FILE = CONFIG_DIR / "highscores.json"
MAX_HIGHSCORES = 10

# UI Sizes
UI_PADDING = 20
UI_FONT_SIZE_LARGE = 48
UI_FONT_SIZE_MEDIUM = 32
UI_FONT_SIZE_SMALL = 24
UI_BUTTON_WIDTH = 200
UI_BUTTON_HEIGHT = 50
