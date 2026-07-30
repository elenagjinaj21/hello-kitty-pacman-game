"""Ghost AI and logic."""

import random
from typing import Any, Callable, List, Optional, Tuple
from enum import Enum

from utils.constants import (
    GHOST_SPEED, GHOST_VALUES, GHOST_RESPAWN_TIME,
    GHOST_NAMES, GHOST_COLORS,
    DIRECTIONS,
)

MoveChecker = Callable[[int, int, int, int], bool]


class GhostState(Enum):
    """Ghost behavioral states."""
    CHASE = "chase"
    SCATTER = "scatter"
    FRIGHTENED = "frightened"
    RESPAWN = "respawn"


class Ghost:
    """Represents a ghost character."""

    def __init__(
        self,
        ghost_id: int,
        start_x: int,
        start_y: int,
        color: Optional[Tuple[int, int, int]] = None,
    ):
        """
        Initialize a ghost.

        Args:
            ghost_id: Ghost identifier (0-3)
            start_x: Starting X position in maze cells
            start_y: Starting Y position in maze cells
            color: RGB color tuple
        """
        self.ghost_id = ghost_id
        self.x = start_x
        self.y = start_y
        self.start_x = start_x
        self.start_y = start_y
        self.color = color or GHOST_COLORS[ghost_id]
        self.name = GHOST_NAMES[ghost_id]
        self.speed = GHOST_SPEED
        self.state = GhostState.CHASE
        self.frightened_time = 0.0
        self.respawn_time = 0.0
        self.last_direction = (0, 0)
        self.move_progress = 1.0 / max(self.speed, 0.1)

    def reset(self) -> None:
        """Reset ghost to starting position."""
        self.x = self.start_x
        self.y = self.start_y
        self.state = GhostState.CHASE
        self.frightened_time = 0.0
        self.respawn_time = 0.0
        self.move_progress = 1.0 / max(self.speed, 0.1)

    def get_position(self) -> Tuple[int, int]:
        """Get current position."""
        return (self.x, self.y)

    def set_position(self, x: int, y: int) -> None:
        """Set position."""
        self.x = x
        self.y = y

    def make_frightened(self, duration: float) -> None:
        """Make the ghost frightened for a duration."""
        self.state = GhostState.FRIGHTENED
        self.frightened_time = duration

    def is_frightened(self) -> bool:
        """Check if ghost is currently frightened."""
        return self.state == GhostState.FRIGHTENED

    def respawn(self) -> None:
        """Start respawning process."""
        self.state = GhostState.RESPAWN
        self.respawn_time = GHOST_RESPAWN_TIME

    def update_frightened_time(self, delta_time: float) -> bool:
        """
        Update frightened duration.

        Args:
            delta_time: Time elapsed in seconds

        Returns:
            True if frightened status ended
        """
        if self.state == GhostState.FRIGHTENED:
            self.frightened_time -= delta_time
            if self.frightened_time <= 0:
                self.state = GhostState.CHASE
                self.frightened_time = 0.0
                return True
        return False

    def update_respawn_time(self, delta_time: float) -> bool:
        """
        Update respawn duration.

        Args:
            delta_time: Time elapsed in seconds

        Returns:
            True if respawn completed
        """
        if self.state == GhostState.RESPAWN:
            self.respawn_time -= delta_time
            if self.respawn_time <= 0:
                self.reset()
                return True
        return False

    def get_move_direction(
        self,
        player_pos: Tuple[int, int],
        can_move_func: MoveChecker,
        get_corridors_func: Optional[Any] = None,
    ) -> Tuple[int, int]:
        """
        Get the next movement direction based on AI behavior.

        Args:
            player_pos: Player position (x, y)
            can_move_func: Function to check if movement is valid
            get_corridors_func: Optional function to get valid corridors

        Returns:
            Direction tuple (dx, dy)
        """
        if self.state == GhostState.FRIGHTENED:
            return self._get_scared_direction(can_move_func)
        elif self.state == GhostState.CHASE:
            return self._get_chase_direction(player_pos, can_move_func)
        else:
            return (0, 0)

    def _get_chase_direction(
        self,
        player_pos: Tuple[int, int],
        can_move_func: MoveChecker,
    ) -> Tuple[int, int]:
        """Get direction when chasing the player."""
        valid_moves = self._get_non_reverse_moves(can_move_func)

        if not valid_moves:
            return (0, 0)

        # Simple chase: move toward player
        player_x, player_y = player_pos
        best_move = valid_moves[0]
        best_distance = (
            abs(self.x + best_move[0] - player_x)
            + abs(self.y + best_move[1] - player_y)
        )

        for dx, dy in valid_moves[1:]:
            distance = abs(self.x + dx - player_x) + abs(self.y + dy - player_y)
            if distance < best_distance:
                best_distance = distance
                best_move = (dx, dy)

        self.last_direction = best_move
        return best_move

    def _get_scared_direction(self, can_move_func: MoveChecker) -> Tuple[int, int]:
        """Get direction when frightened (running away)."""
        valid_moves = self._get_non_reverse_moves(can_move_func)

        if valid_moves:
            move = random.choice(valid_moves)
            self.last_direction = move
            return move

        return (0, 0)

    def _get_non_reverse_moves(
        self,
        can_move_func: MoveChecker,
    ) -> List[Tuple[int, int]]:
        """Return legal moves, allowing a U-turn only at dead ends."""
        valid_moves = [
            (dx, dy)
            for dx, dy in DIRECTIONS
            if can_move_func(self.x, self.y, dx, dy)
        ]
        if not valid_moves or self.last_direction == (0, 0):
            return valid_moves

        reverse = (-self.last_direction[0], -self.last_direction[1])
        preferred_moves = [move for move in valid_moves if move != reverse]
        return preferred_moves or valid_moves

    def try_move(
        self,
        can_move_func: MoveChecker,
        delta_time: Optional[float] = None,
    ) -> bool:
        """
        Attempt to move in the current direction.

        Args:
            can_move_func: Function to check if movement is valid
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

        dx, dy = self.last_direction
        if can_move_func(self.x, self.y, dx, dy):
            self.x += dx
            self.y += dy
            if delta_time is not None:
                self.move_progress = max(0.0, self.move_progress - move_interval)
            return True
        if delta_time is not None:
            self.move_progress = min(self.move_progress, move_interval)
        return False

    def __repr__(self) -> str:
        return (
            f"Ghost({self.ghost_id}, {self.name}, "
            f"pos=({self.x}, {self.y}), state={self.state.value})"
        )


class GhostManager:
    """Manages all ghosts."""

    def __init__(self) -> None:
        """Initialize ghost manager."""
        self.ghosts: List[Ghost] = []
        self.next_ghost_value_index = 0

    def create_ghosts(self, corners: List[Tuple[int, int]]) -> None:
        """
        Create ghosts at corner positions.

        Args:
            corners: List of 4 corner positions
        """
        self.ghosts.clear()
        for i, (x, y) in enumerate(corners[:4]):
            ghost = Ghost(i, x, y)
            self.ghosts.append(ghost)

    def get_ghosts(self) -> List[Ghost]:
        """Get all ghosts."""
        return self.ghosts

    def update_frightened(self, delta_time: float) -> None:
        """Update frightened time for all ghosts."""
        for ghost in self.ghosts:
            if ghost.update_frightened_time(delta_time):
                # Reset ghost value index when frightened state ends
                self.next_ghost_value_index = 0

    def update_respawn(self, delta_time: float) -> None:
        """Update respawn time for all ghosts."""
        for ghost in self.ghosts:
            ghost.update_respawn_time(delta_time)

    def make_all_frightened(self, duration: float) -> None:
        """Make all active ghosts frightened.

        Ghosts that are currently respawning (already eaten) are left alone so
        a fresh power-up cannot cancel their respawn and resurrect them in
        place. The eat-combo value is reset so each power-up starts back at the
        lowest ghost value, matching classic Pac-Man scoring.
        """
        self.next_ghost_value_index = 0
        for ghost in self.ghosts:
            if ghost.state == GhostState.RESPAWN:
                continue
            ghost.make_frightened(duration)

    def eat_ghost(self, ghost: Ghost) -> int:
        """
        Handle eating a ghost.

        Args:
            ghost: The ghost being eaten

        Returns:
            Points earned for eating the ghost
        """
        if ghost.state == GhostState.FRIGHTENED:
            value_index = min(
                self.next_ghost_value_index,
                len(GHOST_VALUES) - 1,
            )
            points = GHOST_VALUES[value_index]
            self.next_ghost_value_index += 1
            ghost.respawn()
            return points
        return 0

    def reset_all(self) -> None:
        """Reset all ghosts."""
        for ghost in self.ghosts:
            ghost.reset()
        self.next_ghost_value_index = 0

    def check_collision(self, player_pos: Tuple[int, int]) -> Optional[Ghost]:
        """
        Check if a ghost collides with the player.

        Args:
            player_pos: Player position

        Returns:
            Ghost that collided, or None
        """
        for ghost in self.ghosts:
            if ghost.get_position() == player_pos and ghost.state != GhostState.RESPAWN:
                return ghost
        return None
