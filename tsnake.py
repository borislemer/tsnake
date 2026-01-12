#!/usr/bin/env python3
"""
Terminal-based Snake Game
Use arrow keys to control the snake. Eat food to grow and increase your score!
"""

import curses
import random
import time
from enum import Enum
from typing import List, Tuple, Optional


class Direction(Enum):
    """Direction enum for snake movement"""
    UP = (-1, 0)
    DOWN = (1, 0)
    LEFT = (0, -1)
    RIGHT = (0, 1)


class SnakeGame:
    """Main Snake Game class"""
    
    # List of 10 different fruit emojis
    FRUITS = ['🍎', '🍌', '🍇', '🍊', '🍓', '🍑', '🍉', '🥝', '🍒', '🍐']
    
    def __init__(self, stdscr):
        self.stdscr = stdscr
        self.height, self.width = stdscr.getmaxyx()
        
        # Game area (leave space for borders and info)
        self.game_height = self.height - 4
        self.game_width = self.width - 4
        
        # Ensure minimum game size
        if self.game_height < 10 or self.game_width < 20:
            raise ValueError("Terminal too small! Please resize to at least 24x24")
        
        # Initialize game state
        self.score = 0
        self.high_score = 0
        self.direction = Direction.RIGHT
        self.next_direction = Direction.RIGHT
        
        # Initialize snake in the center
        # Playable area is from 1 to game_height-2 (walls at 0 and game_height-1)
        center_y = self.game_height // 2
        center_x = self.game_width // 2
        # Ensure snake starts in playable area
        center_y = max(1, min(center_y, self.game_height - 2))
        center_x = max(1, min(center_x, self.game_width - 2))
        self.snake = [
            (center_y, center_x),
            (center_y, center_x - 1),
            (center_y, center_x - 2)
        ]
        
        # Initialize food (position and type)
        self.food_pos = self.generate_food()
        self.food_index = random.randint(0, len(self.FRUITS) - 1)
        self.food_type = self.FRUITS[self.food_index]
        
        # Game settings
        self.speed = 0.1  # Initial speed (seconds between moves)
        self.speed_increment = 0.005  # Speed increase per food eaten
        
        # Colors - initialize more color pairs for different fruits
        curses.start_color()
        curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_BLACK)  # Snake
        curses.init_pair(2, curses.COLOR_RED, curses.COLOR_BLACK)    # Food - Red
        curses.init_pair(3, curses.COLOR_YELLOW, curses.COLOR_BLACK) # Score
        curses.init_pair(4, curses.COLOR_MAGENTA, curses.COLOR_BLACK) # Border - Distinct
        # Fruit colors
        curses.init_pair(5, curses.COLOR_RED, curses.COLOR_BLACK)     # Red fruit
        curses.init_pair(6, curses.COLOR_YELLOW, curses.COLOR_BLACK)   # Yellow fruit
        curses.init_pair(7, curses.COLOR_GREEN, curses.COLOR_BLACK)    # Green fruit
        curses.init_pair(8, curses.COLOR_BLUE, curses.COLOR_BLACK)     # Blue fruit
        curses.init_pair(9, curses.COLOR_MAGENTA, curses.COLOR_BLACK)  # Magenta fruit
        curses.init_pair(10, curses.COLOR_CYAN, curses.COLOR_BLACK)   # Cyan fruit
        curses.init_pair(11, curses.COLOR_WHITE, curses.COLOR_BLACK)   # White fruit
        
        # Map fruits to colors (10 fruits, 7 colors - some will repeat)
        self.fruit_colors = [
            curses.color_pair(5),   # 🍎 Red
            curses.color_pair(6),   # 🍌 Yellow
            curses.color_pair(7),   # 🍇 Green/Purple
            curses.color_pair(6),   # 🍊 Orange/Yellow
            curses.color_pair(5),   # 🍓 Red
            curses.color_pair(5),   # 🍑 Pink/Red
            curses.color_pair(7),   # 🍉 Green
            curses.color_pair(7),   # 🥝 Green
            curses.color_pair(5),   # 🍒 Red
            curses.color_pair(7),   # 🍐 Green/Yellow
        ]
        
        # Swallowing effect state
        self.swallowing = False
        self.swallow_frame = 0
        self.swallowed_fruit = None  # Store the fruit being swallowed
        self.swallowed_fruit_index = None  # Store fruit color index
        
        # Disable cursor
        curses.curs_set(0)
        self.stdscr.nodelay(1)  # Non-blocking input
        self.stdscr.timeout(0)
    
    def generate_food(self) -> Tuple[int, int]:
        """Generate food at a random position not occupied by snake"""
        while True:
            # Generate food within playable area (inside walls)
            # Top wall now allows game coordinate 0, so playable area is 0 to game_height-2
            food_y = random.randint(0, self.game_height - 2)
            food_x = random.randint(1, self.game_width - 2)
            if (food_y, food_x) not in self.snake:
                return (food_y, food_x)
    
    def draw_border(self):
        """Draw distinct game border walls"""
        border_color = curses.color_pair(4)
        
        # Game coordinates: playable area is 1 to game_height-2, game_width-2
        # Walls are at 0 and game_height-1, game_width-1
        # Drawing: game coord (y, x) is drawn at screen (y+2, x+2)
        # So walls should be drawn at:
        # - Top wall: game y=0 -> screen y=2, but draw border line at y=1
        # - Bottom wall: game y=game_height-1 -> screen y=game_height+1, border at y=game_height+1
        # - Left wall: game x=0 -> screen x=2, border at x=1  
        # - Right wall: game x=game_width-1 -> screen x=game_width+1, border at x=game_width+1
        
        # Top and bottom borders
        for x in range(0, self.game_width):
            try:
                # Top border (above game area)
                self.stdscr.addstr(1, x + 2, '═', border_color)
                # Bottom border (below game area)
                self.stdscr.addstr(self.game_height + 1, x + 2, '═', border_color)
            except curses.error:
                pass
        
        # Left and right borders
        for y in range(0, self.game_height):
            try:
                # Left border (left of game area)
                self.stdscr.addstr(y + 2, 1, '║', border_color)
                # Right border (right of game area)
                self.stdscr.addstr(y + 2, self.game_width + 1, '║', border_color)
            except curses.error:
                pass
        
        # Corners
        try:
            self.stdscr.addstr(1, 1, '╔', border_color)
            self.stdscr.addstr(1, self.game_width + 1, '╗', border_color)
            self.stdscr.addstr(self.game_height + 1, 1, '╚', border_color)
            self.stdscr.addstr(self.game_height + 1, self.game_width + 1, '╝', border_color)
        except curses.error:
            pass
    
    def draw_snake(self):
        """Draw the snake with fatter characters and swallowing effect"""
        snake_color = curses.color_pair(1)
        thick_green = curses.color_pair(1) | curses.A_BOLD  # Thicker green for swallowed food
        
        # Calculate which segments show the swallowed food effect (traveling from head to tail)
        swallow_segments = set()
        if self.swallowing:
            # Swallowed food travels from head (position 0) to tail (position len-1)
            # Show thicker green segments moving along the body
            total_frames = len(self.snake) * 3  # Animation frames
            if self.swallow_frame < total_frames:
                # Calculate how many segments should show the effect
                # Progress from 0 to 1, showing more segments as it travels
                progress = self.swallow_frame / total_frames
                # Number of segments to highlight: starts at 1 (head), grows to full length
                num_segments = max(1, int(len(self.snake) * progress))
                # Mark segments from head (0) to the calculated position
                for seg_idx in range(num_segments):
                    if seg_idx < len(self.snake):
                        swallow_segments.add(seg_idx)
        
        for i, (y, x) in enumerate(self.snake):
            # Check if this segment should show the swallowing effect (thicker green)
            if i in swallow_segments:
                # Draw thicker green segment to show swallowed food traveling
                char = '██'  # Thick green blocks
                try:
                    self.stdscr.addstr(y + 2, x + 2, char, thick_green)
                except curses.error:
                    pass
            else:
                # Use normal snake appearance
                if i == 0:
                    # Head - normal appearance
                    char = '▓▓'  # Normal fat head
                else:
                    char = '░░'  # Fat body segments
                try:
                    self.stdscr.addstr(y + 2, x + 2, char, snake_color)
                except curses.error:
                    pass  # Ignore out of bounds errors
    
    def draw_food(self):
        """Draw the food with random fruit and random color"""
        # Get color based on fruit index
        food_color = self.fruit_colors[self.food_index]
        y, x = self.food_pos
        try:
            # Draw fruit emoji with its assigned color
            self.stdscr.addstr(y + 2, x + 2, self.food_type, food_color)
        except curses.error:
            # Fallback if emoji doesn't work - use colored character
            try:
                self.stdscr.addstr(y + 2, x + 2, '*', food_color)
            except curses.error:
                pass
    
    def draw_info(self):
        """Draw score and game info"""
        info_color = curses.color_pair(3)
        info_text = f"Score: {self.score} | High Score: {self.high_score} | Speed: {1/self.speed:.1f}"
        try:
            self.stdscr.addstr(0, 2, info_text, info_color)
        except curses.error:
            pass
    
    def handle_input(self):
        """Handle keyboard input"""
        key = self.stdscr.getch()
        
        # Arrow keys
        if key == curses.KEY_UP and self.direction != Direction.DOWN:
            self.next_direction = Direction.UP
        elif key == curses.KEY_DOWN and self.direction != Direction.UP:
            self.next_direction = Direction.DOWN
        elif key == curses.KEY_LEFT and self.direction != Direction.RIGHT:
            self.next_direction = Direction.LEFT
        elif key == curses.KEY_RIGHT and self.direction != Direction.LEFT:
            self.next_direction = Direction.RIGHT
        # WASD keys
        elif key == ord('w') or key == ord('W'):
            if self.direction != Direction.DOWN:
                self.next_direction = Direction.UP
        elif key == ord('s') or key == ord('S'):
            if self.direction != Direction.UP:
                self.next_direction = Direction.DOWN
        elif key == ord('a') or key == ord('A'):
            if self.direction != Direction.RIGHT:
                self.next_direction = Direction.LEFT
        elif key == ord('d') or key == ord('D'):
            if self.direction != Direction.LEFT:
                self.next_direction = Direction.RIGHT
        # Quit
        elif key == ord('q') or key == ord('Q'):
            return False
        
        return True
    
    def move_snake(self) -> bool:
        """Move the snake and check for collisions. Returns False if game over"""
        self.direction = self.next_direction
        
        # Calculate new head position
        head_y, head_x = self.snake[0]
        dy, dx = self.direction.value
        new_head = (head_y + dy, head_x + dx)
        
        # Check if food eaten FIRST - before other collision checks
        # Both snake head (▓▓) and food emojis are 2 characters wide
        # They are drawn at screen position (y+2, x+2) and occupy 2 columns each
        # Since both are 2 chars wide, they overlap if their positions are:
        # - Exact match: same y, same x
        # - Adjacent horizontally: same y, x differs by 1 (overlap at one column)
        # - Adjacent vertically: same x, y differs by 1 (overlap at one row)
        # - Diagonal: adjacent in both directions (corner touch)
        food_y, food_x = self.food_pos
        new_y, new_x = new_head
        curr_y, curr_x = self.snake[0]
        
        # Calculate if snake head overlaps with food (considering 2-char width)
        # Both are 2 chars wide, so they overlap if:
        # - Same position (exact overlap)
        # - Adjacent horizontally: |new_x - food_x| <= 1 AND new_y == food_y
        # - Adjacent vertically: |new_y - food_y| <= 1 AND new_x == food_x
        # - Diagonal: |new_x - food_x| <= 1 AND |new_y - food_y| <= 1
        
        # PRIMARY CHECK: exact coordinate match
        food_eaten = (new_y == food_y and new_x == food_x)
        
        # SECONDARY CHECK: overlap detection - different behavior for vertical vs horizontal
        if not food_eaten:
            # For VERTICAL movement (top/bottom): allow lenient overlap (works well)
            if new_x == food_x:  # Same column
                # Same column - check if y positions overlap (within 1 for vertical approach)
                if abs(new_y - food_y) <= 1:
                    food_eaten = True
            
            # For HORIZONTAL movement (left/right): require exact match only
            # This prevents accidental eating when passing by from the side
            elif new_y == food_y:  # Same row
                # Same row - require EXACT x match (no adjacent detection)
                if new_x == food_x:
                    food_eaten = True
        
        # TERTIARY CHECK: current head position (safety check)
        if not food_eaten:
            # Exact match only for current position
            if curr_y == food_y and curr_x == food_x:
                food_eaten = True
            # Allow vertical overlap for current position (if moving vertically)
            elif curr_x == food_x and abs(curr_y - food_y) <= 1:
                food_eaten = True
        
        # Check wall collision
        # Playable area: y in [0, game_height-2], x in [1, game_width-2]
        # Walls are at: y=0, y=game_height-1, x=0, x=game_width-1
        # Top wall allows coordinate 0, bottom wall at game_height-1
        if (new_head[0] < 0 or new_head[0] >= self.game_height - 1 or
            new_head[1] < 1 or new_head[1] >= self.game_width - 1):
            return False
        
        # Check self collision (but allow if it's just the tail, which will be removed)
        # Check if new head would collide with body (excluding current tail)
        if new_head in self.snake[:-1]:
            return False
        
        # FINAL SAFETY CHECK: Right before adding head - absolute last chance
        # Re-check with strict horizontal, lenient vertical
        if not food_eaten:
            # Exact match
            if new_head == self.food_pos:
                food_eaten = True
            # Vertical overlap: same column, y within 1 (lenient for top/bottom)
            elif new_x == food_x and abs(new_y - food_y) <= 1:
                food_eaten = True
            # Horizontal: same row, EXACT x match only (strict for left/right)
            elif new_y == food_y and new_x == food_x:
                food_eaten = True
            # Current position: exact or vertical overlap
            elif curr_y == food_y and curr_x == food_x:
                food_eaten = True
            elif curr_x == food_x and abs(curr_y - food_y) <= 1:
                food_eaten = True
        
        # Add new head
        self.snake.insert(0, new_head)
        
        # ULTIMATE FINAL CHECK: After adding head, check one more time
        # This catches any edge cases where food might have been missed
        if not food_eaten:
            head_y, head_x = self.snake[0]
            # Exact match
            if head_y == food_y and head_x == food_x:
                food_eaten = True
            # Vertical overlap: same column, y within 1 (lenient for top/bottom)
            elif head_x == food_x and abs(head_y - food_y) <= 1:
                food_eaten = True
        
        # Handle food eating
        if food_eaten:
            # Store the fruit being swallowed for the animation
            self.swallowed_fruit = self.food_type
            self.swallowed_fruit_index = self.food_index
            
            # Start swallowing effect - will travel along snake body
            self.swallowing = True
            self.swallow_frame = 0
            
            self.score += 10
            if self.score > self.high_score:
                self.high_score = self.score
            # Generate new food position and random fruit type
            self.food_pos = self.generate_food()
            self.food_index = random.randint(0, len(self.FRUITS) - 1)
            self.food_type = self.FRUITS[self.food_index]
            # Increase speed (decrease delay)
            self.speed = max(0.03, self.speed - self.speed_increment)
        else:
            # Remove tail if no food eaten
            self.snake.pop()
        
        return True
    
    def clear_game_area(self):
        """Clear the game area - including bottom line to prevent traces"""
        # Clear from row 2 to game_height+2 (includes bottom playable line)
        # game_height-2 is the bottom playable coordinate, which maps to screen y = (game_height-2)+2 = game_height
        # Need to clear extra columns to handle double-width characters (▓▓, ░░, ██)
        for y in range(2, self.game_height + 3):
            for x in range(2, self.game_width + 3):
                try:
                    self.stdscr.addstr(y, x, ' ')
                except curses.error:
                    pass
            # Also clear one extra position at the end of each row for double-width characters
            try:
                self.stdscr.addstr(y, self.game_width + 3, ' ')
            except curses.error:
                pass
    
    def run(self):
        """Main game loop"""
        while True:
            # Handle input
            if not self.handle_input():
                break
            
            # Update swallowing effect
            if self.swallowing:
                self.swallow_frame += 1
                # Swallowing animation: thick green segments travel from head to tail
                total_frames = len(self.snake) * 3
                if self.swallow_frame >= total_frames:
                    self.swallowing = False
                    self.swallow_frame = 0
                    self.swallowed_fruit = None
                    self.swallowed_fruit_index = None
            
            # Move snake
            if not self.move_snake():
                break  # Game over
            
            # Clear and redraw
            self.clear_game_area()
            self.draw_border()
            self.draw_snake()
            self.draw_food()
            self.draw_info()
            self.stdscr.refresh()
            
            # Control game speed
            time.sleep(self.speed)
        
        return self.score


