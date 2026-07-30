#!/usr/bin/env python3
"""Test different maze generator settings."""

import sys
from pathlib import Path

MAZE_GEN_PATH = Path(__file__).parent / "mazegenerator-00001-py3-none-any"
sys.path.insert(0, str(MAZE_GEN_PATH))

from mazegenerator import MazeGenerator
import signal


def timeout_handler(signum, frame):
    raise TimeoutError("Maze generation timed out!")


print("🧪 Testing MazeGenerator Settings\n")
print("=" * 50)

# Test 1: Original settings (seed=42, perfect=False, size=25x25)
print("\n1️⃣  Trying: seed=42, perfect=False, size=25x25")
signal.signal(signal.SIGALRM, timeout_handler)
signal.alarm(3)  # 3 second timeout
try:
    gen = MazeGenerator(size=(25, 25), perfect=False, seed=42)
    signal.alarm(0)
    print("   ✅ SUCCESS!")
except TimeoutError:
    print("   ❌ HANGS (timeout after 3s)")
    signal.alarm(0)

# Test 2: Without seed
print("\n2️⃣  Trying: seed=None, perfect=False, size=25x25")
signal.alarm(3)
try:
    gen = MazeGenerator(size=(25, 25), perfect=False)
    signal.alarm(0)
    print("   ✅ SUCCESS!")
except TimeoutError:
    print("   ❌ HANGS")
    signal.alarm(0)

# Test 3: Perfect maze with seed
print("\n3️⃣  Trying: seed=42, perfect=True, size=25x25")
signal.alarm(3)
try:
    gen = MazeGenerator(size=(25, 25), perfect=True, seed=42)
    signal.alarm(0)
    print("   ✅ SUCCESS!")
except TimeoutError:
    print("   ❌ HANGS")
    signal.alarm(0)

# Test 4: Perfect maze no seed
print("\n4️⃣  Trying: seed=None, perfect=True, size=25x25")
signal.alarm(3)
try:
    gen = MazeGenerator(size=(25, 25), perfect=True)
    signal.alarm(0)
    print("   ✅ SUCCESS!")
except TimeoutError:
    print("   ❌ HANGS")
    signal.alarm(0)

# Test 5: Smaller maze
print("\n5️⃣  Trying: seed=42, perfect=False, size=15x15")
signal.alarm(3)
try:
    gen = MazeGenerator(size=(15, 15), perfect=False, seed=42)
    signal.alarm(0)
    print("   ✅ SUCCESS!")
except TimeoutError:
    print("   ❌ HANGS")
    signal.alarm(0)

print("\n" + "=" * 50)
print("Done!")
