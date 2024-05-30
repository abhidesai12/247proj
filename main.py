import pygame
import os
from g import game_state

# Initialize Pygame
pygame.init()
pygame.display.set_caption("Cardinal Conquest")
pygame.mixer.init()


from levels.level1.l1 import run_level1
from levels.level3.l3 import run_level3
from intro import run_intro

# Load music
background_music_path = "sound/background.mp3"
if os.path.exists(background_music_path):
    pygame.mixer.music.load(background_music_path)
    pygame.mixer.music.set_volume(0.5)  # Set volume to 50%
    pygame.mixer.music.play(-1)  # Play the music in a loop
else:
    print(f"Error: {background_music_path} not found.")

# Load logo image
logo_image = pygame.image.load("images/logo.png")
logo_image = pygame.transform.scale(logo_image, (350, 350))

# Import levels
from intro import run_intro
from levels.level1.l1 import run_level1
from levels.level2.l2 import run_level2

def main():
    while True:
        current_level = game_state["current_level"]

        if current_level == "intro":
            run_intro()
            game_state["current_level"] = "level_1"
        elif current_level == "level_1":
            run_level1()
        elif game_state["current_level"] == "level_3":
            run_level3()
        elif current_level == "level_2":
            run_level2()

        if game_state["current_level"] not in game_state["level_sequence"]:
            break  # End the game after the last level

if __name__ == "__main__":
    main()
