"""Main game display and rendering."""

from typing import Any, Dict, List, Optional, Tuple
import pygame

from utils.constants import (
    WINDOW_WIDTH, WINDOW_HEIGHT, FPS,
    COLOR_BACKGROUND, COLOR_WALL_DARK, COLOR_CORRIDOR,
    COLOR_TEXT, COLOR_TEXT_DARK, COLOR_HIGHLIGHT,
    CELL_SIZE, PACGUM_SIZE, SUPER_PACGUM_SIZE,
    PLAYER_SIZE, GHOST_SIZE,
    UI_PADDING, UI_FONT_SIZE_LARGE, UI_FONT_SIZE_MEDIUM, UI_FONT_SIZE_SMALL,
    ASSETS_DIR,
)
from ui.assets import AssetManager


class GameDisplay:
    """Handles all game rendering."""

    def __init__(
        self,
        caption: str = "Hello Kitty Maze Game",
        config: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize the game display.

        Args:
            caption: Window title
        """
        import os
        import sys

        pygame.init()

        # Check for display availability. Only relevant on Linux/X11 — Windows
        # and macOS do not use the DISPLAY environment variable.
        if sys.platform.startswith("linux") and not os.environ.get('DISPLAY'):
            print("⚠️  Warning: No X11 display found!")
            print("If running remotely, use: ssh -X user@host")
            print("Or create virtual display: Xvfb :99 -screen 0 1200x900x24 &")

        try:
            self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
            pygame.display.set_caption(caption)
        except pygame.error as e:
            print(f"❌ Display Error: {e}")
            print("Trying to continue with fallback display...")
            self.screen = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))

        self.clock = pygame.time.Clock()
        self.asset_manager = AssetManager(config=config)
        self.maze_offset: Tuple[int, int] = (0, 0)
        self.player_sprite = self._load_player_sprite()

        # Fonts
        self.font_large = pygame.font.Font(None, UI_FONT_SIZE_LARGE)
        self.font_medium = pygame.font.Font(None, UI_FONT_SIZE_MEDIUM)
        self.font_small = pygame.font.Font(None, UI_FONT_SIZE_SMALL)

    def _load_player_sprite(self) -> Optional[pygame.Surface]:
        """Load the configured player PNG or the first sprite PNG available."""
        sprite_dir = ASSETS_DIR / "sprites"
        player_config = self.asset_manager.config.get("player", {})
        configured_name = ""
        if isinstance(player_config, dict):
            configured_name = str(player_config.get("sprite_filename", ""))

        candidates = []
        if configured_name:
            candidates.append(sprite_dir / configured_name)
        candidates.append(sprite_dir / "hello_kitty.png")
        candidates.extend(sorted(sprite_dir.glob("*.png")))

        sprite_path = next((path for path in candidates if path.exists()), None)
        if sprite_path is None:
            return None
        try:
            sprite = pygame.image.load(str(sprite_path)).convert_alpha()
            return pygame.transform.smoothscale(sprite, (PLAYER_SIZE, PLAYER_SIZE))
        except (pygame.error, OSError):
            return None

    def _get_maze_offset(self, maze_adapter: Any) -> Tuple[int, int]:
        """Return the centered pixel offset for the current maze."""
        maze_width = maze_adapter.width * CELL_SIZE
        maze_height = maze_adapter.height * CELL_SIZE
        return (
            max(0, (WINDOW_WIDTH - maze_width) // 2),
            max(0, (WINDOW_HEIGHT - maze_height) // 2),
        )

    def _cell_center(self, x: int, y: int) -> Tuple[int, int]:
        """Convert a maze cell to its centered screen pixel position."""
        offset_x, offset_y = self.maze_offset
        return (
            offset_x + x * CELL_SIZE + CELL_SIZE // 2,
            offset_y + y * CELL_SIZE + CELL_SIZE // 2,
        )

    def _draw_button_label(
        self,
        text: str,
        center: Tuple[int, int],
        width: int = 360,
        height: int = 52,
    ) -> None:
        """Draw a soft rounded menu label."""
        rect = pygame.Rect(0, 0, width, height)
        rect.center = center
        shadow = rect.move(0, 3)
        pygame.draw.rect(self.screen, (248, 194, 214), shadow, border_radius=18)
        pygame.draw.rect(self.screen, (255, 252, 254), rect, border_radius=18)
        pygame.draw.rect(self.screen, COLOR_WALL_DARK, rect, 2, border_radius=18)
        label = self.font_medium.render(text, True, COLOR_TEXT_DARK)
        self.screen.blit(label, label.get_rect(center=rect.center))

    def draw_maze(self, maze_adapter: Any) -> None:
        """Draw the maze."""
        maze = maze_adapter.get_maze_grid()
        self.maze_offset = self._get_maze_offset(maze_adapter)
        offset_x, offset_y = self.maze_offset
        wall_width = 5
        for y, row in enumerate(maze):
            for x, cell in enumerate(row):
                pixel_x = offset_x + x * CELL_SIZE
                pixel_y = offset_y + y * CELL_SIZE

                # Draw corridor
                pygame.draw.rect(
                    self.screen,
                    COLOR_CORRIDOR,
                    (pixel_x, pixel_y, CELL_SIZE, CELL_SIZE)
                )

                # Draw walls as borders
                if maze_adapter.is_wall_north(x, y):
                    pygame.draw.line(
                        self.screen, COLOR_WALL_DARK,
                        (pixel_x, pixel_y),
                        (pixel_x + CELL_SIZE, pixel_y), wall_width
                    )
                if maze_adapter.is_wall_south(x, y):
                    pygame.draw.line(
                        self.screen, COLOR_WALL_DARK,
                        (pixel_x, pixel_y + CELL_SIZE),
                        (pixel_x + CELL_SIZE, pixel_y + CELL_SIZE), wall_width
                    )
                if maze_adapter.is_wall_west(x, y):
                    pygame.draw.line(
                        self.screen, COLOR_WALL_DARK,
                        (pixel_x, pixel_y),
                        (pixel_x, pixel_y + CELL_SIZE), wall_width
                    )
                if maze_adapter.is_wall_east(x, y):
                    pygame.draw.line(
                        self.screen, COLOR_WALL_DARK,
                        (pixel_x + CELL_SIZE, pixel_y),
                        (pixel_x + CELL_SIZE, pixel_y + CELL_SIZE), wall_width
                    )

                # Highlight the 42 area
                if maze_adapter.is_42_cell(x, y):
                    pygame.draw.rect(
                        self.screen,
                        COLOR_HIGHLIGHT,
                        (pixel_x + 2, pixel_y + 2, CELL_SIZE - 4, CELL_SIZE - 4)
                    )

    def draw_collectibles(self, collectible_manager: Any) -> None:
        """Draw all collectibles."""
        for collectible in collectible_manager.get_all_collectibles():
            if collectible.collected:
                continue

            pixel_x, pixel_y = self._cell_center(collectible.x, collectible.y)

            if collectible.is_power_up:
                # Draw super-pacgum (larger, different color)
                pygame.draw.circle(
                    self.screen,
                    COLOR_TEXT,
                    (pixel_x, pixel_y),
                    SUPER_PACGUM_SIZE
                )
                pygame.draw.circle(
                    self.screen,
                    COLOR_TEXT_DARK,
                    (pixel_x, pixel_y),
                    SUPER_PACGUM_SIZE - 1
                )
            else:
                # Draw pacgum
                pygame.draw.circle(
                    self.screen,
                    COLOR_TEXT,
                    (pixel_x, pixel_y),
                    PACGUM_SIZE
                )

    def draw_player(self, player: Any) -> None:
        """Draw the player."""
        pixel_x, pixel_y = self._cell_center(player.x, player.y)
        radius = PLAYER_SIZE // 2

        if self.player_sprite:
            sprite_rect = self.player_sprite.get_rect(center=(pixel_x, pixel_y))
            self.screen.blit(self.player_sprite, sprite_rect)
            if player.is_invincible:
                pygame.draw.circle(
                    self.screen,
                    COLOR_HIGHLIGHT,
                    (pixel_x, pixel_y),
                    radius + 4,
                    2
                )
            return

        fur = (255, 255, 252)
        outline = (236, 145, 176)
        inner_ear = (255, 206, 222)
        bow = (255, 104, 158)
        nose = (248, 205, 82)
        eye = (72, 55, 65)
        cheek = (255, 190, 210)
        whisker = (180, 125, 145)

        ear_radius = max(3, radius // 2)
        pygame.draw.circle(self.screen, outline, (pixel_x - 6, pixel_y - 7), ear_radius)
        pygame.draw.circle(self.screen, outline, (pixel_x + 6, pixel_y - 7), ear_radius)
        pygame.draw.circle(self.screen, fur, (pixel_x - 6, pixel_y - 7), ear_radius - 1)
        pygame.draw.circle(self.screen, fur, (pixel_x + 6, pixel_y - 7), ear_radius - 1)
        inner_radius = max(1, ear_radius - 3)
        pygame.draw.circle(
            self.screen,
            inner_ear,
            (pixel_x - 6, pixel_y - 7),
            inner_radius,
        )
        pygame.draw.circle(
            self.screen,
            inner_ear,
            (pixel_x + 6, pixel_y - 7),
            inner_radius,
        )

        face_rect = (pixel_x - radius, pixel_y - radius + 1, radius * 2, radius * 2 - 1)
        inner_face_rect = (
            pixel_x - radius + 1,
            pixel_y - radius + 2,
            radius * 2 - 2,
            radius * 2 - 3,
        )
        pygame.draw.ellipse(self.screen, outline, face_rect)
        pygame.draw.ellipse(self.screen, fur, inner_face_rect)

        pygame.draw.circle(self.screen, eye, (pixel_x - 4, pixel_y - 2), 1)
        pygame.draw.circle(self.screen, eye, (pixel_x + 4, pixel_y - 2), 1)
        pygame.draw.circle(self.screen, cheek, (pixel_x - 6, pixel_y + 3), 2)
        pygame.draw.circle(self.screen, cheek, (pixel_x + 6, pixel_y + 3), 2)
        pygame.draw.ellipse(self.screen, nose, (pixel_x - 2, pixel_y, 4, 3))
        pygame.draw.line(
            self.screen,
            whisker,
            (pixel_x - 3, pixel_y + 3),
            (pixel_x - 9, pixel_y + 2),
            1,
        )
        pygame.draw.line(
            self.screen,
            whisker,
            (pixel_x - 3, pixel_y + 5),
            (pixel_x - 9, pixel_y + 6),
            1,
        )
        pygame.draw.line(
            self.screen,
            whisker,
            (pixel_x + 3, pixel_y + 3),
            (pixel_x + 9, pixel_y + 2),
            1,
        )
        pygame.draw.line(
            self.screen,
            whisker,
            (pixel_x + 3, pixel_y + 5),
            (pixel_x + 9, pixel_y + 6),
            1,
        )

        bow_center = (pixel_x - 7, pixel_y - 8)
        pygame.draw.circle(self.screen, bow, bow_center, 2)
        pygame.draw.circle(self.screen, bow, (bow_center[0] - 3, bow_center[1]), 3)
        pygame.draw.circle(self.screen, bow, (bow_center[0] + 3, bow_center[1]), 3)
        pygame.draw.circle(self.screen, (255, 214, 228), bow_center, 1)

        # Invincibility indicator
        if player.is_invincible:
            pygame.draw.circle(
                self.screen,
                COLOR_HIGHLIGHT,
                (pixel_x, pixel_y),
                radius + 4,
                2
            )

    def draw_ghosts(self, ghost_manager: Any) -> None:
        """Draw all ghosts."""
        for ghost in ghost_manager.get_ghosts():
            pixel_x, pixel_y = self._cell_center(ghost.x, ghost.y)
            radius = GHOST_SIZE // 2
            state_value = getattr(getattr(ghost, "state", None), "value", "")
            is_respawning = state_value == "respawn"
            if is_respawning:
                body_color = (235, 210, 226)
            elif ghost.is_frightened():
                body_color = (128, 142, 255)
            else:
                body_color = ghost.color
            outline = (154, 72, 120)
            shine = (255, 244, 249)
            eye = (58, 45, 58)
            cheek = (255, 186, 210)
            bow = (255, 105, 160)

            body_rect = pygame.Rect(0, 0, radius * 2, radius * 2 + 5)
            body_rect.center = (pixel_x, pixel_y + 1)
            body_rect.top = pixel_y - radius + 2

            pygame.draw.ellipse(
                self.screen,
                outline,
                (body_rect.left, body_rect.top, body_rect.width, radius * 2),
            )
            pygame.draw.rect(
                self.screen,
                outline,
                (body_rect.left, pixel_y - 1, body_rect.width, radius + 5),
            )
            pygame.draw.ellipse(
                self.screen,
                body_color,
                (
                    body_rect.left + 1,
                    body_rect.top + 1,
                    body_rect.width - 2,
                    radius * 2 - 2,
                ),
            )
            pygame.draw.rect(
                self.screen,
                body_color,
                (body_rect.left + 1, pixel_y, body_rect.width - 2, radius + 3),
            )

            for wave_x in (body_rect.left + 4, pixel_x, body_rect.right - 4):
                pygame.draw.circle(
                    self.screen,
                    body_color,
                    (wave_x, body_rect.bottom - 2),
                    4,
                )
                pygame.draw.circle(
                    self.screen,
                    outline,
                    (wave_x, body_rect.bottom - 2),
                    4,
                    1,
                )

            pygame.draw.circle(self.screen, shine, (pixel_x - 4, pixel_y - 5), 2)
            if is_respawning:
                pygame.draw.line(
                    self.screen,
                    eye,
                    (pixel_x - 7, pixel_y - 2),
                    (pixel_x - 2, pixel_y),
                    1,
                )
                pygame.draw.line(
                    self.screen,
                    eye,
                    (pixel_x + 2, pixel_y),
                    (pixel_x + 7, pixel_y - 2),
                    1,
                )
            else:
                pygame.draw.circle(self.screen, eye, (pixel_x - 4, pixel_y - 1), 2)
                pygame.draw.circle(self.screen, eye, (pixel_x + 4, pixel_y - 1), 2)
            pygame.draw.circle(self.screen, cheek, (pixel_x - 7, pixel_y + 4), 2)
            pygame.draw.circle(self.screen, cheek, (pixel_x + 7, pixel_y + 4), 2)
            if is_respawning:
                pygame.draw.arc(
                    self.screen,
                    eye,
                    (pixel_x - 4, pixel_y + 4, 8, 6),
                    3.14,
                    6.28,
                    1,
                )
            elif ghost.is_frightened():
                pygame.draw.ellipse(
                    self.screen,
                    eye,
                    (pixel_x - 2, pixel_y + 3, 4, 3),
                    1,
                )
            else:
                pygame.draw.arc(
                    self.screen,
                    eye,
                    (pixel_x - 4, pixel_y, 8, 7),
                    0,
                    3.14,
                    1,
                )

            bow_center = (pixel_x + 5, pixel_y - radius + 3)
            pygame.draw.circle(self.screen, bow, bow_center, 2)
            pygame.draw.circle(self.screen, bow, (bow_center[0] - 3, bow_center[1]), 3)
            pygame.draw.circle(self.screen, bow, (bow_center[0] + 3, bow_center[1]), 3)
            pygame.draw.circle(self.screen, shine, bow_center, 1)

    def draw_hud(self, game_engine: Any) -> None:
        """Draw heads-up display."""
        hud_y = 10
        hud_text_color = COLOR_TEXT_DARK

        # Level
        level_text = self.font_small.render(
            f"Level: {game_engine.get_current_level_number()}",
            True,
            hud_text_color
        )
        self.screen.blit(level_text, (UI_PADDING, hud_y))

        # Score
        score_text = self.font_small.render(
            f"Score: {game_engine.get_player_score()}",
            True,
            hud_text_color
        )
        self.screen.blit(score_text, (UI_PADDING, hud_y + 35))

        # Lives
        lives_text = self.font_small.render(
            f"Lives: {game_engine.get_player_lives()}",
            True,
            hud_text_color
        )
        self.screen.blit(lives_text, (UI_PADDING + 300, hud_y))

        # Time
        time_text = self.font_small.render(
            f"Time: {game_engine.get_time_remaining()}s",
            True,
            hud_text_color
        )
        self.screen.blit(time_text, (UI_PADDING + 300, hud_y + 35))

    def draw_main_menu(self) -> None:
        """Draw main menu."""
        self.screen.fill(COLOR_BACKGROUND)

        title = self.font_large.render(
            "🎀 Hello Kitty Maze 🎀",
            True,
            COLOR_TEXT_DARK
        )
        title_rect = title.get_rect(center=(WINDOW_WIDTH // 2, 150))
        self.screen.blit(title, title_rect)

        subtitle = self.font_small.render(
            "Collect every pacgum and dodge the ghosts",
            True,
            COLOR_TEXT
        )
        subtitle_rect = subtitle.get_rect(center=(WINDOW_WIDTH // 2, 210))
        self.screen.blit(subtitle, subtitle_rect)

        self._draw_button_label("SPACE  Start", (WINDOW_WIDTH // 2, 340))
        self._draw_button_label("H  Highscores", (WINDOW_WIDTH // 2, 415))
        self._draw_button_label("I  Instructions", (WINDOW_WIDTH // 2, 490))

        quit_text = self.font_small.render("Q  Quit", True, COLOR_TEXT_DARK)
        quit_rect = quit_text.get_rect(center=(WINDOW_WIDTH // 2, 625))
        self.screen.blit(quit_text, quit_rect)

    def draw_pause_menu(self) -> None:
        """Draw pause menu."""
        # Semi-transparent overlay
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
        overlay.fill((90, 45, 70, 150))
        self.screen.blit(overlay, (0, 0))

        panel = pygame.Rect(0, 0, 440, 290)
        panel.center = (WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2)
        pygame.draw.rect(self.screen, (255, 252, 254), panel, border_radius=24)
        pygame.draw.rect(self.screen, COLOR_WALL_DARK, panel, 3, border_radius=24)

        pause_text = self.font_large.render(
            "PAUSED",
            True,
            COLOR_TEXT_DARK
        )
        pause_rect = pause_text.get_rect(center=(WINDOW_WIDTH // 2, panel.top + 70))
        self.screen.blit(pause_text, pause_rect)

        self._draw_button_label(
            "SPACE  Resume",
            (WINDOW_WIDTH // 2, panel.top + 150),
            320,
            48,
        )
        self._draw_button_label(
            "M  Main Menu",
            (WINDOW_WIDTH // 2, panel.top + 215),
            320,
            48,
        )

    def draw_game_over(self, score: int) -> None:
        """Draw game over screen."""
        self.screen.fill(COLOR_BACKGROUND)

        # Game Over text
        gameover_text = self.font_large.render(
            "GAME OVER",
            True,
            COLOR_TEXT_DARK
        )
        gameover_rect = gameover_text.get_rect(center=(WINDOW_WIDTH // 2, 200))
        self.screen.blit(gameover_text, gameover_rect)

        # Score
        score_text = self.font_medium.render(
            f"Final Score: {score}",
            True,
            COLOR_TEXT
        )
        score_rect = score_text.get_rect(center=(WINDOW_WIDTH // 2, 350))
        self.screen.blit(score_text, score_rect)

        # Instructions
        enter_text = self.font_small.render(
            "Press ENTER to save your score",
            True,
            COLOR_TEXT
        )
        enter_rect = enter_text.get_rect(center=(WINDOW_WIDTH // 2, 450))
        self.screen.blit(enter_text, enter_rect)

    def draw_victory(self, score: int) -> None:
        """Draw victory screen."""
        self.screen.fill(COLOR_BACKGROUND)

        # Victory text
        victory_text = self.font_large.render(
            "🎉 YOU WIN! 🎉",
            True,
            COLOR_TEXT_DARK
        )
        victory_rect = victory_text.get_rect(center=(WINDOW_WIDTH // 2, 200))
        self.screen.blit(victory_text, victory_rect)

        # Score
        score_text = self.font_medium.render(
            f"Final Score: {score}",
            True,
            COLOR_TEXT
        )
        score_rect = score_text.get_rect(center=(WINDOW_WIDTH // 2, 350))
        self.screen.blit(score_text, score_rect)

        # Instructions
        enter_text = self.font_small.render(
            "Press ENTER to save your score",
            True,
            COLOR_TEXT
        )
        enter_rect = enter_text.get_rect(center=(WINDOW_WIDTH // 2, 450))
        self.screen.blit(enter_text, enter_rect)

    def draw_text_input(self, text: str, prompt: str = "Name") -> None:
        """
        Draw centered name-entry modal.

        Args:
            text: Current input text
            prompt: Input prompt
        """
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
        overlay.fill((90, 45, 70, 120))
        self.screen.blit(overlay, (0, 0))

        modal = pygame.Rect(0, 0, 520, 280)
        modal.center = (WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2)
        shadow = modal.move(0, 6)
        pygame.draw.rect(self.screen, (245, 180, 205), shadow, border_radius=28)
        pygame.draw.rect(self.screen, (255, 252, 254), modal, border_radius=28)
        pygame.draw.rect(self.screen, COLOR_WALL_DARK, modal, 3, border_radius=28)

        title = self.font_medium.render("Enter Your Name", True, COLOR_TEXT_DARK)
        self.screen.blit(title, title.get_rect(center=(modal.centerx, modal.top + 58)))

        label = self.font_small.render(
            f"{prompt} (max 10 characters)",
            True,
            COLOR_TEXT,
        )
        self.screen.blit(label, label.get_rect(center=(modal.centerx, modal.top + 100)))

        input_box = pygame.Rect(0, 0, 360, 54)
        input_box.center = (modal.centerx, modal.top + 150)
        pygame.draw.rect(self.screen, (255, 244, 249), input_box, border_radius=16)
        pygame.draw.rect(self.screen, COLOR_TEXT, input_box, 2, border_radius=16)

        display_text = text if text else "Type here"
        text_color = COLOR_TEXT_DARK if text else (185, 130, 155)
        cursor = "|" if pygame.time.get_ticks() // 450 % 2 == 0 else ""
        typed = self.font_medium.render(display_text + cursor, True, text_color)
        typed_rect = typed.get_rect(midleft=(input_box.left + 18, input_box.centery))
        self.screen.blit(typed, typed_rect)

        hint = self.font_small.render("ENTER  Confirm", True, COLOR_TEXT_DARK)
        self.screen.blit(hint, hint.get_rect(center=(modal.centerx, modal.bottom - 42)))

    def draw_highscores(self, highscores: List[Dict[str, Any]]) -> None:
        """Draw highscores screen."""
        self.screen.fill(COLOR_BACKGROUND)

        # Title
        title = self.font_large.render(
            "🏆 Highscores 🏆",
            True,
            COLOR_TEXT_DARK
        )
        title_rect = title.get_rect(center=(WINDOW_WIDTH // 2, 50))
        self.screen.blit(title, title_rect)

        # Highscores
        y_pos = 150
        for i, score_entry in enumerate(highscores[:10], 1):
            score_line = (
                f"{i}. {score_entry['name']:<20} "
                f"{score_entry['score']:>8} "
                f"(Level {score_entry['level']})"
            )
            score_text = self.font_small.render(score_line, True, COLOR_TEXT)
            self.screen.blit(score_text, (UI_PADDING, y_pos))
            y_pos += 40

        # Back instruction
        back_text = self.font_small.render(
            "Press SPACE to return to menu",
            True,
            COLOR_TEXT
        )
        back_rect = back_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT - 50))
        self.screen.blit(back_text, back_rect)

    def draw_instructions(self) -> None:
        """Draw instructions screen."""
        self.screen.fill(COLOR_BACKGROUND)

        # Title
        title = self.font_large.render(
            "📖 Instructions 📖",
            True,
            COLOR_TEXT_DARK
        )
        title_rect = title.get_rect(center=(WINDOW_WIDTH // 2, 30))
        self.screen.blit(title, title_rect)

        # Instructions
        instructions = [
            "Arrow Keys or WASD: Move",
            "Space: Pause/Resume",
            "M: Return to Menu",
            "",
            "Collect pacgums for points",
            "Collect power pellets to eat ghosts",
            "Avoid ghosts or you lose a life",
            "Collect all pacgums to win the level",
            "",
            "Cheat Mode (for testing):",
            "I: Toggle Invincibility",
            "N: Skip Level",
            "F: Freeze Ghosts",
            "L: Extra Life",
            "T: Speed Boost",
        ]

        y_pos = 120
        for instruction in instructions:
            if instruction:
                instr_text = self.font_small.render(instruction, True, COLOR_TEXT)
            else:
                instr_text = pygame.Surface((0, 0))
            self.screen.blit(instr_text, (UI_PADDING + 20, y_pos))
            y_pos += 35

        # Back instruction
        back_text = self.font_small.render(
            "Press SPACE to return to menu",
            True,
            COLOR_TEXT
        )
        back_rect = back_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT - 50))
        self.screen.blit(back_text, back_rect)

    def clear_screen(self) -> None:
        """Clear the screen."""
        self.screen.fill(COLOR_BACKGROUND)

    def flip_display(self) -> None:
        """Update display."""
        try:
            pygame.display.flip()
        except pygame.error:
            # Display not available, continue anyway
            pass

    def tick(self, fps: int = FPS) -> float:
        """
        Tick the clock.

        Args:
            fps: Frames per second

        Returns:
            Delta time in seconds
        """
        try:
            return float(self.clock.tick(fps)) / 1000.0
        except Exception:
            # Fallback if clock fails
            return 1.0 / fps

    def quit(self) -> None:
        """Quit pygame."""
        pygame.quit()
