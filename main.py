import pygame
import os
import sys
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

# Screen dimensions
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# Load backgrounds
backgrounds = {
    "lab": pygame.image.load('assets/backgrounds/background_lab.png'),
    "green": pygame.image.load('assets/backgrounds/background_green.png'),
    "frat_house": pygame.image.load('assets/backgrounds/background_frat_house.png'),
    "dish": pygame.image.load('assets/backgrounds/background_dish.png')
}

# Load and scale character images
mtl_image = pygame.transform.scale(pygame.image.load('assets/characters/mtl.png'), (150, 225))
player_image = pygame.transform.scale(pygame.image.load('assets/characters/player.png'), (100, 150))
mtl_monster_image = pygame.transform.scale(pygame.image.load('assets/characters/mtl_monster.png'), (150, 200))
frat_guy_image = pygame.transform.scale(pygame.image.load('assets/characters/frat_guy.png'), (100, 150))

# Font
font = pygame.font.Font(None, 36)

# Cutscene dialogues and settings
cutscenes = {
    "intro_1": [
        {"bg": "lab", "character": "Player", "text": "I did it! I finished my research on treeification, the process of transforming trees into sentient beings which we can control. Using this, we can help humanity have more trees!"},
        {"bg": "lab", "character": "MTL", "text": "You mean MY research. With this, I will master the art of treeification and use the trees of campus to take over the lands. No one can stop me now! Mwahahahahaha!"},
        {"bg": "lab", "character": "Player", "text": "Hey! That's my life's work! Come back!"},
        {"bg": "lab", "character": "Player", "text": "He's heading to Green! I can't let him get away with this."}
    ],
    "intro_2": [
        {"bg": "green", "character": "Narrator", "text": "I made it to Green! Looks like this place is crawling with his librarian henchmen though… To make it through, I need to defend myself and defeat his minions"},
        {"bg": "green", "character": "Player", "text": "There he goes! I can't lose him now."},
        {"bg": "green", "character": "Instructions", "text": "Use spacebar to shoot and arrow keys to navigate!"}
    ],
    "intro_3": [
        {"bg": "frat_house", "character": "Frat Guy", "text": "Hey! Where do you think you’re going? Do you have a wristband? This party is invite-only!"},
        {"bg": "frat_house", "character": "Narrator", "text": "I’ve gotta make it past all these frat bros without getting caught. If I’m found, who knows what they’ll do to me."},
        {"bg": "frat_house", "character": "Player", "text": "He's leaving the party. This might be my chance to catch up!"},
        {"bg": "frat_house", "character": "Instructions", "text": "Use arrow keys to navigate through the frat house!"}
    ],
    "intro_4": [
        {"bg": "dish", "character": "Player", "text": "To the Main Quad, he must be heading towards the central lab!"},
        {"bg": "dish", "character": "MTL", "text": "Hahahaha! Too slow! I've already started the treeification process. Your research is mine!"},
        {"bg": "dish", "character": "Narrator", "text": "Type the Stanford slang words as fast as you can to disrupt MTL's process!"},
        {"bg": "dish", "character": "Player", "text": "MTL! It’s time for you to give me back my research!"},
        {"bg": "dish", "character": "MTL", "text": "Fine! The hard way it is! You leave me no choice but to treeify myself and take you down personally!", "transform": True},
        {"bg": "dish", "character": "Instructions", "text": "Type to destroy the evil trees and beware of M-Tree-L!"}
    ]
}

# Function to display text within a textbox
def display_text(screen, text, position):
    # Draw textbox
    textbox_rect = pygame.Rect(30, 420, WIDTH - 60, 150)
    pygame.draw.rect(screen, BLACK, textbox_rect)
    pygame.draw.rect(screen, WHITE, textbox_rect, 2)
    
    # Render and split text into multiple lines if necessary
    words = text.split()
    lines = []
    while words:
        line = ""
        while words and font.size(line + words[0])[0] < textbox_rect.width - 20:
            line += words.pop(0) + " "
        lines.append(line)

    # Draw each line of text
    for i, line in enumerate(lines):
        text_surface = font.render(line, True, WHITE)
        screen.blit(text_surface, (textbox_rect.x + 10, textbox_rect.y + 10 + i * font.get_height()))

# Function to play cutscene
def play_cutscene(cutscene_key):
    clock = pygame.time.Clock()
    cutscene = cutscenes[cutscene_key]
    index = 0
    mtl_transformed = False
    space_pressed = False

    while index < len(cutscene):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and not space_pressed:
                    index += 1
                    space_pressed = True
            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_SPACE:
                    space_pressed = False

        if index >= len(cutscene):
            break

        scene = cutscene[index]

        # Clear the screen
        screen.fill(WHITE)

        # Scale the background image to fit the screen
        bg_image = pygame.transform.scale(backgrounds[scene["bg"]], (WIDTH, HEIGHT))
        screen.blit(bg_image, (0, 0))

        if "transform" in scene and scene["transform"]:
            mtl_transformed = True

        # Display characters
        screen.blit(player_image, (50, 250))
        if scene["character"] == "Frat Guy":
            screen.blit(frat_guy_image, (650, 250))
        else:
            screen.blit(mtl_monster_image if mtl_transformed else mtl_image, (650, 250))

        display_text(screen, f'{scene["character"]}: {scene["text"]}', (40, 430))

        pygame.display.flip()
        clock.tick(30)

def main():
    while True:
        current_level = game_state.get("current_level")
        if current_level == "intro":
            run_level3()
            run_intro()
            play_cutscene("intro_1")
            game_state["current_level"] = "level_2"
        elif current_level == "level_2":
            play_cutscene("intro_2")
            run_level2()
            game_state["current_level"] = "level_3"
        elif current_level == "level_3":
            play_cutscene("intro_3")
            run_level3()
            game_state["current_level"] = "level_1"
        elif current_level == "level_1":
            play_cutscene("intro_4")
            run_level1()
            game_state["current_level"] = "level_end"
        elif current_level == "level_end":
            print("Game Over")
            break
        else:
            print("Invalid level")
            break

if __name__ == "__main__":
    main()
