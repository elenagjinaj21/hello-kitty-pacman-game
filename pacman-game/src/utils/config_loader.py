"""Runtime configuration loading and validation."""

import json
import re
import sys
from pathlib import Path
from typing import Any, Callable, Dict

from utils import constants


class ConfigError(ValueError):
    """Raised when the game configuration is invalid."""


def _warn(message: str) -> None:
    """Print a clear non-fatal configuration warning."""
    print(f"Config warning: {message}", file=sys.stderr)


def _strip_json_comments(text: str) -> str:
    """Remove supported full-line and inline comments from JSON text."""
    cleaned_lines = []
    in_block = False
    for raw_line in text.splitlines():
        line = raw_line
        if in_block:
            end = line.find("*/")
            if end == -1:
                continue
            line = line[end + 2:]
            in_block = False
        while "/*" in line:
            start = line.find("/*")
            end = line.find("*/", start + 2)
            if end == -1:
                line = line[:start]
                in_block = True
                break
            line = line[:start] + line[end + 2:]
        stripped = line.lstrip()
        if stripped.startswith("#") or stripped.startswith("//"):
            continue
        line = re.sub(r"(?<!:)//.*$", "", line)
        cleaned_lines.append(line)
    return "\n".join(cleaned_lines)


def _require_section(config: Dict[str, Any], section: str) -> Dict[str, Any]:
    """Return a config section, validating that it is a dictionary."""
    value = config.get(section, {})
    if not isinstance(value, dict):
        _warn(f"{section} must be an object; using defaults for that section")
        return {}
    return value


def _as_color(value: Any, path: str) -> tuple[int, int, int]:
    """Return an RGB tuple from a config list."""
    if not isinstance(value, list) or len(value) != 3:
        raise ValueError(f"{path} must be a list of 3 RGB integers")
    if not all(isinstance(channel, int) for channel in value):
        raise ValueError(f"{path} must contain only integers")
    if not all(0 <= channel <= 255 for channel in value):
        raise ValueError(f"{path} color channels must be between 0 and 255")
    return tuple(value)


def _set_if_present(
    config: Dict[str, Any],
    key: str,
    constant_name: str,
    caster: Callable[[Any], Any],
    validator: Callable[[Any], bool],
    description: str,
) -> None:
    """Set a constant from a config value when present and valid."""
    if key not in config:
        return
    path = f"{constant_name} ({key})"
    try:
        value = caster(config[key])
    except (TypeError, ValueError):
        _warn(f"{path} must be {description}; keeping default")
        return
    if not validator(value):
        _warn(f"{path} must be {description}; keeping default")
        return
    setattr(constants, constant_name, value)


def _positive_int(value: Any) -> int:
    """Convert a value to int without accepting booleans."""
    if isinstance(value, bool):
        raise ValueError
    return int(value)


def _positive_float(value: Any) -> float:
    """Convert a value to float without accepting booleans."""
    if isinstance(value, bool):
        raise ValueError
    return float(value)


def _is_positive(value: Any) -> bool:
    """Return whether a numeric value is positive."""
    return bool(value > 0)


def _is_non_negative(value: Any) -> bool:
    """Return whether a numeric value is non-negative."""
    return bool(value >= 0)


def _apply_levels(levels: Any) -> None:
    """Apply the optional subject-style level array."""
    if not isinstance(levels, list) or not levels:
        _warn("levels must be a non-empty array; keeping default level count")
        return

    valid_levels = 0
    first_level = levels[0]
    if isinstance(first_level, dict):
        _set_if_present(
            first_level,
            "width",
            "MAZE_WIDTH",
            _positive_int,
            _is_positive,
            "a positive integer",
        )
        _set_if_present(
            first_level,
            "height",
            "MAZE_HEIGHT",
            _positive_int,
            _is_positive,
            "a positive integer",
        )

    for level in levels:
        if isinstance(level, dict):
            valid_levels += 1
    if valid_levels >= 10:
        constants.NUM_LEVELS = valid_levels
    else:
        _warn("at least 10 valid levels are required; keeping default level count")


def _apply_points_per_ghost(value: Any) -> None:
    """Apply the subject-style ghost score base value."""
    try:
        points = _positive_int(value)
    except (TypeError, ValueError):
        _warn("points_per_ghost must be a non-negative integer; keeping default")
        return
    if points < 0:
        _warn("points_per_ghost must be a non-negative integer; keeping default")
        return
    constants.GHOST_VALUES = [points, points * 2, points * 4, points * 8]


def _load_json_with_comments(path: Path) -> Dict[str, Any]:
    """Load a JSON object while tolerating supported comments."""
    with open(path, "r", encoding="utf-8") as config_file:
        config_text = _strip_json_comments(config_file.read())
    loaded = json.loads(config_text)
    if not isinstance(loaded, dict):
        raise ConfigError("Config root must be an object")
    return loaded


