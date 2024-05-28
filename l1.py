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

# Load sounds
hit_sound = pygame.mixer.Sound("sound/hit.mp3")
end_sound = pygame.mixer.Sound("sound/end.mp3")
destroy_sound = pygame.mixer.Sound("sound/destroy.wav")


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
}

# Define player attributes
player = {
    "position": (50, 275),
    "base_position": (50, 275),
    "amplitude": 5,
    "frequency": 0.1,
}


# Function to create a new tree
def create_tree(word):
    tree = {
        "position": [random.randint(800, 1600), random.randint(50, 550)],
        "radius": 20,
        "speed": random.uniform(0.5, 1.5) + level_1_state["score"] * 0.01,
        "word": word,
    }
    level_1_state["trees"].append(tree)


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


# Function to run level 1
def run_level1():
    clock = pygame.time.Clock()
    font = pygame.font.Font(None, 36)
    level_1_state["typed_word"] = ""
    level_1_state["frame_count"] = 0
    level_1_state["show_death_screen"] = False

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_BACKSPACE:
                    level_1_state["typed_word"] = level_1_state["typed_word"][:-1]
                elif event.key == pygame.K_RETURN:
                    for tree in level_1_state["trees"]:
                        if tree["word"] == level_1_state["typed_word"]:
                            destroy_sound.play()
                            level_1_state["flame_animations"].append({"position": tree["position"], "frame": 0})
                            level_1_state["trees"].remove(tree)
                            level_1_state["score"] += 1
                            break
                    level_1_state["typed_word"] = ""
                else:
                    level_1_state["typed_word"] += event.unicode

        if level_1_state["show_death_screen"]:
            display_death_page(window, level_1_state["score"])
            fade_out(window)
            game_state["current_level"] = "level_1"
            level_1_state["trees"].clear()
            for _ in range(5):
                create_tree(random.choice(words))
            level_1_state["typed_word"] = ""
            level_1_state["lives"] = 3
            level_1_state["score"] = 0
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

        if random.randint(1, 200) > 195:
            new_word = random.choice(words)
            create_tree(new_word)

        level_1_state["frame_count"] += 1
        clock.tick(30)

