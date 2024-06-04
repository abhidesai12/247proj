import sys
import pygame

from g import window_size, window, game_state
from levels.level1.l1 import level_1_state


# Load logo image
logo_image = pygame.image.load("images/logo.png")
logo_image = pygame.transform.scale(logo_image, (350, 350))

# Lore state
lore_state = {
    "intro_shown": False,
}


# Function to wrap text
def wrap_text(text, font, max_width):
    words = text.split(" ")
    lines = []
    current_line = ""
    for word in words:
        test_line = current_line + word + " "
        if font.size(test_line)[0] <= max_width:
            current_line = test_line
        else:
            lines.append(current_line)
            current_line = word + " "
    lines.append(current_line)
    return lines


# Function to display scrolling text with moving logo
def display_scrolling_text(window, lines, font, color, speed, logo):
    y = window_size[1]
    line_height = font.get_height()
    surface_height = line_height * len(lines) * 2
    scroll_surface = pygame.Surface((window_size[0], surface_height), pygame.SRCALPHA)

    for i, line in enumerate(lines):
        text_surface = font.render(line, True, color)
        scroll_surface.blit(
            text_surface,
            (window_size[0] // 2 - text_surface.get_width() // 2, i * line_height * 2),
        )

    running = True
    while running and y > -surface_height:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    running = False

        window.fill((0, 0, 0))
        window.blit(scroll_surface, (0, y))

        logo_y_position = y + surface_height + 20
        window.blit(logo, (window_size[0] // 2 - logo.get_width() // 2, logo_y_position))

        pygame.display.flip()
        y -= speed
        pygame.time.delay(30)  # Add a delay to control the scrolling speed


# Function to run the intro level
def run_intro():
    font = pygame.font.Font(None, 36)
    intro_text = "Welcome to Cardinal Conquest! Your journey begins here! Use spacebar to make your way through the game."
    lines = wrap_text(intro_text, font, window_size[0] - 40)
    display_scrolling_text(window, lines, font, (255, 255, 255), 2, logo_image)
    lore_state["intro_shown"] = True
    game_state["current_level"] = "level_1"
    game_state["level_state"] = level_1_state
