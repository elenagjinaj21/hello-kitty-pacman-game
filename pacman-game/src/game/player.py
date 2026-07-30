"""Player character logic."""

from typing import Callable, Optional, Tuple
from enum import Enum

from utils.constants import (
    PLAYER_SPEED, PLAYER_START_LIVES,
    UP, DOWN, LEFT, RIGHT,
)

MoveChecker = Callable[[int, int, int, int], bool]


class Direction(Enum):
    """Player movement directions."""
    UP = UP
    DOWN = DOWN
    LEFT = LEFT
    RIGHT = RIGHT
    NONE = (0, 0)


class Player:
    """Manages the player character."""

    def __init__(self, x: int, y: int):
        """
        Initialize the player.

        Args:
            x: Starting X position in maze cells
            y: Starting Y position in maze cells
        """
        self.x = x
        self.y = y
        self.start_x = x
        self.start_y = y
        self.lives = PLAYER_START_LIVES
        self.score = 0
        self.current_direction = Direction.NONE
        self.next_direction = Direction.NONE
        self.speed = PLAYER_SPEED
        self.is_invincible = False
        self.move_progress = 0.0  # For smooth movement between cells

    def reset_position(self) -> None:
        """Reset player to spawn position."""
        self.x = self.start_x
        self.y = self.start_y
        self.move_progress = 0.0
        self.current_direction = Direction.NONE
        self.next_direction = Direction.NONE

    def set_spawn_position(self, x: int, y: int) -> None:
        """Set and move to the player's spawn position."""
        self.start_x = x
        self.start_y = y
        self.reset_position()

    def add_score(self, points: int) -> None:
        """Add points to the score."""
        self.score += points

    def set_score(self, score: int) -> None:
        """Set the score directly."""
        self.score = score

    def get_score(self) -> int:
        """Get the current score."""
        return self.score

    def set_direction(self, direction: Direction) -> None:
        """Set the desired direction for the next move."""
        self.next_direction = direction
        if self.current_direction == Direction.NONE:
            self.move_progress = max(self.move_progress, 1.0 / max(self.speed, 0.1))

    def get_position(self) -> Tuple[int, int]:
        """Get the current position."""
        return (self.x, self.y)

    def get_direction(self) -> Direction:
        """Get the current movement direction."""
        return self.current_direction

    def try_move(
        self,
        can_move_func: MoveChecker,
        delta_time: Optional[float] = None,
    ) -> bool:
        """
        Attempt to move in the current direction.

        Args:
            can_move_func: Function that takes (x, y, dx, dy) and returns bool
            delta_time: Optional elapsed time in seconds for speed-limited movement

        Returns:
            True if movement was successful
        """
        move_interval = 0.0
        if delta_time is not None:
            self.move_progress += delta_time
            move_interval = 1.0 / max(self.speed, 0.1)
            if self.move_progress < move_interval:
                return False

        # Try to move in the next desired direction first
        if self.next_direction != Direction.NONE:
            dx, dy = self.next_direction.value
            if can_move_func(self.x, self.y, dx, dy):
                self.x += dx
                self.y += dy
                self.current_direction = self.next_direction
                self.next_direction = Direction.NONE
                if delta_time is not None:
                    self.move_progress = max(0.0, self.move_progress - move_interval)
                return True

        # Try to continue in current direction
        if self.current_direction != Direction.NONE:
            dx, dy = self.current_direction.value
            if can_move_func(self.x, self.y, dx, dy):
                self.x += dx
                self.y += dy
                if delta_time is not None:
                    self.move_progress = max(0.0, self.move_progress - move_interval)
                return True
            self.current_direction = Direction.NONE

        if delta_time is not None:
            self.move_progress = min(self.move_progress, move_interval)
        return False

    def lose_life(self) -> None:
        """Lose a life."""
        if not self.is_invincible:
            self.lives -= 1

    def gain_life(self) -> None:
        """Gain an extra life."""
        self.lives += 1

    def set_invincible(self, invincible: bool) -> None:
        """Set invincibility state."""
        self.is_invincible = invincible

    def is_game_over(self) -> bool:
        """Check if the player has lost all lives."""
        return self.lives <= 0

    def get_lives(self) -> int:
        """Get remaining lives."""
        return self.lives

    def set_speed(self, speed: float) -> None:
        """Set movement speed multiplier."""
        self.speed = speed

    def __repr__(self) -> str:
        return f"Player({self.x}, {self.y}, Lives: {self.lives}, Score: {self.score})"
