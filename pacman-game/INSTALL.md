# Installation Guide

## System Requirements

- Python 3.9 or higher
- pip (Python package manager)
- 1200x900 minimum screen resolution
- 256MB RAM minimum

## Installation Steps

### 1. Download and Extract

Download the `pacman-game.zip` file and extract it:

```bash
unzip pacman-game.zip
cd pacman-game
```

### 2. Create Virtual Environment (Recommended)

It's recommended to create a Python virtual environment to avoid conflicts with other packages:

```bash
# On Linux/macOS
python3 -m venv venv
source venv/bin/activate

# On Windows
python -m venv venv
venv\Scripts\activate
```

### 3. Install Dependencies

Install required Python packages:

```bash
pip install -r requirements.txt
```

This will install:
- pygame >= 2.1.0

### 4. Verify Installation

To verify everything is installed correctly:

```bash
python -c "import pygame; print(f'Pygame {pygame.ver} installed successfully')"
```

## Running the Game

### Method 1: Direct Execution

```bash
python3 pac-man.py config/game_config.json
```

### Method 2: Using Console Script (after pip install -e .)

```bash
pip install -e .
hello-kitty-maze
```

## Troubleshooting

### Issue: "No module named 'pygame'"

**Solution**: Install pygame
```bash
pip install pygame
```

### Issue: "ModuleNotFoundError: No module named 'mazegenerator'"

**Solution**: Ensure the `mazegenerator-00001-py3-none-any` directory is in the game folder

### Issue: "DISPLAY" error on Linux

**Solution**: You need an X11 display. If running remotely, use X11 forwarding:
```bash
ssh -X user@host
```

### Issue: Window appears but is very slow

**Solution**:
- Close other applications
- Lower graphics quality (edit `config/game_config.json`)
- Update graphics drivers

## Uninstallation

To remove the game:

```bash
# If installed in development mode
pip uninstall hello-kitty-maze

# Delete the game folder
rm -rf pacman-game
```

## Development Installation

For development/testing:

```bash
# Install in development mode with test dependencies
pip install -e ".[dev]"

# Run tests
python -m pytest tests/

# Run with debugging
DEBUG=1 python3 pac-man.py config/game_config.json
```

## Notes

- The first time you run the game, it will create a `config/highscores.json` file
- Game settings can be modified in `config/game_config.json`
- The game requires pygame and will download it automatically via pip

## Support

If you encounter any issues:

1. Check that Python 3.9+ is installed: `python --version`
2. Verify pygame is installed: `pip list | grep pygame`
3. Check that all files are extracted correctly
4. Try reinstalling: `pip install --upgrade -r requirements.txt`

For more information, see the README.md file.
