# Building tsnake

## Prerequisites

To create a compiled executable version of tsnake, you need PyInstaller.

### Option 1: System Package Manager (Recommended)

```bash
sudo apt update
sudo apt install python3-pyinstaller
```

### Option 2: pip with --break-system-packages

```bash
python3 -m pip install --user --break-system-packages pyinstaller
```

### Option 3: Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate
pip install pyinstaller
# Build the executable
pyinstaller --onefile --name tsnake --clean tsnake.py
deactivate
```

## Building

### Option 1: Using virtual environment (Recommended - avoids permission issues)

```bash
./build-venv.sh
```

This creates a virtual environment, installs PyInstaller there, and builds the executable.

### Option 2: Using system package manager

```bash
sudo apt update
sudo apt install python3-pyinstaller
./build.sh
```

### Option 3: Using build script with --break-system-packages

```bash
python3 -m pip install --user --break-system-packages pyinstaller
./build.sh
```

### Option 4: Manual build

```bash
python3 -m PyInstaller --onefile --name tsnake --clean tsnake.py
```

The compiled executable will be created in the `dist/` directory as `tsnake`.

## Running the compiled version

```bash
./dist/tsnake
```

## Installing system-wide (optional)

```bash
sudo cp dist/tsnake /usr/local/bin/
```

After installation, you can run tsnake from anywhere:

```bash
tsnake
```

## Notes

- The compiled executable is standalone and doesn't require Python to be installed
- It includes all dependencies (curses, etc.)
- The executable size will be larger than the Python script (~5-10MB)
- Works on Linux systems with the same architecture

