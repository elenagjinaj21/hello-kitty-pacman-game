"""Adapter for the A-Maze-ing maze generator package."""

import random
import signal
import sys
from pathlib import Path
from types import FrameType
from typing import Any, Callable, List, Optional, Set, Tuple

# Add the maze generator package to the path
MAZE_GEN_PATH = (
    Path(__file__).parent.parent.parent / "mazegenerator-00001-py3-none-any"
)
if str(MAZE_GEN_PATH) not in sys.path:
    sys.path.insert(0, str(MAZE_GEN_PATH))

try:
    from mazegenerator import MazeGenerator
except ImportError:
    raise ImportError(
        "Failed to import MazeGenerator. Ensure mazegenerator package is available."
    )

from utils.constants import FIRST_LEVEL_SEED, MAZE_EXTRA_CONNECTION_CHANCE


class MazeAdapter:
    """
    Adapter layer for the A-Maze-ing maze generator.

    The maze generator produces a 2D grid where each cell contains a bit-encoded
    value indicating which walls exist. This adapter converts that representation
    into a game-friendly format.

    Bit meanings (from MazeGenerator):
    - 1: wall to the north
    - 2: wall to the east
    - 4: wall to the south
    - 8: wall to the west
    - 15: surrounded by walls (completely enclosed)
    """

    WALL_NORTH = 1
    WALL_EAST = 2
    WALL_SOUTH = 4
    WALL_WEST = 8

    def __init__(self, width: int = 19, height: int = 19, level: int = 1):
        """
        Initialize the maze adapter.

        Args:
            width: Maze width in cells (19x19 for better gameplay pacing)
            height: Maze height in cells (19x19 for better gameplay pacing)
            level: Current level number (for seeding)
        """
        self.width = width
        self.height = height
        self.level = level
        self.maze_generator: Optional[MazeGenerator] = None
        self.maze_grid: List[List[int]] = []
        self.start_pos: Tuple[int, int] = (0, 0)
        self.end_pos: Tuple[int, int] = (0, 0)
        self.generate_maze()

    def generate_maze(self) -> None:
        """Generate a new maze for the current level."""
        # Use fixed seed for level 1. The A-Maze-ing package treats seed=0
        # as "choose a random seed" for later levels.
        seed = FIRST_LEVEL_SEED if self.level == 1 else 0

        try:
            self.maze_generator = self._generate_with_timeout(seed)
            self.maze_grid = self.maze_generator.maze
        except Exception as exc:
            print(f"Maze warning: generator failed ({exc}); using fallback maze")
            self.maze_generator = None
            self.maze_grid = self._make_fallback_maze()

        self._open_extra_connections(seed)
        if self.maze_generator:
            entry = self.maze_generator.maze_entry
            exit_cell = self.maze_generator.maze_exit
        else:
            entry = (0, 0)
            exit_cell = (self.width - 1, self.height - 1)
        self.start_pos = self._find_nearest_corridor(*entry)
        self.end_pos = self._find_nearest_corridor(*exit_cell)

    def get_maze_grid(self) -> List[List[int]]:
        """Get the raw maze grid."""
        return self.maze_grid

    def is_wall_north(self, x: int, y: int) -> bool:
        """Check if there's a wall to the north."""
        if 0 <= y < self.height and 0 <= x < self.width:
            return bool(self.maze_grid[y][x] & self.WALL_NORTH)
        return True

    def is_wall_south(self, x: int, y: int) -> bool:
        """Check if there's a wall to the south."""
        if 0 <= y < self.height and 0 <= x < self.width:
            return bool(self.maze_grid[y][x] & self.WALL_SOUTH)
        return True

    def is_wall_east(self, x: int, y: int) -> bool:
        """Check if there's a wall to the east."""
        if 0 <= y < self.height and 0 <= x < self.width:
            return bool(self.maze_grid[y][x] & self.WALL_EAST)
        return True

    def is_wall_west(self, x: int, y: int) -> bool:
        """Check if there's a wall to the west."""
        if 0 <= y < self.height and 0 <= x < self.width:
            return bool(self.maze_grid[y][x] & self.WALL_WEST)
        return True

    def can_move_to(self, x: int, y: int) -> bool:
        """Check if a position is a valid corridor."""
        if not (0 <= x < self.width and 0 <= y < self.height):
            return False

        # Check if it's a corridor (not surrounded by walls)
        cell_value = self.maze_grid[y][x]

        # Value 15 means completely enclosed
        if cell_value == 15:
            return False

        # If at least one side is open, it's passable
        return True

    def can_move(self, x: int, y: int, dx: int, dy: int) -> bool:
        """
        Check if an entity can move from (x,y) to (x+dx, y+dy).

        Args:
            x: Current x position
            y: Current y position
            dx: Direction x (-1, 0, 1)
            dy: Direction y (-1, 0, 1)

        Returns:
            True if movement is possible
        """
        # Only single-cell cardinal movement is valid in the maze.
        if abs(dx) + abs(dy) != 1:
            return False

        if not self.can_move_to(x, y):
            return False

        # Check boundaries
        new_x, new_y = x + dx, y + dy
        if not (0 <= new_x < self.width and 0 <= new_y < self.height):
            return False

        if not self.can_move_to(new_x, new_y):
            return False

        # Check both cells. This keeps collision correct even if a generated
        # maze contains an inconsistent one-sided wall.
        if dx == 1:  # Moving east
            if self.is_wall_east(x, y) or self.is_wall_west(new_x, new_y):
                return False
        elif dx == -1:  # Moving west
            if self.is_wall_west(x, y) or self.is_wall_east(new_x, new_y):
                return False
        elif dy == -1:  # Moving north
            if self.is_wall_north(x, y) or self.is_wall_south(new_x, new_y):
                return False
        elif dy == 1:  # Moving south
            if self.is_wall_south(x, y) or self.is_wall_north(new_x, new_y):
                return False

        return True

    def get_start_position(self) -> Tuple[int, int]:
        """Get the maze entry point (player start position)."""
        return self.start_pos

    def get_center_position(self) -> Tuple[int, int]:
        """Get the nearest playable cell to the center of the maze."""
        return self._find_nearest_corridor(self.width // 2, self.height // 2)

    def get_corner_positions(self) -> List[Tuple[int, int]]:
        """Get four playable corner positions for ghosts and super-pacgums."""
        margin = 2
        desired_positions = [
            (margin, margin),  # Top-left
            (self.width - 1 - margin, margin),  # Top-right
            (margin, self.height - 1 - margin),  # Bottom-left
            (self.width - 1 - margin, self.height - 1 - margin),  # Bottom-right
        ]
        occupied: Set[Tuple[int, int]] = set()
        corners = []
        for x, y in desired_positions:
            corner = self._find_nearest_corridor(x, y, occupied)
            corners.append(corner)
            occupied.add(corner)
        return corners

    def get_all_corridors(self) -> List[Tuple[int, int]]:
        """Get a list of all corridor positions."""
        corridors = []
        for y in range(self.height):
            for x in range(self.width):
                if self.can_move_to(x, y):
                    corridors.append((x, y))
        return corridors

    def is_42_cell(self, x: int, y: int) -> bool:
        """Check if a cell is part of the embedded '42' pattern."""
        if 0 <= x < self.width and 0 <= y < self.height:
            return self.maze_grid[y][x] == 15
        return False

    def get_shortest_path(self) -> str:
        """Get the shortest path from start to end (as a string of directions)."""
        if self.maze_generator and isinstance(self.maze_generator.shortest_path, str):
            return self.maze_generator.shortest_path
        return ""

    def maze_to_pixel_coords(
        self,
        cell_x: int,
        cell_y: int,
        cell_size: int = 30,
    ) -> Tuple[int, int]:
        """Convert maze cell coordinates to pixel coordinates."""
        return (cell_x * cell_size, cell_y * cell_size)

    def pixel_to_maze_coords(
        self,
        pixel_x: int,
        pixel_y: int,
        cell_size: int = 30,
    ) -> Tuple[int, int]:
        """Convert pixel coordinates to maze cell coordinates."""
        return (pixel_x // cell_size, pixel_y // cell_size)

    def _find_nearest_corridor(
        self,
        target_x: int,
        target_y: int,
        excluded: Optional[Set[Tuple[int, int]]] = None
    ) -> Tuple[int, int]:
        """Find the playable cell nearest to a requested maze position."""
        excluded = excluded or set()
        target_x = min(max(target_x, 0), self.width - 1)
        target_y = min(max(target_y, 0), self.height - 1)

        if (
            self.can_move_to(target_x, target_y)
            and (target_x, target_y) not in excluded
        ):
            return (target_x, target_y)

        corridors = [
            (abs(x - target_x) + abs(y - target_y), y, x)
            for y in range(self.height)
            for x in range(self.width)
            if self.can_move_to(x, y) and (x, y) not in excluded
        ]
        if not corridors:
            raise ValueError("Generated maze does not contain any playable corridors")

        _, y, x = min(corridors)
        return (x, y)

    def _open_extra_connections(self, seed: int) -> None:
        """Open extra internal walls so the maze has more Pac-Man-style loops."""
        rng = random.Random(seed if seed > 0 else None)

        for y in range(1, self.height - 1):
            for x in range(1, self.width - 1):
                if not self.can_move_to(x, y) or self.is_42_cell(x, y):
                    continue

                if (
                    x + 1 < self.width - 1
                    and self.can_move_to(x + 1, y)
                    and not self.is_42_cell(x + 1, y)
                    and self.is_wall_east(x, y)
                    and rng.random() < MAZE_EXTRA_CONNECTION_CHANCE
                ):
                    self._remove_wall_between(x, y, x + 1, y)

                if (
                    y + 1 < self.height - 1
                    and self.can_move_to(x, y + 1)
                    and not self.is_42_cell(x, y + 1)
                    and self.is_wall_south(x, y)
                    and rng.random() < MAZE_EXTRA_CONNECTION_CHANCE
                ):
                    self._remove_wall_between(x, y, x, y + 1)

    def _remove_wall_between(self, x: int, y: int, other_x: int, other_y: int) -> None:
        """Remove matching wall bits between two adjacent cells."""
        dx = other_x - x
        dy = other_y - y

        if dx == 1 and dy == 0:
            self.maze_grid[y][x] &= ~self.WALL_EAST
            self.maze_grid[other_y][other_x] &= ~self.WALL_WEST
        elif dx == -1 and dy == 0:
            self.maze_grid[y][x] &= ~self.WALL_WEST
            self.maze_grid[other_y][other_x] &= ~self.WALL_EAST
        elif dx == 0 and dy == 1:
            self.maze_grid[y][x] &= ~self.WALL_SOUTH
            self.maze_grid[other_y][other_x] &= ~self.WALL_NORTH
        elif dx == 0 and dy == -1:
            self.maze_grid[y][x] &= ~self.WALL_NORTH
            self.maze_grid[other_y][other_x] &= ~self.WALL_SOUTH

    def _make_fallback_maze(self) -> List[List[int]]:
        """Create a simple open maze if the external generator cannot run."""
        maze: List[List[int]] = []
        for y in range(self.height):
            row: List[int] = []
            for x in range(self.width):
                value = 0
                if y == 0:
                    value |= self.WALL_NORTH
                if x == self.width - 1:
                    value |= self.WALL_EAST
                if y == self.height - 1:
                    value |= self.WALL_SOUTH
                if x == 0:
                    value |= self.WALL_WEST
                row.append(value)
            maze.append(row)
        return maze

    def _generate_with_timeout(self, seed: int) -> MazeGenerator:
        """Run the assigned generator with perfect=False and a safety timeout.

        The expensive part of the generator is its recursive shortest-path
        search, which we always skip here. On platforms that support it
        (Unix main thread) we additionally arm a SIGALRM watchdog; Windows and
        worker threads simply run without the alarm.
        """
        original_shortest_path: Callable[[Any], None] = MazeGenerator._find_short_path

        def _skip_shortest_path(generator: Any) -> None:
            generator._shortest_path = ""

        setattr(MazeGenerator, "_find_short_path", _skip_shortest_path)

        # signal.SIGALRM / signal.alarm only exist on Unix, and signal handlers
        # can only be installed from the main thread. Fall back gracefully when
        # either condition is not met instead of crashing into the fallback maze.
        use_alarm = hasattr(signal, "SIGALRM") and hasattr(signal, "alarm")
        previous_handler = None

        def _timeout_handler(signum: int, frame: Optional[FrameType]) -> None:
            raise TimeoutError("A-Maze-ing generator timed out")

        if use_alarm:
            try:
                previous_handler = signal.getsignal(signal.SIGALRM)
                signal.signal(signal.SIGALRM, _timeout_handler)
                signal.alarm(2)
            except (ValueError, OSError):
                # Not running in the main thread; continue without the watchdog.
                use_alarm = False
                previous_handler = None

        try:
            return MazeGenerator(
                size=(self.width, self.height),
                perfect=False,
                seed=seed,
            )
        finally:
            if use_alarm:
                signal.alarm(0)
                if previous_handler is not None:
                    signal.signal(signal.SIGALRM, previous_handler)
            setattr(MazeGenerator, "_find_short_path", original_shortest_path)
