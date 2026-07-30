"""Unit tests for the game engine."""

import sys
from pathlib import Path

# Add src to path
SRC_PATH = Path(__file__).parent.parent / "src"
if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

import unittest
from game.player import Player, Direction
from game.ghost import Ghost, GhostManager, GhostState
from game.collectible import Collectible, CollectibleManager, CollectibleType
from game.game_engine import GameEngine
from utils.constants import STATE_PLAYING, DIRECTIONS


class TestPlayer(unittest.TestCase):
    """Test player functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.player = Player(10, 10)

    def test_player_initialization(self):
        """Test player initializes correctly."""
        self.assertEqual(self.player.x, 10)
        self.assertEqual(self.player.y, 10)
        self.assertEqual(self.player.lives, 3)
        self.assertEqual(self.player.score, 0)

    def test_player_movement(self):
        """Test player position."""
        self.assertEqual(self.player.get_position(), (10, 10))

    def test_player_movement_uses_speed_timing(self):
        """Test player does not move once per frame."""
        player = Player(0, 0)

        def can_move(x, y, dx, dy):
            return True

        player.set_direction(Direction.RIGHT)
        self.assertTrue(player.try_move(can_move, 0.016))
        self.assertEqual(player.get_position(), (1, 0))

        self.assertFalse(player.try_move(can_move, 0.016))
        self.assertEqual(player.get_position(), (1, 0))

        self.assertTrue(player.try_move(can_move, 1.0 / player.speed))
        self.assertEqual(player.get_position(), (2, 0))

    def test_add_score(self):
        """Test score addition."""
        self.player.add_score(100)
        self.assertEqual(self.player.get_score(), 100)
        self.player.add_score(50)
        self.assertEqual(self.player.get_score(), 150)

    def test_lose_life(self):
        """Test losing a life."""
        initial_lives = self.player.get_lives()
        self.player.lose_life()
        self.assertEqual(self.player.get_lives(), initial_lives - 1)

    def test_invincibility(self):
        """Test invincibility."""
        self.player.set_invincible(True)
        self.assertTrue(self.player.is_invincible)
        self.player.lose_life()
        self.assertEqual(self.player.get_lives(), 3)  # Should not lose life

    def test_game_over(self):
        """Test game over condition."""
        while self.player.get_lives() > 0:
            self.player.lose_life()
        self.assertTrue(self.player.is_game_over())


class TestGhost(unittest.TestCase):
    """Test ghost functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.ghost = Ghost(0, 5, 5)

    def test_ghost_initialization(self):
        """Test ghost initializes correctly."""
        self.assertEqual(self.ghost.x, 5)
        self.assertEqual(self.ghost.y, 5)
        self.assertEqual(self.ghost.ghost_id, 0)

    def test_ghost_frightened(self):
        """Test ghost frightened state."""
        self.ghost.make_frightened(5.0)
        self.assertTrue(self.ghost.is_frightened())

    def test_ghost_respawn(self):
        """Test ghost respawn."""
        self.ghost.x = 0
        self.ghost.y = 0
        self.ghost.respawn()
        self.assertEqual(self.ghost.state, GhostState.RESPAWN)

    def test_chase_does_not_reverse_when_forward_path_exists(self):
        """Ghosts must not U-turn mid-corridor while chasing."""
        self.ghost.last_direction = (1, 0)

        def can_move(x, y, dx, dy):
            return (dx, dy) in [(-1, 0), (1, 0)]

        direction = self.ghost.get_move_direction((0, 5), can_move)

        self.assertEqual(direction, (1, 0))

    def test_chase_can_reverse_at_dead_end(self):
        """Ghosts may reverse only when the reverse is the only legal move."""
        self.ghost.last_direction = (1, 0)

        def can_move(x, y, dx, dy):
            return (dx, dy) == (-1, 0)

        direction = self.ghost.get_move_direction((0, 5), can_move)

        self.assertEqual(direction, (-1, 0))


class TestGhostManager(unittest.TestCase):
    """Test ghost manager behaviour."""

    def setUp(self):
        """Set up test fixtures."""
        self.manager = GhostManager()
        self.manager.create_ghosts([(0, 0), (1, 0), (0, 1), (1, 1)])

    def test_power_up_does_not_resurrect_eaten_ghost(self):
        """A new power-up must not cancel a respawning (eaten) ghost."""
        eaten = self.manager.get_ghosts()[0]
        eaten.make_frightened(5.0)
        self.manager.eat_ghost(eaten)
        self.assertEqual(eaten.state, GhostState.RESPAWN)

        self.manager.make_all_frightened(5.0)

        # The eaten ghost stays in RESPAWN; the others become frightened.
        self.assertEqual(eaten.state, GhostState.RESPAWN)
        self.assertTrue(
            all(g.is_frightened() for g in self.manager.get_ghosts()[1:])
        )

    def test_power_up_resets_eat_combo(self):
        """Each power-up restarts the ghost-eating value sequence."""
        ghosts = self.manager.get_ghosts()
        self.manager.make_all_frightened(5.0)
        first = self.manager.eat_ghost(ghosts[0])
        second = self.manager.eat_ghost(ghosts[1])
        self.assertGreater(second, first)

        # A fresh power-up should reset the combo back to the lowest value.
        self.manager.make_all_frightened(5.0)
        third = self.manager.eat_ghost(ghosts[2])
        self.assertEqual(third, first)

    def test_third_ghost_uses_its_own_spawn_position(self):
        """The third ghost should not accidentally reuse the first spawn."""
        corners = [(2, 2), (22, 2), (2, 22), (22, 22)]
        self.manager.create_ghosts(corners)

        ghosts = self.manager.get_ghosts()

        self.assertEqual(ghosts[2].get_position(), corners[2])
        self.assertNotEqual(ghosts[2].get_position(), ghosts[0].get_position())


