import sys
import pygame
import random
import math
import json

from g import window_size, window, game_state

# Load words
with open("./assets/words.json", "r") as file:
    words = json.load(file)

# Load sprites
background_image = pygame.image.load("images/background.png")
background_image = pygame.transform.scale(background_image, window_size)
tree_sprite = pygame.image.load("images/tree.png")
tree_sprite = pygame.transform.scale(tree_sprite, (60, 60))
heart_sprite = pygame.image.load("images/heart.png")
heart_sprite = pygame.transform.scale(heart_sprite, (30, 30))
student_sprite = pygame.image.load("images/student.png")
student_sprite = pygame.transform.scale(student_sprite, (95, 95))
boss_sprite = pygame.image.load("images/boss.png")
boss_sprite = pygame.transform.scale(boss_sprite, (150, 150))

# Load sounds
hit_sound = pygame.mixer.Sound("sound/hit.mp3")
end_sound = pygame.mixer.Sound("sound/end.mp3")
destroy_sound = pygame.mixer.Sound("sound/destroy.wav")
boss_music_path = "sound/boss.mp3"
background_music_path = "sound/background.mp3"

def draw_text_with_outline(surface, text, font, text_color, outline_color, x, y):
    # Render the text
    text_surface = font.render(text, True, text_color)
    outline_surface = font.render(text, True, outline_color)

    # Draw the outline by blitting the outline surface slightly offset in each direction
    surface.blit(outline_surface, (x - 1, y - 1))
    surface.blit(outline_surface, (x + 1, y - 1))
    surface.blit(outline_surface, (x - 1, y + 1))
    surface.blit(outline_surface, (x + 1, y + 1))

    # Draw the actual text on top
    surface.blit(text_surface, (x, y))

# Load flame animation frames
flame_frames = []
N = 2  # Number of flame frames
for i in range(1, N + 1):
    flame_image = pygame.image.load(f"images/flame{i}.png")
    flame_image = pygame.transform.scale(flame_image, (50, 50))
    flame_frames.extend([flame_image] * 5)

# Level 1 state
level_1_state = {
    "trees": [],
    "flame_animations": [],
    "lives": 3,
    "score": 0,
    "typed_word": "",
    "frame_count": 0,
    "boss_active": False,
    "boss_paragraph": "",
    "boss_typed": "",
    "boss_position": [800, 275],  # Initial boss position
    "boss_speed": 1.0,  # Boss movement speed
    "boss_dialogue_shown": False,
    "wave": 1,
    "trees_destroyed": 0
}

# Define player attributes
player = {
    "position": (50, 275),
    "base_position": (50, 275),
    "amplitude": 5,
    "frequency": 0.1,
}

# Function to create a new tree
def create_tree(word, speed):
    tree = {
        "position": [random.randint(800, 1600), random.randint(50, 550)],
        "radius": 20,
        "speed": speed,
        "word": word.lower(),  # Ensure the word is in lower case
    }
    level_1_state["trees"].append(tree)

# Function to create a boss
def create_boss():
    level_1_state["boss_active"] = True
    level_1_state["boss_paragraph"] = generate_random_paragraph()
    level_1_state["boss_typed"] = ""
    level_1_state["boss_dialogue_shown"] = False  # Reset dialogue shown flag
    # Stop existing music and start boss music
    pygame.mixer.music.stop()
    pygame.mixer.music.load(boss_music_path)
    pygame.mixer.music.play(-1)

# Function to generate a random paragraph
def generate_random_paragraph():
    sentences = [
        "I AM GOING TO DEFEAT YOU!"
    ]
    return " ".join(random.choices(sentences, k=1)).lower()  # Ensure the paragraph is in lower case

# Function to fade in
def fade_in(window, color=(0, 0, 0)):
    fade_surface = pygame.Surface(window.get_size())
    fade_surface.fill(color)
    for alpha in range(0, 255, 5):
        fade_surface.set_alpha(alpha)
        window.blit(fade_surface, (0, 0))
        pygame.display.update()
        pygame.time.delay(10)

# Function to fade out
def fade_out(window, color=(0, 0, 0)):
    fade_surface = pygame.Surface(window.get_size())
    fade_surface.fill(color)
    for alpha in range(255, -1, -5):
        fade_surface.set_alpha(alpha)
        window.blit(fade_surface, (0, 0))
        pygame.display.update()
        pygame.time.delay(10)

