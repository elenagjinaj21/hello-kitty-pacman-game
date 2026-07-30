"""Asset loading and management."""

import json
from typing import Any, Dict, Optional, Tuple

from utils.constants import CONFIG_DIR


class AssetManager:
    """Manages game assets (sprites, fonts, sounds, colors)."""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize asset manager."""
        self.sprites: Dict[str, Any] = {}
        self.fonts: Dict[str, Any] = {}
        self.sounds: Dict[str, Any] = {}
        self.config: Dict[str, Any] = config or self._load_default_config()

    def _load_default_config(self) -> Dict[str, Any]:
        """Load default game configuration from JSON, with a safe fallback."""
        config_file = CONFIG_DIR / "game_config.json"
        if not config_file.exists():
            return self._get_default_config()
        try:
            with open(config_file, "r", encoding="utf-8") as config_handle:
                loaded = json.load(config_handle)
        except (json.JSONDecodeError, OSError):
            return self._get_default_config()
        return loaded if isinstance(loaded, dict) else self._get_default_config()

    def _get_default_config(self) -> Dict[str, Any]:
        """Get default game configuration."""
        return {
            "game_title": "Hello Kitty Maze Game",
            "colors": {
                "primary": [255, 192, 203],
                "secondary": [255, 182, 193],
                "accent": [220, 105, 150],
                "text": [200, 65, 130],
                "background": [255, 240, 245],
            },
            "debug": False,
        }

    def get_color(self, color_name: str) -> Tuple[int, int, int]:
        """Get a color by name."""
        colors = self.config.get("colors", {})
        color = colors.get(color_name, [255, 255, 255])
        return tuple(color)

    def load_sprite(self, sprite_name: str) -> Optional[Any]:
        """Load a sprite."""
        if sprite_name in self.sprites:
            return self.sprites[sprite_name]
        return None

    def load_font(self, font_name: str) -> Optional[Any]:
        """Load a font."""
        if font_name in self.fonts:
            return self.fonts[font_name]
        return None

    def load_sound(self, sound_name: str) -> Optional[Any]:
        """Load a sound."""
        if sound_name in self.sounds:
            return self.sounds[sound_name]
        return None

    def register_sprite(self, sprite_name: str, sprite_data: Any) -> None:
        """Register a sprite."""
        self.sprites[sprite_name] = sprite_data

    def register_font(self, font_name: str, font_data: Any) -> None:
        """Register a font."""
        self.fonts[font_name] = font_data

    def register_sound(self, sound_name: str, sound_data: Any) -> None:
        """Register a sound."""
        self.sounds[sound_name] = sound_data

    def save_config(self) -> None:
        """Save configuration to file."""
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        config_file = CONFIG_DIR / "game_config.json"
        with open(config_file, 'w') as f:
            json.dump(self.config, f, indent=2)
