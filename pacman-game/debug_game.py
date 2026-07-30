#!/usr/bin/env python3
"""Debug version of the game with extensive logging."""

import sys
from pathlib import Path

# Add src to path
SRC_PATH = Path(__file__).parent / "src"
if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

import pygame
from pygame.locals import (
    KEYDOWN,
    K_DOWN,
    K_ESCAPE,
    K_LEFT,
    K_RIGHT,
    K_SPACE,
    K_UP,
    K_a,
    K_d,
    K_q,
    K_s,
    K_w,
    QUIT,
)

print("📋 Starting Debug Game...")

try:
    from game import GameEngine, Direction
    print("✅ GameEngine imported")

    from ui import GameDisplay
    print("✅ GameDisplay imported")

    from utils.constants import (
        STATE_MENU,
        STATE_PLAYING,
    )
    print("✅ Constants imported")

except Exception as e:
    print(f"❌ Import error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)


class DebugGameApplication:
    """Debug game with logging."""

    def __init__(self):
        """Initialize the game application."""
        print("🎮 Initializing GameEngine...")
        self.engine = GameEngine()
        print("✅ GameEngine ready")

        print("🎨 Initializing GameDisplay...")
        self.display = GameDisplay()
        print("✅ GameDisplay ready")

        self.running = True
        self.clock = pygame.time.Clock()
        self.player_name = ""
        self.input_mode = False
        self.frame_count = 0
        self.event_count = 0

    def handle_events(self) -> None:
        """Handle input events."""
        events = pygame.event.get()
        if events:
            self.event_count += len(events)
            print(f"📨 Got {len(events)} event(s) (total: {self.event_count})")

        for event in events:
            if event.type == QUIT:
                print("🚪 QUIT event received")
                self.running = False

            elif event.type == KEYDOWN:
                print(f"⌨️  KEYDOWN: key={event.key}, unicode={event.unicode}")

                if self.input_mode:
                    print("   → Text input mode")
                elif self.engine.state == STATE_MENU:
                    print("   → Menu input")
                    if event.key == K_SPACE:
                        print("   → SPACE pressed, starting game")
                        self.engine.start_new_game()
                    elif event.key == K_q or event.key == K_ESCAPE:
                        print("   → Quit key pressed")
                        self.running = False
                elif self.engine.state == STATE_PLAYING:
                    print("   → Game input")
                    if event.key == K_UP or event.key == K_w:
                        print("   → Move UP")
                        self.engine.set_player_direction(Direction.UP)
                    elif event.key == K_DOWN or event.key == K_s:
                        print("   → Move DOWN")
                        self.engine.set_player_direction(Direction.DOWN)
                    elif event.key == K_LEFT or event.key == K_a:
                        print("   → Move LEFT")
                        self.engine.set_player_direction(Direction.LEFT)
                    elif event.key == K_RIGHT or event.key == K_d:
                        print("   → Move RIGHT")
                        self.engine.set_player_direction(Direction.RIGHT)
                    elif event.key == K_SPACE:
                        print("   → Pause")
                        self.engine.pause_game()
            else:
                print(f"   → Other event: {event.type}")

    def update(self, delta_time: float) -> None:
        """Update game logic."""
        self.engine.update(delta_time)

    def render(self) -> None:
        """Render the game."""
        self.display.clear_screen()

        if self.engine.state == STATE_MENU:
            self.display.draw_main_menu()
        elif self.engine.state == STATE_PLAYING:
            level = self.engine.get_current_level()
            if level:
                self.display.draw_maze(level.maze)
            self.display.draw_player(self.engine.get_player())
            self.display.draw_hud(self.engine)

        self.display.flip_display()

    def run(self) -> None:
        """Main game loop."""
        print("\n" + "="*50)
        print("🎀 Hello Kitty Maze Game - DEBUG MODE 🎀")
        print("="*50)
        print("Controls: SPACE to start, arrow keys to move, Q to quit")
        print("="*50 + "\n")

        frame_count = 0
        try:
            while self.running:
                frame_count += 1

                try:
                    delta_time = self.display.tick(60)

                    if frame_count % 60 == 0:
                        print(
                            f"📊 Frame {frame_count}, "
                            f"State: {self.engine.state}, "
                            f"Events: {self.event_count}"
                        )

                    self.handle_events()
                    self.update(delta_time)
                    self.render()

                except Exception as e:
                    print(f"❌ Error in frame {frame_count}: {e}")
                    import traceback
                    traceback.print_exc()
                    break

        except KeyboardInterrupt:
            print("\n⚠️  Game interrupted by user")
        except Exception as e:
            print(f"❌ Fatal error: {e}")
            import traceback
            traceback.print_exc()
        finally:
            print(f"\n📊 Final stats: {frame_count} frames, {self.event_count} events")
            self.display.quit()
            print("Game ended. Thanks for playing! 🎀")


def main():
    """Entry point."""
    app = DebugGameApplication()
    app.run()


if __name__ == "__main__":
    main()
