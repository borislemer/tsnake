/*
 * tsnake - Terminal Snake Game in C
 * Made by Boris Lemer with cursor.ai for fun... :P
 */

#define _POSIX_C_SOURCE 200809L
#define _DEFAULT_SOURCE

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <unistd.h>
#include <ncurses.h>
#include <stdbool.h>

#define MAX_SNAKE_LENGTH 1000
#define INITIAL_SPEED 100000  // microseconds
#define SPEED_INCREMENT 5000
#define MIN_SPEED 30000

// Direction enum
typedef enum {
    DIR_UP = 0,
    DIR_DOWN,
    DIR_LEFT,
    DIR_RIGHT
} Direction;

// Point structure
typedef struct {
    int y;
    int x;
} Point;

// Fruit types
const char* FRUITS[] = {
    "🍎", "🍌", "🍇", "🍊", "🍓", "🍑", "🍉", "🥝", "🍒", "🍐"
};
const int NUM_FRUITS = 10;

// Game state
typedef struct {
    Point snake[MAX_SNAKE_LENGTH];
    int snake_length;
    Direction direction;
    Direction next_direction;
    Point food_pos;
    int food_index;
    int score;
    int high_score;
    int game_height;
    int game_width;
    bool swallowing;
    int swallow_frame;
    int swallowed_fruit_index;
    int speed;
} GameState;

// Color pairs
#define COLOR_SNAKE 1
#define COLOR_FOOD 2
#define COLOR_INFO 3
#define COLOR_BORDER 4
#define COLOR_FRUIT_RED 5
#define COLOR_FRUIT_YELLOW 6
#define COLOR_FRUIT_GREEN 7

// Fruit color mapping (10 fruits mapped to colors)
int fruit_colors[10] = {
    COLOR_FRUIT_RED,    // 🍎
    COLOR_FRUIT_YELLOW, // 🍌
    COLOR_FRUIT_GREEN,  // 🍇
    COLOR_FRUIT_YELLOW, // 🍊
    COLOR_FRUIT_RED,    // 🍓
    COLOR_FRUIT_RED,    // 🍑
    COLOR_FRUIT_GREEN,  // 🍉
    COLOR_FRUIT_GREEN,  // 🥝
    COLOR_FRUIT_RED,    // 🍒
    COLOR_FRUIT_GREEN   // 🍐
};

// Initialize colors
void init_colors() {
    start_color();
    init_pair(COLOR_SNAKE, COLOR_GREEN, COLOR_BLACK);
    init_pair(COLOR_FOOD, COLOR_RED, COLOR_BLACK);
    init_pair(COLOR_INFO, COLOR_YELLOW, COLOR_BLACK);
    init_pair(COLOR_BORDER, COLOR_MAGENTA, COLOR_BLACK);
    init_pair(COLOR_FRUIT_RED, COLOR_RED, COLOR_BLACK);
    init_pair(COLOR_FRUIT_YELLOW, COLOR_YELLOW, COLOR_BLACK);
    init_pair(COLOR_FRUIT_GREEN, COLOR_GREEN, COLOR_BLACK);
}

// Initialize game state
void init_game(GameState* game, int height, int width) {
    game->game_height = height - 4;
    game->game_width = width - 4;
    
    if (game->game_height < 10 || game->game_width < 20) {
        endwin();
        fprintf(stderr, "Terminal too small! Please resize to at least 24x24\n");
        exit(1);
    }
    
    game->score = 0;
    game->high_score = 0;
    game->direction = DIR_RIGHT;
    game->next_direction = DIR_RIGHT;
    game->speed = INITIAL_SPEED;
    game->swallowing = false;
    game->swallow_frame = 0;
    
    // Initialize snake in center
    int center_y = game->game_height / 2;
    int center_x = game->game_width / 2;
    center_y = (center_y < 1) ? 1 : (center_y > game->game_height - 2) ? game->game_height - 2 : center_y;
    center_x = (center_x < 1) ? 1 : (center_x > game->game_width - 2) ? game->game_width - 2 : center_x;
    
    game->snake_length = 3;
    game->snake[0] = (Point){center_y, center_x};
    game->snake[1] = (Point){center_y, center_x - 1};
    game->snake[2] = (Point){center_y, center_x - 2};
    
    // Generate initial food
    srand(time(NULL));
    game->food_index = rand() % NUM_FRUITS;
    game->food_pos.y = rand() % (game->game_height - 2) + 1;
    game->food_pos.x = rand() % (game->game_width - 2) + 1;
}

