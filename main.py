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
backgrounds = {"lab": pygame.image.load("assets/backgrounds/background_lab.png"), "green": pygame.image.load("assets/backgrounds/background_green.png"), "frat_house": pygame.image.load("assets/backgrounds/background_frat_house.png"), "dish": pygame.image.load("assets/backgrounds/background_dish.png"), "confetti": pygame.image.load("assets/backgrounds/background_confetti.png")}

# Load and scale character images
mtl_image = pygame.transform.scale(pygame.image.load("assets/characters/mtl.png"), (150, 225))
player_image = pygame.transform.scale(pygame.image.load("assets/characters/player.png"), (100, 150))
mtl_monster_image = pygame.transform.scale(pygame.image.load("assets/characters/mtl_monster.png"), (150, 200))
frat_guy_image = pygame.transform.scale(pygame.image.load("assets/characters/frat_guy.png"), (100, 150))

# Font
font = pygame.font.Font(None, 36)

# Cutscene dialogues and settings
cutscenes = {
    "intro_1": [
        {"bg": "lab", "character": "Player", "text": "I did it! After years of research on treeification, I've finally found a way to make trees sentient! This could change urban planning forever—imagine cities designed by the very trees that inhabit them!"},
        {"bg": "lab", "character": "MTL", "text": "Brilliant work! And it's all I need to grow my empire. These trees will be the root of my rule across the land. The seeds of my conquest are now planted!"},
        {"bg": "lab", "character": "MTL Leaves", "text": ""},
        {"bg": "lab", "character": "Player", "text": "That’s my life's work you're twisting! It's meant for peace, not power! Come back with my tree-tise!"},
        {"bg": "lab", "character": "Player", "text": "He's heading towards Green library! He must be planning to gather followers for his scheme. I need to stop him before it takes root."},
    ],
    "intro_2": [{"bg": "green", "character": "Player", "text": "Green is swarming with MTL's new recruits, blending in as students. To reach MTL, I'll need to sneak past or confront his minions."}],
    "intro_3": [
        {"bg": "frat_house", "character": "Player", "text": "I made it out alive! There he is, slipping away! If I don't catch him soon, his plan will sprout across campus. I think I saw him headed towards the row… I know there’s a party going on there, but I’m sure it’ll be fine to just walk on by."},
        {"bg": "frat_house", "character": "Frat Guard", "text": "Whoa there, you need a wristband. This party's roots are deep and exclusive!"},
        {"bg": "frat_house", "character": "Player", "text": "I just need to... prune some information. Let me through, please?"},
        {"bg": "frat_house", "character": "Frat Guard Leaves", "text": ""},
        {"bg": "frat_house", "character": "Player", "text": "This frat house is a maze of partygoers. I need to navigate this thicket without drawing attention."},
        {"bg": "frat_house", "character": "Player", "text": "MTL's leaving already? He must be heading to his next spot to further his plans. Can't let him go!"},
    ],
    "intro_4": [
        {"bg": "dish", "character": "Player", "text": "The Dish! He's going there to amplify his control over the treeified beings with its powerful antennas. This is where he'll seed his new world unless I stop him!"},
        {"bg": "dish", "character": "MTL", "text": "You're just in time to watch the birth of my empire. Soon, the entire campus will flourish under my canopy!"},
        {"bg": "dish", "character": "MTL Using Dish", "text": ""},
        {"bg": "dish", "character": "Player", "text": "To counteract the signal, I need to overload the system with everything Stanford. Yelling our slang might just do the trick!"},
        {"bg": "dish", "character": "Narrator", "text": "It's time to type up a storm! Disrupt his control by flooding the network with Stanford spirit!"},
        {"bg": "dish", "character": "Player", "text": "This is your last chance, MTL. Return what you stole or brace yourself for a fall!"},
        {"bg": "dish", "character": "MTL", "text": "Prepare yourself! I've grafted myself with treeification technology. You're about to face the full force of nature!", "transform": True},
    ],
    "celebration": [{"bg": "confetti", "character": "Narrator", "text": "With MTL's defeat, the trees are liberated from his control. Peace and natural growth will once again define our campus landscape. The true potential of treeification can now be explored safely.", "no_characters": True}],
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
    right_arrow_pressed = False
    mtl_x_pos = 650

    while index < len(cutscene):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RIGHT and not right_arrow_pressed:
                    index += 1
                    right_arrow_pressed = True
            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_RIGHT:
                    right_arrow_pressed = False

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

        # Move MTL sprite off-screen if needed
        if scene["character"] == "MTL Leaves":
            while mtl_x_pos < WIDTH:
                mtl_x_pos += 5
                screen.fill(WHITE)
                screen.blit(bg_image, (0, 0))
                screen.blit(player_image, (50, 250))
                display_text(screen, f'{scene["character"]}: {scene["text"]}', (40, 430))
                pygame.display.flip()
                clock.tick(30)
            continue  # Skip further rendering for this scene

        # Display characters
        if scene.get("no_characters"):
            pass
        else:
            screen.blit(player_image, (50, 250))
            if scene["character"] == "Frat Guard":
                screen.blit(frat_guy_image, (mtl_x_pos, 250))
            else:
                screen.blit(mtl_monster_image if mtl_transformed else mtl_image, (mtl_x_pos, 250))

        display_text(screen, f'{scene["character"]}: {scene["text"]}', (40, 430))

        pygame.display.flip()
        clock.tick(30)


def main():
    while True:
        current_level = game_state.get("current_level")
        if current_level == "intro":
            run_level2()
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
            game_state["current_level"] = "celebration"
        elif current_level == "celebration":
            play_cutscene("celebration")
            print("Game Over")
            break
        else:
            print("Invalid level")
            break


if __name__ == "__main__":
    main()
