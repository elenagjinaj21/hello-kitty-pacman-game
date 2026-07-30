"""Level management and progression."""

from typing import Optional
from utils.constants import NUM_LEVELS, LEVEL_TIME_LIMIT, MAZE_WIDTH, MAZE_HEIGHT
from game.maze_adapter import MazeAdapter
from game.collectible import CollectibleManager
from game.ghost import GhostManager
from game.player import Player


class Level:
    """Represents a single game level."""

    def __init__(self, level_number: int):
        """
        Initialize a level.

        Args:
            level_number: Level number (1-indexed)
        """
        self.level_number = level_number
        self.maze = MazeAdapter(
            width=MAZE_WIDTH,
            height=MAZE_HEIGHT,
            level=level_number,
        )
        self.collectible_manager = CollectibleManager()
        self.ghost_manager = GhostManager()
        self.time_remaining: float = LEVEL_TIME_LIMIT
        self.completed = False

        # Initialize level content
        self._initialize_collectibles()
        self._initialize_ghosts()

    def _initialize_collectibles(self) -> None:
        """Initialize collectibles for this level."""
        corridors = self.maze.get_all_corridors()
        corners = self.maze.get_corner_positions()
        self.collectible_manager.create_level_collectibles(corridors, corners)

    def _initialize_ghosts(self) -> None:
        """Initialize ghosts for this level."""
        corners = self.maze.get_corner_positions()
        self.ghost_manager.create_ghosts(corners)

    def update(self, delta_time: float) -> None:
        """
        Update level state.

        Args:
            delta_time: Time elapsed in seconds
        """
        self.time_remaining -= delta_time
        if self.time_remaining < 0:
            self.time_remaining = 0

        # Update ghost states
        self.ghost_manager.update_frightened(delta_time)
        self.ghost_manager.update_respawn(delta_time)

    def is_complete(self) -> bool:
        """Check if level is complete (all collectibles collected)."""
        return self.collectible_manager.is_level_complete()

    def is_time_up(self) -> bool:
        """Check if time limit is reached."""
        return self.time_remaining <= 0

    def get_time_remaining(self) -> int:
        """Get remaining time in seconds."""
        return max(0, int(self.time_remaining))

    def __repr__(self) -> str:
        return f"Level({self.level_number}, time_left={self.get_time_remaining()}s)"


class LevelManager:
    """Manages level progression."""

    def __init__(self) -> None:
        """Initialize level manager."""
        self.current_level_number = 1
        self.current_level: Optional[Level] = None
        self.player: Optional[Player] = None

    def start_game(self, player: Player) -> None:
        """
        Start a new game.

        Args:
            player: The player object
        """
        self.player = player
        self.current_level_number = 1
        self.load_level(1)

    def load_level(self, level_number: int) -> bool:
        """
        Load a specific level.

        Args:
            level_number: Level to load (1-indexed)

        Returns:
            True if successful
        """
        if level_number < 1 or level_number > NUM_LEVELS:
            return False

        self.current_level_number = level_number
        self.current_level = Level(level_number)

        if self.player:
            # Reset player spawn to the nearest playable maze center.
            center_x, center_y = self.current_level.maze.get_center_position()
            self.player.set_spawn_position(center_x, center_y)

        return True

    def next_level(self) -> bool:
        """
        Progress to the next level.

        Returns:
            True if there's a next level
        """
        if self.current_level_number < NUM_LEVELS:
            return self.load_level(self.current_level_number + 1)
        return False

    def get_current_level(self) -> Optional[Level]:
        """Get the current level."""
        return self.current_level

    def get_current_level_number(self) -> int:
        """Get the current level number."""
        return self.current_level_number

    def is_final_level(self) -> bool:
        """Check if current level is the final level."""
        return self.current_level_number >= NUM_LEVELS

    def is_game_complete(self) -> bool:
        """Check if all levels have been completed."""
        return bool(
            self.is_final_level()
            and self.current_level
            and self.current_level.is_complete()
        )

    def update(self, delta_time: float) -> None:
        """
        Update level state.

        Args:
            delta_time: Time elapsed in seconds
        """
        if self.current_level:
            self.current_level.update(delta_time)