// Check if point is in snake
bool is_in_snake(GameState* game, Point p) {
    for (int i = 0; i < game->snake_length; i++) {
        if (game->snake[i].y == p.y && game->snake[i].x == p.x) {
            return true;
        }
    }
    return false;
}

// Generate new food position
void generate_food(GameState* game) {
    while (true) {
        game->food_pos.y = rand() % (game->game_height - 1);
        game->food_pos.x = rand() % (game->game_width - 2) + 1;
        if (!is_in_snake(game, game->food_pos)) {
            break;
        }
    }
    game->food_index = rand() % NUM_FRUITS;
}

// Handle input
bool handle_input(GameState* game) {
    int ch = getch();
    
    if (ch == ERR) {
        return true;  // No input
    }
    
    switch (ch) {
        case KEY_UP:
        case 'w':
        case 'W':
            if (game->direction != DIR_DOWN) {
                game->next_direction = DIR_UP;
            }
            break;
        case KEY_DOWN:
        case 's':
        case 'S':
            if (game->direction != DIR_UP) {
                game->next_direction = DIR_DOWN;
            }
            break;
        case KEY_LEFT:
        case 'a':
        case 'A':
            if (game->direction != DIR_RIGHT) {
                game->next_direction = DIR_LEFT;
            }
            break;
        case KEY_RIGHT:
        case 'd':
        case 'D':
            if (game->direction != DIR_LEFT) {
                game->next_direction = DIR_RIGHT;
            }
            break;
        case 'q':
        case 'Q':
            return false;
        default:
            break;
    }
    return true;
}

// Move snake and check collisions
bool move_snake(GameState* game) {
    game->direction = game->next_direction;
    
    // Calculate new head position
    Point new_head = game->snake[0];
    switch (game->direction) {
        case DIR_UP:
            new_head.y--;
            break;
        case DIR_DOWN:
            new_head.y++;
            break;
        case DIR_LEFT:
            new_head.x--;
            break;
        case DIR_RIGHT:
            new_head.x++;
            break;
    }
    
    // Check wall collision
    if (new_head.y < 0 || new_head.y >= game->game_height - 1 ||
        new_head.x < 1 || new_head.x >= game->game_width - 1) {
        return false;
    }
    
    // Check self collision
    for (int i = 0; i < game->snake_length - 1; i++) {
        if (game->snake[i].y == new_head.y && game->snake[i].x == new_head.x) {
            return false;
        }
    }
    
    // Check food collision
    bool food_eaten = false;
    
    // Primary: exact match
    if (new_head.y == game->food_pos.y && new_head.x == game->food_pos.x) {
        food_eaten = true;
    }
    
    // Secondary: lenient for vertical, strict for horizontal
    if (!food_eaten) {
        if (new_head.x == game->food_pos.x) {
            // Same column - lenient for vertical approach
            if (abs(new_head.y - game->food_pos.y) <= 1) {
                food_eaten = true;
            }
        } else if (new_head.y == game->food_pos.y) {
            // Same row - exact match only for horizontal approach
            if (new_head.x == game->food_pos.x) {
                food_eaten = true;
            }
        }
    }
    
    // Add new head
    for (int i = game->snake_length; i > 0; i--) {
        game->snake[i] = game->snake[i - 1];
    }
    game->snake[0] = new_head;
    
    if (food_eaten) {
        // Start swallowing effect
        game->swallowing = true;
        game->swallow_frame = 0;
        game->swallowed_fruit_index = game->food_index;
        
        game->score += 10;
        if (game->score > game->high_score) {
            game->high_score = game->score;
        }
        
        // Grow snake
        game->snake_length++;
        if (game->snake_length >= MAX_SNAKE_LENGTH) {
            game->snake_length = MAX_SNAKE_LENGTH;
        }
        
        // Generate new food
        generate_food(game);
        
        // Increase speed
        game->speed -= SPEED_INCREMENT;
        if (game->speed < MIN_SPEED) {
            game->speed = MIN_SPEED;
        }
    }
    
    return true;
}