def show_welcome_screen(stdscr):
    """Display welcome screen with instructions"""
    stdscr.clear()
    stdscr.border()
    
    # SNAKE ASCII art
    snake_art = [
        " ___________  ________  _____  ___        __       __   ___  _______  ",
        "(\"     _   \")/\"       )(\\\"   \\|\"  \\      /\"\"\\     |/\"| /  \")/\"     \"| ",
        " )__/  \\\\__/(:   \\___/ |.\\\\   \\    |    /    \\    (: |/   /(: ______) ",
        "    \\\\_ /    \\___  \\   |: \\.   \\\\  |   /' /\\  \\   |    __/  \\/    |   ",
        "    |.  |     __/  \\\\  |.  \\    \\. |  //  __'  \\  (// _  \\  // ___)_  ",
        "    \\:  |    /\" \\   :) |    \\    \\ | /   /  \\\\  \\ |: | \\  \\(:      \"| ",
        "     \\__|   (_______/   \\___|\\____\\)(___/    \\___)(__|  \\__)\\\\_______) ",
        "                                                                      "
    ]
    
    # Welcome message with controls
    welcome_text = [
        "",
        "CONTROLS:",
        "  • Arrow Keys or WASD - Move",
        "  • Q - Quit",
        "",
        "OBJECTIVE:",
        "  Eat the food (🍎) to grow and score points!",
        "  Avoid hitting the walls or yourself.",
        "  The game gets faster as you eat more food.",
        "",
        "Press any key to start...",
        "",
        "made by Boris Lemer with cursor.ai for fun... :P"
    ]
    
    # Signature ASCII art
    signature_art = [
        "               #   ___           !!!         .      .                                       |\"|            ___          |\"|           !!!      ",
        "     ,,,       #  <_*_>       `  _ _  '    .  .:::.       `  _ ,  '           _/7          _|_|_          /_\\ `*       _|_|_       `  _ _  '   ",
        "    (o o)      #  (o o)      -  (OXO)  -     :(o o):  .  -  (o)o)  -         (o o)         (o o)         (o o)         (o o)      -  (OXO)  -  ",
        "ooO--(_)--Ooo--8---(_)--Ooo-ooO--(_)--Ooo-ooO--(_)--Ooo--ooO'(_)--Ooo----ooO--(_)--Ooo-ooO--(_)--Ooo-ooO--(_)--Ooo-ooO--(_)--Ooo-ooO--(_)--Ooo-"
    ]
    
    height, width = stdscr.getmaxyx()
    
    # Draw ASCII art at the top, centered
    art_start_y = 2
    for i, line in enumerate(snake_art):
        x = (width - len(line)) // 2
        if x < 0:
            x = 0
        try:
            stdscr.addstr(art_start_y + i, x, line)
        except curses.error:
            pass
    
    # Draw welcome text below ASCII art
    text_start_y = art_start_y + len(snake_art) + 2
    for i, line in enumerate(welcome_text):
        x = (width - len(line)) // 2
        if x < 0:
            x = 0
        try:
            stdscr.addstr(text_start_y + i, x, line)
        except curses.error:
            pass
    
    # Draw signature at the bottom
    signature_start_y = height - len(signature_art) - 2
    for i, line in enumerate(signature_art):
        x = (width - len(line)) // 2
        if x < 0:
            x = 0
        try:
            stdscr.addstr(signature_start_y + i, x, line)
        except curses.error:
            pass
    
    stdscr.refresh()
    stdscr.nodelay(0)
    stdscr.getch()  # Wait for any key
    stdscr.nodelay(1)


