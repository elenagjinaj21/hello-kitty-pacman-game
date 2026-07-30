#!/usr/bin/env python3
"""Required command-line launcher for the game."""

import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent
SRC_PATH = PROJECT_ROOT / "src"
if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))


def main() -> int:
    """Load the requested config and run the game."""
    if len(sys.argv) != 2:
        print("Usage: python3 pac-man.py config.json", file=sys.stderr)
        return 1

    from utils.config_loader import apply_config

    try:
        config = apply_config(sys.argv[1])
    except Exception as exc:
        print(f"Failed to load config: {exc}", file=sys.stderr)
        return 1

    from game.main import GameApplication

    GameApplication(config).run()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