// Draw border
void draw_border(GameState* game) {
    attron(COLOR_PAIR(COLOR_BORDER));
    
    // Top and bottom
    for (int x = 0; x < game->game_width; x++) {
        mvaddch(1, x + 2, ACS_HLINE);
        mvaddch(game->game_height + 1, x + 2, ACS_HLINE);
    }
    
    // Left and right
    for (int y = 0; y < game->game_height; y++) {
        mvaddch(y + 2, 1, ACS_VLINE);
        mvaddch(y + 2, game->game_width + 1, ACS_VLINE);
    }
    
    // Corners
    mvaddch(1, 1, ACS_ULCORNER);
    mvaddch(1, game->game_width + 1, ACS_URCORNER);
    mvaddch(game->game_height + 1, 1, ACS_LLCORNER);
    mvaddch(game->game_height + 1, game->game_width + 1, ACS_LRCORNER);
    
    attroff(COLOR_PAIR(COLOR_BORDER));
}

// Draw snake
void draw_snake(GameState* game) {
    attron(COLOR_PAIR(COLOR_SNAKE));
    
    // Calculate swallowing segments
    bool swallow_segments[MAX_SNAKE_LENGTH] = {false};
    if (game->swallowing) {
        int total_frames = game->snake_length * 3;
        if (game->swallow_frame < total_frames) {
            float progress = (float)game->swallow_frame / total_frames;
            int num_segments = (int)(game->snake_length * progress);
            if (num_segments < 1) num_segments = 1;
            for (int i = 0; i < num_segments && i < game->snake_length; i++) {
                swallow_segments[i] = true;
            }
        }
    }
    
    for (int i = 0; i < game->snake_length; i++) {
        int y = game->snake[i].y + 2;
        int x = game->snake[i].x + 2;
        
        if (swallow_segments[i]) {
            // Thick green for swallowing effect
            attron(A_BOLD);
            mvprintw(y, x, "██");
            attroff(A_BOLD);
        } else if (i == 0) {
            // Head
            mvprintw(y, x, "▓▓");
        } else {
            // Body
            mvprintw(y, x, "░░");
        }
    }
    
    attroff(COLOR_PAIR(COLOR_SNAKE));
}

// Draw food
void draw_food(GameState* game) {
    int color_pair = fruit_colors[game->food_index];
    attron(COLOR_PAIR(color_pair));
    int y = game->food_pos.y + 2;
    int x = game->food_pos.x + 2;
    mvprintw(y, x, "%s", FRUITS[game->food_index]);
    attroff(COLOR_PAIR(color_pair));
}

// Draw info
void draw_info(GameState* game) {
    attron(COLOR_PAIR(COLOR_INFO));
    char info[200];
    float speed_val = 1000000.0 / game->speed;
    snprintf(info, sizeof(info), "Score: %d | High Score: %d | Speed: %.1f",
             game->score, game->high_score, speed_val);
    mvprintw(0, 2, "%s", info);
    attroff(COLOR_PAIR(COLOR_INFO));
}

// Clear game area
void clear_game_area(GameState* game) {
    for (int y = 2; y < game->game_height + 3; y++) {
        for (int x = 2; x < game->game_width + 3; x++) {
            mvaddch(y, x, ' ');
        }
    }
}

// Show welcome screen
void show_welcome_screen() {
    clear();
    box(stdscr, 0, 0);
    
    const char* snake_art[] = {
        " ___________  ________  _____  ___        __       __   ___  _______  ",
        "(\"     _   \")/\"       )(\\\"   \\|\"  \\      /\"\"\\     |/\"| /  \")/\"     \"| ",
        " )__/  \\\\__/(:   \\___/ |.\\\\   \\    |    /    \\    (: |/   /(: ______) ",
        "    \\\\_ /    \\___  \\   |: \\.   \\\\  |   /' /\\  \\   |    __/  \\/    |   ",
        "    |.  |     __/  \\\\  |.  \\    \\. |  //  __'  \\  (// _  \\  // ___)_  ",
        "    \\:  |    /\" \\   :) |    \\    \\ | /   /  \\\\  \\ |: | \\  \\(:      \"| ",
        "     \\__|   (_______/   \\___|\\____\\)(___/    \\___)(__|  \\__)\\\\_______) ",
        "                                                                      "
    };
    
    const char* welcome_text[] = {
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
    };
    
    const char* signature[] = {
        "               #   ___           !!!         .      .                                       |\"|            ___          |\"|           !!!      ",
        "     ,,,       #  <_*_>       `  _ _  '    .  .:::.       `  _ ,  '           _/7          _|_|_          /_\\ `*       _|_|_       `  _ _  '   ",
        "    (o o)      #  (o o)      -  (OXO)  -     :(o o):  .  -  (o)o)  -         (o o)         (o o)         (o o)         (o o)      -  (OXO)  -  ",
        "ooO--(_)--Ooo--8---(_)--Ooo-ooO--(_)--Ooo-ooO--(_)--Ooo--ooO'(_)--Ooo----ooO--(_)--Ooo-ooO--(_)--Ooo-ooO--(_)--Ooo-ooO--(_)--Ooo-ooO--(_)--Ooo-"
    };
    
    int height, width;
    getmaxyx(stdscr, height, width);
    
    // Draw ASCII art
    int art_start_y = 2;
    for (int i = 0; i < 8; i++) {
        int x = (width - strlen(snake_art[i])) / 2;
        if (x < 0) x = 0;
        mvprintw(art_start_y + i, x, "%s", snake_art[i]);
    }
    
    // Draw welcome text
    int text_start_y = art_start_y + 8 + 2;
    for (int i = 0; i < 13; i++) {
        int x = (width - strlen(welcome_text[i])) / 2;
        if (x < 0) x = 0;
        mvprintw(text_start_y + i, x, "%s", welcome_text[i]);
    }
    
    // Draw signature at bottom
    int sig_start_y = height - 5;
    for (int i = 0; i < 4; i++) {
        int x = (width - strlen(signature[i])) / 2;
        if (x < 0) x = 0;
        mvprintw(sig_start_y + i, x, "%s", signature[i]);
    }
    
    refresh();
    nodelay(stdscr, FALSE);
    getch();
    nodelay(stdscr, TRUE);
}

