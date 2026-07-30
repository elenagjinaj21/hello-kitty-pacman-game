"""Regression tests for subject-specific config and highscore requirements."""

import json
import sys
import tempfile
from pathlib import Path

SRC_PATH = Path(__file__).parent.parent / "src"
if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

import unittest

from utils import constants
from utils.config_loader import apply_config
from utils.highscore import HighscoreManager


class TestConfigAndHighscores(unittest.TestCase):
    """Test robust config parsing and highscore validation."""

    def setUp(self):
        """Keep global constants isolated between tests."""
        self.original_values = {
            "PLAYER_START_LIVES": constants.PLAYER_START_LIVES,
            "PACGUM_VALUE": constants.PACGUM_VALUE,
            "SUPER_PACGUM_VALUE": constants.SUPER_PACGUM_VALUE,
            "GHOST_VALUES": list(constants.GHOST_VALUES),
            "LEVEL_TIME_LIMIT": constants.LEVEL_TIME_LIMIT,
            "FIRST_LEVEL_SEED": constants.FIRST_LEVEL_SEED,
            "HIGHSCORE_FILE": constants.HIGHSCORE_FILE,
        }

    def tearDown(self):
        """Restore global constants."""
        for name, value in self.original_values.items():
            setattr(constants, name, value)

    def test_config_accepts_comments_and_subject_keys(self):
        """Subject-style keys and # comments are accepted."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "review.json"
            config_path.write_text(
                """
                # peer review can edit this file
                {
                  "lives": 4,
                  "points_per_pacgum": 12,
                  "points_per_super_pacgum": 60,
                  "points_per_ghost": 250,
                  "seed": 7,
                  "level_max_time": 45
                }
                """,
                encoding="utf-8",
            )

            apply_config(str(config_path))

        self.assertEqual(constants.PLAYER_START_LIVES, 4)
        self.assertEqual(constants.PACGUM_VALUE, 12)
        self.assertEqual(constants.SUPER_PACGUM_VALUE, 60)
        self.assertEqual(constants.GHOST_VALUES[0], 250)
        self.assertEqual(constants.FIRST_LEVEL_SEED, 7)
        self.assertEqual(constants.LEVEL_TIME_LIMIT, 45)

    def test_bad_config_values_keep_defaults(self):
        """Invalid values warn and keep safe defaults."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "bad.json"
            config_path.write_text(
                json.dumps({"lives": -5, "game": {"fps": "nope"}}),
                encoding="utf-8",
            )

            apply_config(str(config_path))

        self.assertEqual(
            constants.PLAYER_START_LIVES,
            self.original_values["PLAYER_START_LIVES"],
        )

    def test_highscore_sanitizes_name_and_uses_custom_path(self):
        """Highscores keep top ten and sanitize player names."""
        with tempfile.TemporaryDirectory() as temp_dir:
            constants.HIGHSCORE_FILE = Path(temp_dir) / "scores.json"
            manager = HighscoreManager()

            position = manager.add_score("A!@ very long name", 100, 2)

            self.assertEqual(position, 1)
            self.assertEqual(manager.get_top_scores()[0]["name"], "A very lon")
            self.assertTrue(constants.HIGHSCORE_FILE.exists())


if __name__ == "__main__":
    unittest.main()
