# Running on Remote Server / Headless System

If you're running the game on a remote Linux server or a system without a graphical display, you have several options:

## Option 1: SSH X11 Forwarding (Recommended)

If you're connecting via SSH, simply add the `-X` flag to enable X11 forwarding:

```bash
ssh -X user@hostname
cd pacman-game
pip install -r requirements.txt
python src/game/main.py
```

This will display the game window on your local machine while running on the remote server.

## Option 2: Virtual Display (Xvfb)

If X11 forwarding isn't available, you can create a virtual display:

```bash
# Install Xvfb if not already installed
sudo apt-get install xvfb

# Create virtual display
export DISPLAY=:99
Xvfb :99 -screen 0 1200x900x24 &

# Run the game
python src/game/main.py
```

Then use a VNC client to view the virtual display.

## Option 3: VNC Remote Desktop

Set up a VNC server on the remote machine:

```bash
# Install VNC server
sudo apt-get install tightvncserver

# Start VNC server
vncserver :1

# Connect from your local machine
vncviewer hostname:1
```

Then run the game normally.

## Option 4: Wayland Display Server

If you have Wayland available:

```bash
export WAYLAND_DISPLAY=wayland-0
python src/game/main.py
```

## Option 5: Browser-based (Future Feature)

The game is built with Pygame, which requires a display. For a web-based version, consider using Pygame to Canvas conversion or Pyglet with WebGL in the future.

## Troubleshooting

### "No X11 display found" Error

This means Pygame can't find a graphical display. Use one of the options above.

### Window appears frozen/unresponsive

- Make sure you're using X11 forwarding or a virtual display
- Check your SSH connection is still active
- Ensure DISPLAY environment variable is set: `echo $DISPLAY`

### Performance Issues

- Virtual displays may be slower - reduce window size if needed
- Use faster X11 forwarding: `ssh -C -X` (compression)

## Environment Variables

```bash
# Check current display
echo $DISPLAY

# Set display manually
export DISPLAY=:0
export DISPLAY=localhost:10.0

# Check if display is working
xdpyinfo -display $DISPLAY
```

## Running Tests Only (No Display Needed)

If you only want to run tests without a display:

```bash
python -m pytest tests/ -v
```

## Native Running (Local Machine)

If running on a local machine with a graphical desktop:

```bash
python src/game/main.py
```

Should work immediately!

---

For more details, see **README.md** and **INSTALL.md**.