# Function to display the death page
def display_death_page(window, score):
    fade_in(window)
    font = pygame.font.Font(None, 74)
    death_text = font.render("You Died", True, (255, 0, 0))
    score_text = font.render(f"Score: {score}", True, (255, 255, 255))
    replay_text = font.render("Replay Game", True, (255, 255, 255))
    replay_rect = replay_text.get_rect(center=(window_size[0] // 2, window_size[1] // 2 + 100))

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if replay_rect.collidepoint(event.pos):
                    return  # Exit the death screen to restart the game

        window.fill((0, 0, 0))
        window.blit(
            death_text,
            (
                window_size[0] // 2 - death_text.get_width() // 2,
                window_size[1] // 2 - death_text.get_height() - 75 // 2,
            ),
        )
        window.blit(
            score_text,
            (window_size[0] // 2 - score_text.get_width() // 2, window_size[1] // 2),
        )
        window.blit(replay_text, replay_rect.topleft)
        pygame.display.flip()

# Function to display the win page
def display_win_page(window, score):
    fade_in(window)
    font = pygame.font.Font(None, 74)
    win_text = font.render("Congrats! You Won!", True, (0, 255, 0))
    score_text = font.render(f"Score: {score}", True, (255, 255, 255))
    replay_text = font.render("Replay Game", True, (255, 255, 255))
    replay_rect = replay_text.get_rect(center=(window_size[0] // 2, window_size[1] // 2 + 100))

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if replay_rect.collidepoint(event.pos):
                    return  # Exit the win screen to restart the game

        window.fill((0, 0, 0))
        window.blit(
            win_text,
            (
                window_size[0] // 2 - win_text.get_width() // 2,
                window_size[1] // 2 - win_text.get_height() - 75 // 2,
            ),
        )
        window.blit(
            score_text,
            (window_size[0] // 2 - score_text.get_width() // 2, window_size[1] // 2),
        )
        window.blit(replay_text, replay_rect.topleft)
        pygame.display.flip()

# Function to wrap text
def wrap_text(text, font, max_width):
    words = text.split()
    lines = []
    current_line = ""
    for word in words:
        if font.size(current_line + " " + word)[0] <= max_width:
            current_line += " " + word if current_line else word
        else:
            lines.append(current_line)
            current_line = word
    if current_line:
        lines.append(current_line)
    return lines

# Function to display text
def display_text(screen, text, position):
    font = pygame.font.Font(None, 36)
    lines = wrap_text(text, font, window_size[0] - 60)
    y = position[1]
    for line in lines:
        text_surface = font.render(line, True, (255, 255, 255))
        screen.blit(text_surface, (position[0], y))
        y += font.get_height()

# Function to display the boss dialogue
def display_boss_dialogue(screen, text):
    font = pygame.font.Font(None, 28)
    lines = wrap_text(text, font, 200)  # Adjust width for the smaller box
    dialogue_box = pygame.Rect(550, 150, 200, 100)  # Smaller box on the right side
    pygame.draw.rect(screen, (0, 0, 0), dialogue_box)
    pygame.draw.rect(screen, (255, 255, 255), dialogue_box, 2)
    y = dialogue_box.y + 10
    for line in lines:
        text_surface = font.render(line, True, (255, 255, 255))
        screen.blit(text_surface, (dialogue_box.x + 10, y))
        y += font.get_height()

def run_level1():
    pygame.key.set_repeat(0)
    clock = pygame.time.Clock()
    font = pygame.font.Font(None, 36)
    level_1_state["typed_word"] = ""
    level_1_state["frame_count"] = 0
    level_1_state["show_death_screen"] = False
    boss_active = False
    boss_paragraph = generate_random_paragraph()
    boss_typed = ""

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_BACKSPACE:
                    if level_1_state["boss_active"]:
                        level_1_state["boss_typed"] = level_1_state["boss_typed"][:-1]
                    else:
                        level_1_state["typed_word"] = level_1_state["typed_word"][:-1]
                elif event.key == pygame.K_RETURN:
                    if level_1_state["boss_active"]:
                        if level_1_state["boss_typed"].strip().lower() == level_1_state["boss_paragraph"].strip().lower():
                            destroy_sound.play()
                            level_1_state["flame_animations"].append({"position": level_1_state["boss_position"], "frame": 0})
                            # Switch back to background music
                            pygame.mixer.music.stop()
                            pygame.mixer.music.load(background_music_path)
                            pygame.mixer.music.play(-1)
                            display_win_page(window, level_1_state["score"])
                            game_state["current_level"] = "level_2"
                            return
                    else:
                        for tree in level_1_state["trees"]:
                            if tree["word"] == level_1_state["typed_word"].lower():
                                destroy_sound.play()
                                level_1_state["flame_animations"].append({"position": tree["position"], "frame": 0})
                                level_1_state["trees"].remove(tree)
                                level_1_state["score"] += 1
                                level_1_state["trees_destroyed"] += 1
                                if level_1_state["trees_destroyed"] == 10:
                                    level_1_state["wave"] = 2
                                elif level_1_state["trees_destroyed"] == 20:
                                    create_boss()
                                    level_1_state["wave"] = 3
                                elif level_1_state["trees_destroyed"] == 30 and not level_1_state["boss_active"]:
                                    display_win_page(window, level_1_state["score"])
                                    game_state["current_level"] = "level_2"
                                    return
                                break
                        level_1_state["typed_word"] = ""
                else:
                    if level_1_state["boss_active"]:
                        level_1_state["boss_typed"] += event.unicode.lower()
                    else:
                        level_1_state["typed_word"] += event.unicode.lower()

        if level_1_state["show_death_screen"]:
            display_death_page(window, level_1_state["score"])
            fade_out(window)
            game_state["current_level"] = "level_1"
            level_1_state["trees"].clear()
            for _ in range(5):
                create_tree(random.choice(words), 1.0)
            level_1_state["typed_word"] = ""
            level_1_state["lives"] = 3
            level_1_state["score"] = 0
            level_1_state["trees_destroyed"] = 0
            level_1_state["wave"] = 1
            pygame.mixer.music.play(-1)
            level_1_state["show_death_screen"] = False
            continue

        window.blit(background_image, (0, 0))

        y_offset = player["amplitude"] * math.sin(player["frequency"] * level_1_state["frame_count"])
        player_position_with_offset = (
            player["position"][0],
            player["base_position"][1] + y_offset,
        )
        window.blit(
            student_sprite,
            (
                player_position_with_offset[0] - student_sprite.get_width() / 2,
                player_position_with_offset[1] - student_sprite.get_height() / 2,
            ),
        )

        if level_1_state["boss_active"]:
            boss_position = level_1_state["boss_position"]
            boss_position[0] -= level_1_state["boss_speed"]
            if boss_position[0] < player_position_with_offset[0] + student_sprite.get_width() / 2:
                level_1_state["lives"] = 0
                display_death_page(window, level_1_state["score"])
                fade_out(window)
                game_state["current_level"] = "level_1"
                level_1_state["trees"].clear()
                for _ in range(5):
                    create_tree(random.choice(words), 1.0)
                level_1_state["typed_word"] = ""
                level_1_state["lives"] = 3
                level_1_state["score"] = 0
                level_1_state["trees_destroyed"] = 0
                level_1_state["wave"] = 1
                pygame.mixer.music.play(-1)
                level_1_state["show_death_screen"] = False
                continue

            window.blit(boss_sprite, boss_position)
            display_text(window, level_1_state["boss_paragraph"], (boss_position[0] - 50, boss_position[1] - 50))
            display_text(window, level_1_state["boss_typed"], (boss_position[0] - 50, boss_position[1]))

            if not level_1_state["boss_dialogue_shown"]:
                display_boss_dialogue(window, "Prepare to be defeated!")
                level_1_state["boss_dialogue_shown"] = True
                pygame.display.flip()
                pygame.time.delay(2000)  # Show the dialogue for 2 seconds

        for tree in level_1_state["trees"]:
            window.blit(
                tree_sprite,
                (
                    tree["position"][0] - tree_sprite.get_width() / 2,
                    tree["position"][1] - tree_sprite.get_height() / 2,
                ),
            )
            tree["position"][0] -= tree["speed"]

            draw_text_with_outline(window, tree["word"], font, (255, 255, 255), (0, 0, 0), tree["position"][0] - font.size(tree["word"])[0] / 2, tree["position"][1] - 50)

            if tree["position"][0] < player["position"][0] + student_sprite.get_width() / 2:
                level_1_state["trees"].remove(tree)
                level_1_state["lives"] -= 1
                hit_sound.play()
                if level_1_state["lives"] == 0:
                    pygame.mixer.music.stop()
                    end_sound.play()
                    level_1_state["show_death_screen"] = True

        for animation in level_1_state["flame_animations"][:]:
            frame = animation["frame"]
            if frame < len(flame_frames):
                window.blit(
                    flame_frames[frame],
                    (
                        animation["position"][0] - flame_frames[frame].get_width() / 2,
                        animation["position"][1] - flame_frames[frame].get_height() / 2,
                    ),
                )
                animation["frame"] += 1
            else:
                level_1_state["flame_animations"].remove(animation)

        text = font.render(level_1_state["typed_word"], True, (255, 255, 255))
        window.blit(text, (10, 10))

        score_text = font.render(f"Score: {level_1_state['score']}", True, (255, 255, 255))
        window.blit(score_text, (window_size[0] - score_text.get_width() - 10, 10))

        for i in range(level_1_state["lives"]):
            window.blit(heart_sprite, (10 + i * 40, 50))

        pygame.display.flip()

        if level_1_state["wave"] == 1 and random.randint(1, 200) > 195:
            new_word = random.choice(words)
            create_tree(new_word, 1.0)
        elif level_1_state["wave"] == 2 and random.randint(1, 150) > 140:
            new_word = random.choice(words)
            create_tree(new_word, 2.0)
        elif level_1_state["wave"] == 3 and random.randint(1, 100) > 90:
            new_word = random.choice(words)
            create_tree(new_word, 3.0)

        level_1_state["frame_count"] += 1
        clock.tick(30)
