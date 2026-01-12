#!/bin/bash
# Build script for tsnake using virtual environment - avoids externally-managed-environment issues

echo "Building tsnake executable using virtual environment..."

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install PyInstaller in virtual environment
if ! python -m pip show pyinstaller &> /dev/null; then
    echo "Installing PyInstaller..."
    pip install pyinstaller
fi

# Build the executable
echo "Compiling tsnake..."
pyinstaller --onefile --name tsnake --clean tsnake.py

BUILD_RESULT=$?

# Deactivate virtual environment
deactivate

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
    echo ""
    echo "Note: The venv/ directory can be deleted after building if desired."
else
    echo "Build failed!"
    exit 1
fi