def show_game_over_screen(stdscr, score: int, high_score: int):
    """Display game over screen"""
    stdscr.clear()
    stdscr.border()
    
    game_over_text = [
        "",
        "╔════════════════════════════════════╗",
        "║           GAME OVER!              ║",
        "╚════════════════════════════════════╝",
        "",
        f"Final Score: {score}",
        f"High Score: {high_score}",
        "",
        "Press 'R' to play again",
        "Press 'Q' to quit",
        ""
    ]
    
    height, width = stdscr.getmaxyx()
    start_y = (height - len(game_over_text)) // 2
    
    for i, line in enumerate(game_over_text):
        x = (width - len(line)) // 2
        try:
            stdscr.addstr(start_y + i, x, line)
        except curses.error:
            pass
    
    stdscr.refresh()
    stdscr.nodelay(0)
    
    while True:
        key = stdscr.getch()
        if key == ord('r') or key == ord('R'):
            return True
        elif key == ord('q') or key == ord('Q'):
            return False


def main(stdscr):
    """Main function"""
    high_score = 0
    
    while True:
        # Show welcome screen
        show_welcome_screen(stdscr)
        
        # Initialize and run game
        try:
            game = SnakeGame(stdscr)
            score = game.run()
            
            if score > high_score:
                high_score = score
            
            # Show game over screen
            if not show_game_over_screen(stdscr, score, high_score):
                break
        except ValueError as e:
            # Terminal too small
            stdscr.clear()
            stdscr.addstr(0, 0, str(e))
            stdscr.addstr(1, 0, "Press any key to exit...")
            stdscr.refresh()
            stdscr.nodelay(0)
            stdscr.getch()
            break
        except KeyboardInterrupt:
            break


if __name__ == "__main__":
    curses.wrapper(main)

