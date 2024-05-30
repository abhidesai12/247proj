import pygame

window_size = (800, 600)
window = pygame.display.set_mode(window_size)

# Game state object
game_state = {
    "window_size": window_size,
    "current_level": "intro",  # Start with the intro
    "current_level_index": 0,  # Index to track the current level in the sequence
}
