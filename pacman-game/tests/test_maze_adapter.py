"""Regression tests for maze generation and movement."""

import sys
from pathlib import Path

SRC_PATH = Path(__file__).parent.parent / "src"
if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

import unittest

from game.level_manager import LevelManager, Level
from game.maze_adapter import MazeAdapter
from game.player import Player


def make_adapter(grid):
    """Create a MazeAdapter test double without invoking the generator."""
    adapter = MazeAdapter.__new__(MazeAdapter)
    adapter.width = len(grid[0])
    adapter.height = len(grid)
    adapter.level = 1
    adapter.maze_generator = None
    adapter.maze_grid = grid
    adapter.start_pos = (0, 0)
    adapter.end_pos = (adapter.width - 1, adapter.height - 1)
    return adapter


class TestMazeAdapter(unittest.TestCase):
    """Test maze wall interpretation and safe spawn positions."""

    def test_wall_bits_match_a_maze_ing_generator(self):
        adapter = make_adapter([[1, 4, 2, 8, 15]])

        self.assertTrue(adapter.is_wall_north(0, 0))
        self.assertTrue(adapter.is_wall_south(1, 0))
        self.assertTrue(adapter.is_wall_east(2, 0))
        self.assertTrue(adapter.is_wall_west(3, 0))
        self.assertFalse(adapter.can_move_to(4, 0))

    def test_can_move_rejects_invalid_move_shapes(self):
        adapter = make_adapter([
            [0, 0],
            [0, 0],
        ])

        self.assertFalse(adapter.can_move(0, 0, 0, 0))
        self.assertFalse(adapter.can_move(0, 0, 1, 1))
        self.assertFalse(adapter.can_move(0, 0, 2, 0))

    def test_can_move_requires_both_sides_of_wall_to_be_open(self):
        adapter = make_adapter([[0, 8]])

        self.assertFalse(adapter.can_move(0, 0, 1, 0))

    def test_generated_level_uses_playable_spawns_and_power_corners(self):
        level = Level(1)
        center = level.maze.get_center_position()
        corners = level.maze.get_corner_positions()
        cells = [
            cell
            for row in level.maze.get_maze_grid()
            for cell in row
        ]

        self.assertTrue(level.maze.can_move_to(*center))
        self.assertIsNotNone(level.maze.maze_generator)
        self.assertGreater(sum(1 for cell in cells if cell), 100)
        self.assertEqual(len(corners), 4)
        self.assertEqual(len(set(corners)), 4)
        for corner in corners:
            self.assertTrue(level.maze.can_move_to(*corner))

        self.assertEqual(level.collectible_manager.get_remaining_super_pacgums(), 4)
        self.assertEqual(len(level.ghost_manager.get_ghosts()), 4)

    def test_player_spawn_tracks_loaded_maze_center(self):
        player = Player(0, 0)
        manager = LevelManager()
        manager.start_game(player)

        level = manager.get_current_level()
        spawn = level.maze.get_center_position()

        self.assertEqual(player.get_position(), spawn)
        self.assertEqual((player.start_x, player.start_y), spawn)


if __name__ == "__main__":
    unittest.main()
