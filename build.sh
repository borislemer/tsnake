#!/bin/bash
# Build script for tsnake - creates a compiled executable

echo "Building tsnake executable..."

# Try to use system PyInstaller first
if command -v pyinstaller &> /dev/null; then
    echo "Using system PyInstaller..."
    pyinstaller --onefile --name tsnake --clean tsnake.py
    BUILD_RESULT=$?
elif python3 -m PyInstaller --version &> /dev/null; then
    echo "Using PyInstaller from Python modules..."
    python3 -m PyInstaller --onefile --name tsnake --clean tsnake.py
    BUILD_RESULT=$?
else
    echo "PyInstaller not found. Attempting to install..."
    
    # Try installing with --break-system-packages
    python3 -m pip install --user --break-system-packages pyinstaller 2>/dev/null || {
        echo ""
        echo "Failed to install PyInstaller automatically."
        echo ""
        echo "Please install PyInstaller using one of these methods:"
        echo ""
        echo "Option 1: Use system package manager (recommended):"
        echo "  sudo apt update"
        echo "  sudo apt install python3-pyinstaller"
        echo ""
        echo "Option 2: Install with --break-system-packages:"
        echo "  python3 -m pip install --user --break-system-packages pyinstaller"
        echo ""
        echo "Option 3: Use virtual environment:"
        echo "  python3 -m venv venv"
        echo "  source venv/bin/activate"
        echo "  pip install pyinstaller"
        echo "  pyinstaller --onefile --name tsnake --clean tsnake.py"
        echo "  deactivate"
        echo ""
        exit 1
    }
    
    # Try building after installation
    echo "Compiling tsnake..."
    python3 -m PyInstaller --onefile --name tsnake --clean tsnake.py
    BUILD_RESULT=$?
fi

if [ $BUILD_RESULT -eq 0 ]; then
    echo ""
    echo "Build successful!"
    echo "Executable created at: dist/tsnake"
    echo ""
    echo "To run the compiled version:"
    echo "  ./dist/tsnake"
    echo ""
    echo "To copy to a system location (optional):"
    echo "  sudo cp dist/tsnake /usr/local/bin/"
else
    echo "Build failed!"
    exit 1
fi

