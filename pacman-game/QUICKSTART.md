# Quick Start Guide

## 🎀 Hello Kitty Maze Game - 5 Minute Setup

### Step 1: Extract the ZIP (30 seconds)
```bash
unzip pacman-game.zip
cd pacman-game
```

### Step 2: Install Python Dependencies (2 minutes)
```bash
pip install -r requirements.txt
```

### Step 3: Run the Game! (Instant)
```bash
python3 pac-man.py config/game_config.json
```

That's it! The game should start immediately.

---

## 🎮 How to Play

### Controls
- **Arrow Keys** or **WASD**: Move the player
- **Space**: Pause/Resume
- **M**: Return to menu

### Goal
- Collect all the pink dots (pacgums) in the maze
- Avoid the ghosts!
- Collect the large dots (power pellets) to eat ghosts
- Complete all 15 levels

### Scoring
- **Pacgum**: 10 points
- **Power Pellet**: 50 points
- **Eating Ghost**: 200-1600 points (depends on combo)

---

## 🎯 Tips for Success

1. **Learn the Maze**: Take time to understand the maze layout
2. **Plan Your Route**: Decide where to collect pacgums before moving
3. **Avoid Ghosts**: Don't get cornered - always have an escape route
4. **Use Power Pellets**: Eat a power pellet when surrounded by ghosts
5. **Stay Calm**: Panic often leads to mistakes

---

## 🛠️ Troubleshooting

### Game Won't Start
```
Error: No module named 'pygame'
→ Run: pip install pygame
```

### Game Runs Slowly
- Close other applications
- Check your screen resolution (should be 1200x900+)
- Update graphics drivers

### Fullscreen Issues
- Game runs in windowed mode by default
- You can resize the window normally

---

## 🎨 Game Features

✨ **15 Levels** - Progressive difficulty
🎀 **Hello Kitty Theme** - Pastel pink aesthetic
👻 **4 Intelligent Ghosts** - Realistic chase behavior
🏆 **Highscore System** - Save your best scores
🎮 **Cheat Mode** - Test features easily

---

## 📚 More Information

- Full documentation: See **README.md**
- Installation guide: See **INSTALL.md**
- Project details: See **docs/PROJECT_MANAGEMENT.md**
- Code: Explore **src/** directory

---

## 🚀 Cheat Mode (for Testing)

While playing, press:
- **I** - Invincibility
- **N** - Skip Level
- **F** - Freeze Ghosts
- **L** - Extra Life
- **T** - Speed Boost

---

## 📞 Need Help?

1. Check **INSTALL.md** for detailed installation steps
2. Read **README.md** for complete documentation
3. Ensure Python 3.9+ is installed: `python --version`
4. Verify pygame is installed: `pip list | grep pygame`

---

🎀 **Enjoy the game!** 🎀

Happy gaming! If you complete all 15 levels, take a screenshot and share your score!
