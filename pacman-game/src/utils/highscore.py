"""Highscore management system."""

import json
import re
from datetime import datetime
from typing import Any, Dict, List

from utils import constants

NAME_PATTERN = re.compile(r"[^A-Za-z0-9 ]+")


class HighscoreManager:
    """Manages game highscores and persistent storage."""

    def __init__(self) -> None:
        """Initialize the highscore manager."""
        self.highscores: List[Dict[str, Any]] = []
        self.load_highscores()

    def load_highscores(self) -> None:
        """Load highscores from file."""
        if not constants.HIGHSCORE_FILE.exists():
            self.highscores = []
            return
        try:
            with open(constants.HIGHSCORE_FILE, "r", encoding="utf-8") as score_file:
                loaded = json.load(score_file)
        except (json.JSONDecodeError, OSError):
            self.highscores = []
            return
        if not isinstance(loaded, list):
            self.highscores = []
            return
        valid_scores = [
            score for score in loaded
            if isinstance(score, dict)
            and isinstance(score.get("name"), str)
            and isinstance(score.get("score"), int)
            and isinstance(score.get("level"), int)
            and score["score"] >= 0
        ]
        valid_scores.sort(key=lambda x: int(x["score"]), reverse=True)
        self.highscores = valid_scores[:constants.MAX_HIGHSCORES]

    def save_highscores(self) -> None:
        """Save highscores to file."""
        try:
            constants.HIGHSCORE_FILE.parent.mkdir(parents=True, exist_ok=True)
            with open(
                constants.HIGHSCORE_FILE,
                "w",
                encoding="utf-8",
            ) as score_file:
                json.dump(self.highscores, score_file, indent=2)
        except OSError as exc:
            print(f"Highscore warning: could not save scores: {exc}")

    def _sanitize_name(self, name: str) -> str:
        """Return a max-10-character alphanumeric/spaces player name."""
        clean_name = NAME_PATTERN.sub("", name).strip()[:10]
        return clean_name or "PLAYER"

    def add_score(self, name: str, score: int, level: int) -> int:
        """
        Add a new score to the highscore list.

        Args:
            name: Player name
            score: Final score
            level: Level reached

        Returns:
            Position in highscore list (1-indexed), or -1 if not in top 10
        """
        clean_score = max(0, int(score))
        clean_level = max(1, int(level))
        entry: Dict[str, Any] = {
            "name": self._sanitize_name(name),
            "score": clean_score,
            "level": clean_level,
            "date": datetime.now().isoformat()
        }

        self.highscores.append(entry)
        self.highscores.sort(key=lambda x: x["score"], reverse=True)
        self.highscores = self.highscores[:constants.MAX_HIGHSCORES]

        position = next(
            (i for i, h in enumerate(self.highscores) if h == entry),
            -1
        )
        self.save_highscores()

        return position + 1 if position >= 0 else -1

    def get_top_scores(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get top scores."""
        return self.highscores[:limit]

    def is_highscore(self, score: int) -> bool:
        """Check if score qualifies for highscores."""
        if len(self.highscores) < constants.MAX_HIGHSCORES:
            return True
        return bool(score > self.highscores[-1]["score"])

    def clear_highscores(self) -> None:
        """Clear all highscores (for testing)."""
        self.highscores = []
        self.save_highscores()
