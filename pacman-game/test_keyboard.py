#!/usr/bin/env python3
"""Simple test to verify the game works with proper input."""

import sys
from pathlib import Path

SRC_PATH = Path(__file__).parent / "src"
if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

import pygame
from pygame.locals import KEYDOWN, QUIT

# Minimal test
print("🎮 Pygame Keyboard Input Test\n")
print("=" * 50)

pygame.init()
screen = pygame.display.set_mode((600, 400))
pygame.display.set_caption("Press any key!")

clock = pygame.time.Clock()
running = True
key_pressed = None

print("✅ Display created - window should appear")
print("✅ Try pressing keys...\n")

frame = 0
while running and frame < 300:  # Run for 5 seconds at 60 FPS
    frame += 1

    for event in pygame.event.get():
        if event.type == QUIT:
            running = False
        elif event.type == KEYDOWN:
            key_pressed = pygame.key.name(event.key)
            print(f"⌨️  KEY PRESSED: {key_pressed}")

    # Display feedback
    screen.fill((50, 50, 50))

    if key_pressed:
        text = pygame.font.Font(None, 48).render(
            f"You pressed: {key_pressed}", True, (0, 255, 0)
        )
    else:
        text = pygame.font.Font(None, 48).render(
            "Press any key!", True, (255, 255, 255)
        )

    screen.blit(text, text.get_rect(center=(300, 200)))
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
print("\n✅ Test complete!")
print("If you saw a window and could press keys, the game will work fine!")
