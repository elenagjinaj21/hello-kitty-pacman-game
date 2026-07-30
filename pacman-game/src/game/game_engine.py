"""Main game engine."""

from typing import Any, Dict, List, Optional

from utils.constants import (
    STATE_MENU, STATE_PLAYING, STATE_PAUSED,
    STATE_LEVEL_COMPLETE, STATE_GAME_OVER, STATE_VICTORY,
    SUPER_PACGUM_DURATION,
)
from game.player import Direction, Player
from game.ghost import Ghost, GhostState
from game.level_manager import Level, LevelManager
from utils.highscore import HighscoreManager


class GameEngine:
    """Main game engine coordinating all game logic."""

    def __init__(self) -> None:
        """Initialize the game engine."""
        self.state = STATE_MENU
        self.player = Player(12, 12)  # Center position
        self.level_manager = LevelManager()
        self.highscore_manager = HighscoreManager()

        # Cheat mode
        self.cheat_mode_enabled = False
        self.cheat_freeze_ghosts = False
        self.cheat_speed_boost = 1.0
        self._normal_player_speed = self.player.speed

    def start_new_game(self) -> None:
        """Start a new game."""
        self.player = Player(12, 12)
        self.level_manager.start_game(self.player)
        self.state = STATE_PLAYING
        self.cheat_mode_enabled = False
        self.cheat_freeze_ghosts = False
        self.cheat_speed_boost = 1.0
        self._normal_player_speed = self.player.speed

    def update(self, delta_time: float) -> None:
        """
        Update game state.

        Args:
            delta_time: Time elapsed in seconds
        """
        if self.state != STATE_PLAYING:
            return

        level = self.level_manager.get_current_level()
        if not level:
            return

        # Update level
        level.update(delta_time)

        # Capture pre-move positions so we can detect a player/ghost swap
        # (otherwise a ghost and the player can exchange cells in one frame
        # and never be seen sharing a cell).
        player_prev = self.player.get_position()
        ghosts = level.ghost_manager.get_ghosts()
        ghost_prev = [ghost.get_position() for ghost in ghosts]

        # Move player
        self._update_player(level, delta_time)

        # Move ghosts
        self._update_ghosts(level, delta_time)

        # Check for collectibles
        self._check_collectibles(level)

        # Check for ghost collisions
        self._check_ghost_collisions(level, player_prev, ghosts, ghost_prev)

        # Check win/lose conditions
        self._check_level_completion(level)

    def _update_player(self, level: Level, delta_time: float) -> None:
        """Update player movement."""
        self.player.try_move(
            lambda x, y, dx, dy: level.maze.can_move(x, y, dx, dy),
            delta_time
        )

    def _update_ghosts(self, level: Level, delta_time: float) -> None:
        """Update ghost movement."""
        if self.cheat_freeze_ghosts:
            return

        for ghost in level.ghost_manager.get_ghosts():
            if ghost.respawn_time > 0:
                continue

            direction = ghost.get_move_direction(
                self.player.get_position(),
                lambda x, y, dx, dy: level.maze.can_move(x, y, dx, dy)
            )
            ghost.last_direction = direction
            ghost.try_move(
                lambda x, y, dx, dy: level.maze.can_move(x, y, dx, dy),
                delta_time
            )

    def _check_collectibles(self, level: Level) -> None:
        """Check for collectible pickups."""
        player_x, player_y = self.player.get_position()
        collected, points, is_power_up = level.collectible_manager.collect_at_position(
            player_x, player_y
        )

        if collected:
            self.player.add_score(points)

            if is_power_up:
                level.ghost_manager.make_all_frightened(SUPER_PACGUM_DURATION)

    def _check_ghost_collisions(
        self,
        level: Level,
        player_prev: Optional[tuple[int, int]] = None,
        ghosts: Optional[list[Ghost]] = None,
        ghost_prev: Optional[list[tuple[int, int]]] = None,
    ) -> None:
        """Check for collisions with ghosts, including same-frame swaps."""
        player_pos = self.player.get_position()
        ghost = level.ghost_manager.check_collision(player_pos)

        # If nobody shares the player's cell, check whether a ghost and the
        # player swapped cells this frame (they passed through each other).
        if ghost is None and ghosts is not None and ghost_prev is not None:
            for moved_ghost, previous in zip(ghosts, ghost_prev):
                if moved_ghost.state == GhostState.RESPAWN:
                    continue
                if (
                    moved_ghost.get_position() == player_prev
                    and previous == player_pos
                ):
                    ghost = moved_ghost
                    break

        if ghost:
            if ghost.is_frightened():
                # Eat the ghost
                points = level.ghost_manager.eat_ghost(ghost)
                self.player.add_score(points)
            else:
                # Ghost eats player
                if not self.player.is_invincible:
                    self.player.lose_life()
                    self.player.reset_position()
                    # Send the ghosts back to their corners too, otherwise a
                    # ghost sitting on the respawn cell drains the remaining
                    # lives across consecutive frames.
                    level.ghost_manager.reset_all()

                    if self.player.is_game_over():
                        self.state = STATE_GAME_OVER

    def _check_level_completion(self, level: Level) -> None:
        """Check if level is complete or time is up."""
        if level.is_complete():
            self.state = STATE_LEVEL_COMPLETE
        elif level.is_time_up():
            self.state = STATE_GAME_OVER

    def set_player_direction(self, direction: Direction) -> None:
        """
        Set player movement direction.

        Args:
            direction: Movement direction
        """
        self.player.set_direction(direction)

    def pause_game(self) -> None:
        """Pause the game."""
        if self.state == STATE_PLAYING:
            self.state = STATE_PAUSED

    def resume_game(self) -> None:
        """Resume the game."""
        if self.state == STATE_PAUSED:
            self.state = STATE_PLAYING

    def next_level(self) -> None:
        """Progress to the next level."""
        if self.level_manager.next_level():
            self.state = STATE_PLAYING
        else:
            self.state = STATE_VICTORY

    def return_to_menu(self) -> None:
        """Return to main menu."""
        self.state = STATE_MENU

    def is_playing(self) -> bool:
        """Check if game is currently playing."""
        return self.state == STATE_PLAYING

    def is_paused(self) -> bool:
        """Check if game is paused."""
        return self.state == STATE_PAUSED

    def is_game_over(self) -> bool:
        """Check if game is over."""
        return self.state == STATE_GAME_OVER

    def is_level_complete(self) -> bool:
        """Check if current level is complete."""
        return self.state == STATE_LEVEL_COMPLETE

    def is_victory(self) -> bool:
        """Check if game is won."""
        return self.state == STATE_VICTORY

    def get_state(self) -> str:
        """Get current game state."""
        return self.state

    # Cheat mode methods
    def toggle_cheat_invincible(self) -> None:
        """Toggle invincibility."""
        self.player.set_invincible(not self.player.is_invincible)

    def toggle_cheat_freeze_ghosts(self) -> None:
        """Toggle ghost freeze."""
        self.cheat_freeze_ghosts = not self.cheat_freeze_ghosts

    def activate_cheat_skip_level(self) -> None:
        """Skip to next level."""
        level = self.level_manager.get_current_level()
        if level:
            level.collectible_manager.collectibles.clear()
            self.state = STATE_LEVEL_COMPLETE

    def activate_cheat_extra_lives(self) -> None:
        """Add extra lives."""
        self.player.gain_life()

    def toggle_cheat_speed_up(self) -> None:
        """Toggle speed boost."""
        if self.cheat_speed_boost == 1.0:
            self.cheat_speed_boost = 2.0
        else:
            self.cheat_speed_boost = 1.0
        self.player.set_speed(self._normal_player_speed * self.cheat_speed_boost)

    def get_current_level_number(self) -> int:
        """Get current level number."""
        return self.level_manager.get_current_level_number()

    def get_player_score(self) -> int:
        """Get player score."""
        return self.player.get_score()

    def get_player_lives(self) -> int:
        """Get player lives."""
        return self.player.get_lives()

    def get_time_remaining(self) -> int:
        """Get time remaining in current level."""
        level = self.level_manager.get_current_level()
        if level:
            return level.get_time_remaining()
        return 0

    def get_current_level(self) -> Optional[Level]:
        """Get current level object."""
        return self.level_manager.get_current_level()

    def get_player(self) -> Player:
        """Get player object."""
        return self.player

    def save_highscore(self, name: str) -> int:
        """
        Save a highscore.

        Args:
            name: Player name

        Returns:
            Position in highscores (1-indexed)
        """
        level = self.level_manager.get_current_level_number()
        return self.highscore_manager.add_score(name, self.player.score, level)

    def get_highscores(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get top highscores."""
        return self.highscore_manager.get_top_scores(limit)

    def is_highscore(self, score: int) -> bool:
        """Check if score qualifies for highscores."""
        return self.highscore_manager.is_highscore(score)
