import pygame
import os
from g import game_state

# Initialize Pygame
pygame.init()
pygame.display.set_caption("Cardinal Conquest")
pygame.mixer.init()

# Load music
background_music_path = "sound/background.mp3"
if os.path.exists(background_music_path):
    pygame.mixer.music.load(background_music_path)
    pygame.mixer.music.set_volume(0.5)  # Set volume to 50%
    pygame.mixer.music.play(-1)  # Play the music in a loop
else:
    print(f"Error: {background_music_path} not found.")

# Load logo image
logo_image_path = "images/logo.png"
if os.path.exists(logo_image_path):
    logo_image = pygame.image.load(logo_image_path)
    logo_image = pygame.transform.scale(logo_image, (350, 350))
else:
    print(f"Error: {logo_image_path} not found.")

# Import levels
from intro import run_intro
from levels.level1.l1 import run_level1
from levels.level2.l2 import run_level2
from levels.level3.l3 import run_level3

def main():
    while True:
        current_level = game_state.get("current_level")
        if current_level == "intro":
            #run_intro()
            run_level2()
            game_state["current_level"] = "level_1"
        elif current_level == "level_1":
            run_level1()
        elif current_level == "level_2":
            run_level2()
        elif current_level == "level_3":
            run_level3()
        else:
            print("Invalid level")
            break

if __name__ == "__main__":
    main()
