# Asset Placeholder Directory

Author: egjinaj shajdar

This directory contains game sprites and visual assets.

## Current Assets

### Sprites
- Player sprites (Hello Kitty inspired)
- Ghost sprites (4 different colored ghosts)
- Collectible sprites (pacgums, power pellets, hearts, bows, strawberries)
- UI elements

### Fonts
- Game font (used for score, menus, HUD)

### Sounds (Future)
- Pacgum collection sound
- Power-up sound
- Ghost eaten sound
- Level complete sound
- Game over sound

## Asset Format

- Sprites: PNG format (32x32 or 48x48 pixels recommended)
- Fonts: TTF (TrueType Font) format
- Sounds: WAV or MP3 format

## Currently Used

The game currently uses procedural rendering (geometric shapes) for all visuals:
- Player: Pink circle with eyes
- Ghosts: Pink circles with eyes (blue when frightened)
- Pacgums: Small pink dots
- Super-pacgums: Larger pink dots
- Maze walls: Pink lines

This placeholder system allows the game to run without external assets while maintaining the Hello Kitty aesthetic through color choices (pastel pink palette).

## To Add Custom Assets

1. Create sprite images in `sprites/`
2. Create font files in `fonts/`
3. Update `AssetManager` class to load assets
4. Update `GameDisplay` rendering methods to use loaded assets

## Recommended Asset Sizes

- Sprites: 32x32 pixels (tile size)
- UI Elements: 64x64 pixels
- Fonts: 24pt, 32pt, 48pt sizes
