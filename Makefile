# Makefile for tsnake (C version)

CC = gcc
CFLAGS = -Wall -Wextra -std=c11 -O2
LIBS = -lncursesw
TARGET = tsnake
SRC = tsnake.c

# Default target
all: $(TARGET)

# Build the executable
$(TARGET): $(SRC)
	$(CC) $(CFLAGS) -o $(TARGET) $(SRC) $(LIBS)

# Clean build artifacts
clean:
	rm -f $(TARGET) *.o

# Install (optional)
install: $(TARGET)
	sudo cp $(TARGET) /usr/local/bin/

# Uninstall (optional)
uninstall:
	sudo rm -f /usr/local/bin/$(TARGET)

# Run the game
run: $(TARGET)
	./$(TARGET)

.PHONY: all clean install uninstall run