def apply_config(config_path: str) -> Dict[str, Any]:
    """
    Load a JSON config file and apply supported values to game constants.

    Args:
        config_path: Path to the JSON configuration file.

    Returns:
        Parsed configuration dictionary.
    """
    path = Path(config_path)
    if path.suffix.lower() != ".json":
        _warn(f"{config_path} is not a .json file; trying to load it anyway")
    try:
        config = _load_json_with_comments(path)
    except FileNotFoundError:
        _warn(f"Config file not found: {config_path}; using built-in defaults")
        return {}
    except (json.JSONDecodeError, OSError, ConfigError) as exc:
        _warn(f"Could not load {config_path}: {exc}; using built-in defaults")
        return {}

    game = _require_section(config, "game")
    maze = _require_section(config, "maze")
    player = _require_section(config, "player")
    ghosts = _require_section(config, "ghosts")
    collectibles = _require_section(config, "collectibles")
    ui = _require_section(config, "ui")
    colors = _require_section(config, "colors")

    positive_int = (_positive_int, _is_positive, "a positive integer")
    positive_float = (_positive_float, _is_positive, "a positive number")
    non_negative_int = (_positive_int, _is_non_negative, "a non-negative integer")
    non_negative_float = (
        _positive_float,
        _is_non_negative,
        "a non-negative number",
    )

    for key, constant_name, caster, validator, description in [
        ("lives", "PLAYER_START_LIVES", *positive_int),
        ("pacgum", "PACGUM_VALUE", *non_negative_int),
        ("points_per_pacgum", "PACGUM_VALUE", *non_negative_int),
        ("points_per_super_pacgum", "SUPER_PACGUM_VALUE", *non_negative_int),
        ("level_max_time", "LEVEL_TIME_LIMIT", *positive_float),
        ("seed", "FIRST_LEVEL_SEED", *non_negative_int),
        ("width", "WINDOW_WIDTH", *positive_int),
        ("height", "WINDOW_HEIGHT", *positive_int),
        ("fps", "FPS", *positive_int),
        ("num_levels", "NUM_LEVELS", *positive_int),
        ("level_time_limit", "LEVEL_TIME_LIMIT", *positive_float),
        ("first_level_seed", "FIRST_LEVEL_SEED", *non_negative_int),
    ]:
        _set_if_present(game, key, constant_name, caster, validator, description)

    for key, constant_name, caster, validator, description in [
        ("lives", "PLAYER_START_LIVES", *positive_int),
        ("pacgum", "PACGUM_VALUE", *non_negative_int),
        ("points_per_pacgum", "PACGUM_VALUE", *non_negative_int),
        ("points_per_super_pacgum", "SUPER_PACGUM_VALUE", *non_negative_int),
        ("level_max_time", "LEVEL_TIME_LIMIT", *positive_float),
        ("seed", "FIRST_LEVEL_SEED", *non_negative_int),
    ]:
        _set_if_present(config, key, constant_name, caster, validator, description)
    if "level" in config:
        _apply_levels(config["level"])
    if "points_per_ghost" in config:
        _apply_points_per_ghost(config["points_per_ghost"])

    for key, constant_name in [
        ("width", "MAZE_WIDTH"),
        ("height", "MAZE_HEIGHT"),
        ("cell_size", "CELL_SIZE"),
    ]:
        _set_if_present(
            maze,
            key,
            constant_name,
            *positive_int,
        )

    for key, constant_name, caster, validator, description in [
        ("start_lives", "PLAYER_START_LIVES", *positive_int),
        ("speed", "PLAYER_SPEED", *positive_float),
        ("size", "PLAYER_SIZE", *positive_int),
    ]:
        _set_if_present(player, key, constant_name, caster, validator, description)

    _set_if_present(
        config,
        "highscore_filename",
        "HIGHSCORE_FILE",
        lambda value: constants.GAME_ROOT / str(value),
        lambda value: str(value).endswith(".json"),
        "a JSON filename",
    )

    for key, constant_name, caster, validator, description in [
        ("speed", "GHOST_SPEED", *positive_float),
        ("size", "GHOST_SIZE", *positive_int),
        ("respawn_time", "GHOST_RESPAWN_TIME", *non_negative_float),
    ]:
        _set_if_present(ghosts, key, constant_name, caster, validator, description)
    if "names" in ghosts:
        if not isinstance(ghosts["names"], list) or len(ghosts["names"]) < 4:
            _warn("ghosts.names must contain at least 4 names; keeping default")
        else:
            constants.GHOST_NAMES = [str(name) for name in ghosts["names"][:4]]

    for key, constant_name, caster, validator, description in [
        ("pacgum_value", "PACGUM_VALUE", *non_negative_int),
        ("super_pacgum_value", "SUPER_PACGUM_VALUE", *non_negative_int),
        ("super_pacgum_duration", "SUPER_PACGUM_DURATION", *positive_float),
    ]:
        _set_if_present(
            collectibles,
            key,
            constant_name,
            caster,
            validator,
            description,
        )

    for key, constant_name, caster, validator, description in [
        ("padding", "UI_PADDING", *non_negative_int),
        ("font_size_large", "UI_FONT_SIZE_LARGE", *positive_int),
        ("font_size_medium", "UI_FONT_SIZE_MEDIUM", *positive_int),
        ("font_size_small", "UI_FONT_SIZE_SMALL", *positive_int),
        ("button_width", "UI_BUTTON_WIDTH", *positive_int),
        ("button_height", "UI_BUTTON_HEIGHT", *positive_int),
    ]:
        _set_if_present(ui, key, constant_name, caster, validator, description)

    color_map = {
        "background": "COLOR_BACKGROUND",
        "wall_light": "COLOR_WALL",
        "wall_dark": "COLOR_WALL_DARK",
        "corridor": "COLOR_CORRIDOR",
        "accent": "COLOR_TEXT",
        "text": "COLOR_TEXT_DARK",
        "highlight": "COLOR_HIGHLIGHT",
    }
    for config_key, constant_name in color_map.items():
        if config_key in colors:
            try:
                color = _as_color(colors[config_key], f"colors.{config_key}")
            except ValueError as exc:
                _warn(f"{exc}; keeping default")
            else:
                setattr(constants, constant_name, color)

    return config
