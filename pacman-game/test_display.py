#!/usr/bin/env python3
"""Test if display is available."""

import os
import sys

print("🔍 Checking Display Configuration...")
print()

# Check DISPLAY variable
display = os.environ.get('DISPLAY')
print(f"DISPLAY env var: {display if display else '❌ NOT SET'}")

# Check if X11 is available
try:
    import subprocess
    result = subprocess.run(['xdpyinfo'], capture_output=True, timeout=2)
    if result.returncode == 0:
        print("✅ X11 Display Server: FOUND")
    else:
        print("❌ X11 Display Server: NOT RESPONDING")
except Exception as e:
    print(f"❌ X11 Display Server: {e}")

print()
print("🔍 Checking Pygame...")

try:
    import pygame
    print("✅ Pygame imported successfully")

    # Try to initialize pygame
    pygame.init()
    print("✅ Pygame initialized")

    # Try to create a display
    pygame.display.set_mode((100, 100))
    print("✅ Display created successfully!")
    pygame.quit()
    print("")
    print("✨ DISPLAY WORKING - Game should run! ✨")

except Exception as e:
    print(f"❌ Pygame error: {e}")
    print("")
    print("❌ DISPLAY NOT AVAILABLE")
    print("")
    print("SOLUTIONS:")
    print("")
    print("1️⃣  If using SSH:")
    print("   ssh -X user@hostname")
    print("")
    print("2️⃣  If on headless server, use virtual display:")
    print("   export DISPLAY=:99")
    print("   Xvfb :99 -screen 0 1200x900x24 &")
    print("")
    print("3️⃣  Check current DISPLAY setting:")
    print(f"   Current: {os.environ.get('DISPLAY', 'NOT SET')}")
    print("")
    sys.exit(1)
