"""Main game application entry point."""

import sys
from pathlib import Path
from typing import Any, Dict, Optional

# Add src to path
SRC_PATH = Path(__file__).parent.parent
if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

import pygame
from pygame.locals import (
    KEYDOWN, QUIT,
    K_BACKSPACE, K_DOWN, K_ESCAPE, K_h, K_i, K_LEFT, K_m, K_q,
    K_RETURN, K_RIGHT, K_SPACE, K_UP, K_a, K_d, K_s, K_w,
)

from game import GameEngine, Direction
from ui import GameDisplay
from utils.constants import (
    WINDOW_WIDTH, WINDOW_HEIGHT,
    STATE_MENU, STATE_PLAYING, STATE_PAUSED,
    STATE_LEVEL_COMPLETE, STATE_GAME_OVER, STATE_VICTORY,
    CHEAT_INVINCIBLE, CHEAT_SKIP_LEVEL, CHEAT_FREEZE_GHOSTS,
    CHEAT_EXTRA_LIVES, CHEAT_SPEED_UP,
)


class GameApplication:
    """Main application class."""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the game application."""
        self.engine = GameEngine()
        self.display = GameDisplay(config=config)
        self.running = True
        self.clock = pygame.time.Clock()
        self.player_name = ""
        self.input_mode = False

    def handle_events(self) -> None:
        """Handle input events."""
        for event in pygame.event.get():
            if event.type == QUIT:
                self.running = False

            elif event.type == KEYDOWN:
                if self.input_mode:
                    self._handle_text_input(event)
                elif self.engine.state == STATE_MENU:
                    self._handle_menu_input(event)
                elif self.engine.state == STATE_PLAYING:
                    self._handle_game_input(event)
                elif self.engine.state == STATE_PAUSED:
                    self._handle_pause_input(event)
                elif self.engine.state == STATE_LEVEL_COMPLETE:
                    self._handle_level_complete_input(event)
                elif self.engine.state in (STATE_GAME_OVER, STATE_VICTORY):
                    self._handle_game_end_input(event)

    def _handle_menu_input(self, event: pygame.event.Event) -> None:
        """Handle menu input."""
        if event.key == K_SPACE:
            self.engine.start_new_game()
        elif event.key == K_h:
            self._show_highscores()
        elif event.key == K_i:
            self._show_instructions()
        elif event.key == K_q or event.key == K_ESCAPE:
            self.running = False

    def _handle_game_input(self, event: pygame.event.Event) -> None:
        """Handle game input."""
        if event.key == K_UP or event.key == K_w:
            self.engine.set_player_direction(Direction.UP)
        elif event.key == K_DOWN or event.key == K_s:
            self.engine.set_player_direction(Direction.DOWN)
        elif event.key == K_LEFT or event.key == K_a:
            self.engine.set_player_direction(Direction.LEFT)
        elif event.key == K_RIGHT or event.key == K_d:
            self.engine.set_player_direction(Direction.RIGHT)
        elif event.key == K_SPACE:
            self.engine.pause_game()
        elif event.key == K_m:
            self.engine.return_to_menu()

        # Cheat mode
        elif event.key == ord(CHEAT_INVINCIBLE):
            self.engine.toggle_cheat_invincible()
        elif event.key == ord(CHEAT_SKIP_LEVEL):
            self.engine.activate_cheat_skip_level()
        elif event.key == ord(CHEAT_FREEZE_GHOSTS):
            self.engine.toggle_cheat_freeze_ghosts()
        elif event.key == ord(CHEAT_EXTRA_LIVES):
            self.engine.activate_cheat_extra_lives()
        elif event.key == ord(CHEAT_SPEED_UP):
            self.engine.toggle_cheat_speed_up()

    def _handle_pause_input(self, event: pygame.event.Event) -> None:
        """Handle pause menu input."""
        if event.key == K_SPACE:
            self.engine.resume_game()
        elif event.key == K_m:
            self.engine.return_to_menu()

    def _handle_level_complete_input(self, event: pygame.event.Event) -> None:
        """Handle level complete input."""
        if event.key == K_SPACE:
            self.engine.next_level()

    def _handle_game_end_input(self, event: pygame.event.Event) -> None:
        """Handle game end input."""
        if event.key == K_RETURN:
            self.player_name = ""
            self.input_mode = True
        elif event.key == K_m:
            self.engine.return_to_menu()

    def _handle_text_input(self, event: pygame.event.Event) -> None:
        """Handle text input for name entry."""
        if event.key == K_RETURN:
            name = self.player_name.strip() or "PLAYER"
            self.engine.save_highscore(name[:10])
            self.player_name = ""
            self.input_mode = False
            self.engine.return_to_menu()
        elif event.key == K_BACKSPACE:
            self.player_name = self.player_name[:-1]
        elif len(self.player_name) < 10:
            if event.unicode.isalnum() or event.unicode == ' ':
                self.player_name += event.unicode

    def _show_highscores(self) -> None:
        """Display highscores."""
        showing = True
        while showing:
            for event in pygame.event.get():
                if event.type == QUIT:
                    self.running = False
                    showing = False
                elif event.type == KEYDOWN:
                    if event.key == K_SPACE:
                        showing = False

            self.display.clear_screen()
            self.display.draw_highscores(self.engine.get_highscores())
            self.display.flip_display()
            self.display.tick(60)

    def _show_instructions(self) -> None:
        """Display instructions."""
        showing = True
        while showing:
            for event in pygame.event.get():
                if event.type == QUIT:
                    self.running = False
                    showing = False
                elif event.type == KEYDOWN:
                    if event.key == K_SPACE:
                        showing = False

            self.display.clear_screen()
            self.display.draw_instructions()
            self.display.flip_display()
            self.display.tick(60)

    def update(self, delta_time: float) -> None:
        """Update game state."""
        if self.engine.state == STATE_PLAYING:
            self.engine.update(delta_time)

    def render(self) -> None:
        """Render game state."""
        self.display.clear_screen()

        if self.engine.state == STATE_MENU:
            self.display.draw_main_menu()

        elif self.engine.state == STATE_PLAYING:
            level = self.engine.get_current_level()
            if level:
                self.display.draw_maze(level.maze)
                self.display.draw_collectibles(level.collectible_manager)
                self.display.draw_ghosts(level.ghost_manager)
            self.display.draw_player(self.engine.get_player())
            self.display.draw_hud(self.engine)

        elif self.engine.state == STATE_PAUSED:
            level = self.engine.get_current_level()
            if level:
                self.display.draw_maze(level.maze)
                self.display.draw_collectibles(level.collectible_manager)
                self.display.draw_ghosts(level.ghost_manager)
            self.display.draw_player(self.engine.get_player())
            self.display.draw_hud(self.engine)
            self.display.draw_pause_menu()

        elif self.engine.state == STATE_LEVEL_COMPLETE:
            self.display.draw_main_menu()
            complete_text = self.display.font_medium.render(
                "Level Complete! Press SPACE for next level",
                True,
                (220, 105, 150)
            )
            self.display.screen.blit(
                complete_text,
                complete_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2))
            )

        elif self.engine.state == STATE_GAME_OVER:
            self.display.draw_game_over(self.engine.get_player_score())
            if self.input_mode:
                self.display.draw_text_input(self.player_name)
            else:
                press_text = self.display.font_small.render(
                    "Press ENTER to continue",
                    True,
                    (200, 65, 130)
                )
                self.display.screen.blit(
                    press_text,
                    press_text.get_rect(center=(WINDOW_WIDTH // 2, 550))
                )

        elif self.engine.state == STATE_VICTORY:
            self.display.draw_victory(self.engine.get_player_score())
            if self.input_mode:
                self.display.draw_text_input(self.player_name)
            else:
                press_text = self.display.font_small.render(
                    "Press ENTER to continue",
                    True,
                    (200, 65, 130)
                )
                self.display.screen.blit(
                    press_text,
                    press_text.get_rect(center=(WINDOW_WIDTH // 2, 550))
                )

        self.display.flip_display()

    def run(self) -> None:
        """Main game loop."""
        print("🎀 Hello Kitty Maze Game Started! 🎀", flush=True)
        print(
            "Controls: Arrow Keys/WASD to move, Space to pause, M for menu",
            flush=True,
        )
        print("Cheat Mode: I=Invincible, N=Skip, F=Freeze, L=Life, T=Speed", flush=True)
        print("", flush=True)

        try:
            while self.running:
                delta_time = self.display.tick(60)
                self.handle_events()
                self.update(delta_time)
                self.render()

        except KeyboardInterrupt:
            print("\n⚠️  Game interrupted by user", flush=True)
        except Exception as e:
            print(f"\n❌ FATAL ERROR: {e}", flush=True)
        finally:
            self.display.quit()
            print("Game ended. Thanks for playing! 🎀", flush=True)


def main() -> None:
    """Entry point."""
    app = GameApplication()
    app.run()


if __name__ == "__main__":
    main()