// Show game over screen
bool show_game_over_screen(GameState* game) {
    clear();
    box(stdscr, 0, 0);
    
    const char* game_over_text[] = {
        "",
        "╔════════════════════════════════════╗",
        "║           GAME OVER!              ║",
        "╚════════════════════════════════════╝",
        "",
        "",
        "",
        "",
        "Press 'R' to play again",
        "Press 'Q' to quit",
        ""
    };
    
    int height, width;
    getmaxyx(stdscr, height, width);
    
    int start_y = (height - 10) / 2;
    for (int i = 0; i < 10; i++) {
        int x = (width - strlen(game_over_text[i])) / 2;
        if (x < 0) x = 0;
        mvprintw(start_y + i, x, "%s", game_over_text[i]);
    }
    
    // Print scores
    char score_text[100];
    snprintf(score_text, sizeof(score_text), "Final Score: %d", game->score);
    int x = (width - strlen(score_text)) / 2;
    mvprintw(start_y + 4, x, "%s", score_text);
    
    snprintf(score_text, sizeof(score_text), "High Score: %d", game->high_score);
    x = (width - strlen(score_text)) / 2;
    mvprintw(start_y + 5, x, "%s", score_text);
    
    refresh();
    nodelay(stdscr, FALSE);
    
    while (true) {
        int ch = getch();
        if (ch == 'r' || ch == 'R') {
            nodelay(stdscr, TRUE);
            return true;
        } else if (ch == 'q' || ch == 'Q') {
            nodelay(stdscr, TRUE);
            return false;
        }
    }
}

// Main game loop
int run_game(GameState* game) {
    while (true) {
        if (!handle_input(game)) {
            break;
        }
        
        // Update swallowing effect
        if (game->swallowing) {
            game->swallow_frame++;
            int total_frames = game->snake_length * 3;
            if (game->swallow_frame >= total_frames) {
                game->swallowing = false;
                game->swallow_frame = 0;
            }
        }
        
        if (!move_snake(game)) {
            break;  // Game over
        }
        
        clear_game_area(game);
        draw_border(game);
        draw_snake(game);
        draw_food(game);
        draw_info(game);
        refresh();
        
        // Sleep using nanosleep for better compatibility
        struct timespec ts;
        ts.tv_sec = game->speed / 1000000;
        ts.tv_nsec = (game->speed % 1000000) * 1000;
        nanosleep(&ts, NULL);
    }
    
    return game->score;
}

// Main function
int main() {
    initscr();
    noecho();
    curs_set(0);
    keypad(stdscr, TRUE);
    nodelay(stdscr, TRUE);
    timeout(0);
    
    init_colors();
    
    int high_score = 0;
    
    while (true) {
        show_welcome_screen();
        
        int height, width;
        getmaxyx(stdscr, height, width);
        
        GameState game;
        init_game(&game, height, width);
        
        int score = run_game(&game);
        
        if (score > high_score) {
            high_score = score;
        }
        game.high_score = high_score;
        
        if (!show_game_over_screen(&game)) {
            break;
        }
    }
    
    endwin();
    return 0;
}

