# tsnake 🐍

A classic Snake game implemented in **Python** and **C** for the terminal, featuring a welcome screen, smooth gameplay, and increasing difficulty.

## Features

- 🎮 Classic Snake gameplay
- 🎨 Colorful terminal interface
- 📊 Score tracking with high score
- ⚡ Increasing speed as you progress
- 🎯 Welcome screen with instructions
- 🎪 Game over screen with replay option
- ⌨️ Multiple control options (Arrow keys or WASD)

## Requirements

### Python Version
- Python 3.6 or higher
- Terminal with curses support (included in most Linux/Unix systems)

### C Version
- GCC compiler
- ncurses development library (`libncurses-dev` on Debian/Ubuntu)
- Terminal size: Minimum 24x24 characters (recommended: 30x40 or larger)

## Installation

No additional packages required! The game uses Python's built-in `curses` library.

```bash
# Clone or download the repository
cd tsnake

# Make the script executable (optional)
chmod +x tsnake.py
```

## How to Run

### Python Script Version

```bash
python3 tsnake.py
```

Or if you made it executable:

```bash
./tsnake.py
```

### C Version (Recommended for Performance)

First, install ncurses development library:

```bash
sudo apt install libncurses-dev
```

Then build and run:

```bash
make
./tsnake
```

Or install system-wide:

```bash
sudo make install
tsnake
```

### Python Compiled Executable Version

To build the compiled Python version, see [BUILD.md](BUILD.md) for instructions.

After building:

```bash
./dist/tsnake
```

## Controls

- **Arrow Keys** or **WASD** - Move the snake
  - ↑/W - Move up
  - ↓/S - Move down
  - ←/A - Move left
  - →/D - Move right
- **Q** - Quit during gameplay
- **R** - Restart after game over
- **Q** - Quit after game over

## Gameplay

1. Start the game and read the welcome screen
2. Use arrow keys or WASD to control your snake
3. Eat the food (🍎) to grow and increase your score
4. Avoid hitting the walls or your own tail
5. The game gets progressively faster as you eat more food
6. Try to beat your high score!

## Scoring

- Each food eaten: **10 points**
- High score is tracked during your session
- Game speed increases slightly with each food eaten

## Tips

- Plan your moves ahead to avoid getting trapped
- Use the full game area efficiently
- The snake moves continuously, so be careful with direction changes
- Start slow and get used to the controls before going for high scores

## Troubleshooting

**Terminal too small error:**
- Resize your terminal window to at least 24x24 characters
- Recommended size: 30x40 or larger for best experience

**Colors not displaying:**
- Some terminals may not support colors, but the game will still work
- Try using a different terminal emulator if colors are important

**Emoji not displaying:**
- The game will automatically fall back to '*' if emojis aren't supported
- This doesn't affect gameplay

## License

Free to use and modify!

## Enjoy! 🎮

Have fun playing Snake! Try to beat your high score!

