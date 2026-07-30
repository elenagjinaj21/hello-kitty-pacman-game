#!/usr/bin/env python3
"""Test maze generator initialization."""

import sys
from pathlib import Path

print("🔍 Testing Maze Generator...\n")

# Add maze generator to path
MAZE_GEN_PATH = Path(__file__).parent / "mazegenerator-00001-py3-none-any"
print(f"Looking for maze generator at: {MAZE_GEN_PATH}")
print(f"Exists: {MAZE_GEN_PATH.exists()}")

if MAZE_GEN_PATH not in sys.path:
    sys.path.insert(0, str(MAZE_GEN_PATH))

try:
    print("\n1️⃣  Importing MazeGenerator...")
    from mazegenerator import MazeGenerator
    print("   ✅ Import successful")
except ImportError as e:
    print(f"   ❌ Import failed: {e}")
    sys.exit(1)

try:
    print("\n2️⃣  Creating maze generator...")
    gen = MazeGenerator(size=(25, 25), perfect=False, seed=42)
    print("   ✅ MazeGenerator created")
except Exception as e:
    print(f"   ❌ MazeGenerator creation failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

try:
    print("\n3️⃣  Accessing maze grid...")
    maze = gen.maze
    print(f"   ✅ Maze grid accessed: {len(maze)}x{len(maze[0])} cells")
except Exception as e:
    print(f"   ❌ Maze grid access failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

try:
    print("\n4️⃣  Accessing entry/exit...")
    entry = gen.maze_entry
    exit_pos = gen.maze_exit
    print(f"   ✅ Entry: {entry}, Exit: {exit_pos}")
except Exception as e:
    print(f"   ❌ Entry/exit access failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n✨ Maze generator works perfectly!")