class TestCollectible(unittest.TestCase):
    """Test collectible functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.pacgum = Collectible(5, 5, CollectibleType.PACGUM)
        self.super = Collectible(10, 10, CollectibleType.SUPER_PACGUM)

    def test_pacgum_value(self):
        """Test pacgum point value."""
        self.assertEqual(self.pacgum.value, 10)

    def test_super_pacgum_value(self):
        """Test super pacgum point value."""
        self.assertEqual(self.super.value, 50)

    def test_super_pacgum_is_power_up(self):
        """Test super pacgum is a power-up."""
        self.assertTrue(self.super.is_power_up)
        self.assertFalse(self.pacgum.is_power_up)

    def test_collect_collectible(self):
        """Test collecting a collectible."""
        self.assertFalse(self.pacgum.collected)
        self.pacgum.collect()
        self.assertTrue(self.pacgum.collected)


class TestCollectibleManager(unittest.TestCase):
    """Test collectible manager."""

    def setUp(self):
        """Set up test fixtures."""
        self.manager = CollectibleManager()

    def test_add_collectible(self):
        """Test adding collectible."""
        self.manager.add_collectible(5, 5, CollectibleType.PACGUM)
        self.assertEqual(len(self.manager.get_all_collectibles()), 1)

    def test_collect_at_position(self):
        """Test collecting at position."""
        self.manager.add_collectible(5, 5, CollectibleType.PACGUM)
        collected, points, is_power = self.manager.collect_at_position(5, 5)
        self.assertTrue(collected)
        self.assertEqual(points, 10)

    def test_level_complete(self):
        """Test level complete detection."""
        self.manager.add_collectible(5, 5, CollectibleType.PACGUM)
        self.assertFalse(self.manager.is_level_complete())
        self.manager.collectibles[0].collect()
        self.assertTrue(self.manager.is_level_complete())


class TestGameEngine(unittest.TestCase):
    """Test game engine."""

    def setUp(self):
        """Set up test fixtures."""
        self.engine = GameEngine()

    def test_engine_initialization(self):
        """Test engine initializes correctly."""
        self.assertIsNotNone(self.engine.player)
        self.assertIsNotNone(self.engine.level_manager)
        self.assertEqual(self.engine.state, "menu")

    def test_start_game(self):
        """Test starting a game."""
        self.engine.start_new_game()
        self.assertEqual(self.engine.state, "playing")

    def test_pause_game(self):
        """Test pausing game."""
        self.engine.start_new_game()
        self.engine.pause_game()
        self.assertEqual(self.engine.state, "paused")

    def test_resume_game(self):
        """Test resuming game."""
        self.engine.start_new_game()
        self.engine.pause_game()
        self.engine.resume_game()
        self.assertEqual(self.engine.state, "playing")

    def test_engine_update_uses_seconds_for_timed_movement(self):
        """Test timed movement progresses with normal frame delta seconds."""
        self.engine.start_new_game()
        self.engine.state = STATE_PLAYING
        level = self.engine.get_current_level()
        player = self.engine.get_player()
        direction_by_delta = {
            (0, -1): Direction.UP,
            (0, 1): Direction.DOWN,
            (-1, 0): Direction.LEFT,
            (1, 0): Direction.RIGHT,
        }
        dx, dy = next(
            delta for delta in DIRECTIONS
            if level.maze.can_move(player.x, player.y, delta[0], delta[1])
        )
        self.engine.set_player_direction(direction_by_delta[(dx, dy)])
        start_pos = self.engine.get_player().get_position()

        for _ in range(20):
            self.engine.update(1.0 / 60.0)

        self.assertNotEqual(self.engine.get_player().get_position(), start_pos)

    def test_speed_cheat_does_not_compound_from_current_speed(self):
        """Speed boost toggles from normal speed, not current mutated speed."""
        base_speed = self.engine.player.speed

        self.engine.toggle_cheat_speed_up()
        self.assertEqual(self.engine.player.speed, base_speed * 2.0)

        self.engine.player.set_speed(base_speed * 10.0)
        self.engine.toggle_cheat_speed_up()
        self.assertEqual(self.engine.player.speed, base_speed)

        self.engine.toggle_cheat_speed_up()
        self.assertEqual(self.engine.player.speed, base_speed * 2.0)

    def test_life_loss_clears_frightened_state(self):
        """Death resets ghost states so frightened mode/music cannot restart."""
        self.engine.start_new_game()
        level = self.engine.get_current_level()
        player = self.engine.get_player()
        ghosts = level.ghost_manager.get_ghosts()
        lives = player.get_lives()

        ghosts[0].set_position(*player.get_position())
        ghosts[0].state = GhostState.CHASE
        ghosts[1].make_frightened(5.0)

        self.engine._check_ghost_collisions(level)

        self.assertEqual(player.get_lives(), lives - 1)
        self.assertFalse(any(ghost.is_frightened() for ghost in ghosts))


if __name__ == "__main__":
    unittest.main()
