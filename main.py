import pygame

from g import game_state

# Initialize Pygame
pygame.init()
pygame.display.set_caption("Cardinal Conquest")
pygame.mixer.init()


# after inits are done, import the rest of the levels
from levels.level1.l1 import run_level1
from levels.level3.l3 import run_level3
from intro import run_intro

# Load music
pygame.mixer.music.load("sound/background.mp3")
pygame.mixer.music.set_volume(0.5)  # Set volume to 50%
pygame.mixer.music.play(-1)  # Play the music in a loop


# Load logo image
logo_image = pygame.image.load("images/logo.png")
logo_image = pygame.transform.scale(logo_image, (350, 350))

# Lore state
lore_state = {
    "intro_shown": False,
}


def main():
    while True:
        if game_state["current_level"] == "lore":
            run_intro()
        elif game_state["current_level"] == "level_1":
            run_level1()
        elif game_state["current_level"] == "level_3":
            run_level3()


if __name__ == "__main__":
    main()
