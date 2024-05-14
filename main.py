import sys
import pygame
import random
import math
import json


# Initialize Pygame
pygame.init()

# Set up the game window
window_size = (800, 600)
window = pygame.display.set_mode(window_size)
pygame.display.set_caption("Cardinal Conquest")

# Load and set up sounds
pygame.mixer.init()
hit_sound = pygame.mixer.Sound("sound/hit.mp3")
end_sound = pygame.mixer.Sound("sound/end.mp3")
destroy_sound = pygame.mixer.Sound("sound/destroy.wav")  # Load the destruction sound

# Load music
pygame.mixer.music.load("sound/background.mp3")

# Load sprites
background_image = pygame.image.load("images/background.png")
background_image = pygame.transform.scale(
    background_image, window_size
)  # Scale to fit window size
tree_sprite = pygame.image.load("images/tree.png")
tree_sprite = pygame.transform.scale(tree_sprite, (60, 60))  # Scale to appropriate size
heart_sprite = pygame.image.load("images/heart.png")
heart_sprite = pygame.transform.scale(
    heart_sprite, (30, 30)
)  # Scale to appropriate size
student_sprite = pygame.image.load("images/student.png")
student_sprite = pygame.transform.scale(
    student_sprite, (95, 95)
)  # Scale to appropriate size

# Load logo image
logo_image = pygame.image.load("images/logo.png")
logo_image = pygame.transform.scale(logo_image, (350, 350))  # Adjust the size as needed

# Load flame animation frames
flame_frames = []
N = 2  # Number of flame frames
for i in range(
    1, N + 1
):  # Assuming frames are named flame1.png, flame2.png, ..., flameN.png
    flame_image = pygame.image.load(f"images/flame{i}.png")
    flame_image = pygame.transform.scale(
        flame_image, (50, 50)
    )  # Scale to appropriate size
    flame_frames.extend(
        [flame_image] * 5
    )  # Repeat each frame to make the animation last longer

# Define player and tree attributes
player = {
    "position": (50, 275),  # Position the player on the left side
    "base_position": (50, 275),  # Base position for the oscillation
    "amplitude": 5,  # Amplitude of the oscillation
    "frequency": 0.1,  # Frequency of the oscillation
}

trees = []
flame_animations = []  # List to track active flame animations
lives = 3  # Start with 3 lives
score = 0  # Initialize score

# List of words for trees
with open("./assets/words.json", "r") as file:
    words = json.load(file)


# Function to create a new tree
def create_tree(word):
    tree = {
        "position": [random.randint(800, 1600), random.randint(50, 550)],
        "radius": 20,
        "speed": random.uniform(0.5, 1.5),  # Reduced speed for trees
        "word": word,
    }
    trees.append(tree)


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
    surface_height = (
        line_height * len(lines) * 2
    )  # Increase surface height for more spacing between lines
    scroll_surface = pygame.Surface((window_size[0], surface_height), pygame.SRCALPHA)

    # Render each line of text
    for i, line in enumerate(lines):
        text_surface = font.render(line, True, color)
        scroll_surface.blit(
            text_surface,
            (window_size[0] // 2 - text_surface.get_width() // 2, i * line_height * 2),
        )

    # Scroll the text
    while y > -surface_height:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        window.fill((0, 0, 0))
        window.blit(scroll_surface, (0, y))

        # Calculate logo position
        logo_y_position = y + surface_height + 20
        window.blit(
            logo, (window_size[0] // 2 - logo.get_width() // 2, logo_y_position)
        )

        pygame.display.flip()
        y -= speed
        pygame.time.delay(20)  # Decrease the delay to speed up the scrolling


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
    replay_rect = replay_text.get_rect(
        center=(window_size[0] // 2, window_size[1] // 2 + 100)
    )

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


# Lore text
lore_text = "In the mystical land of Stanford, you are the last guardian of the ancient Tree of Knowledge. Evil trees have been corrupted by dark forces and are marching towards the heart of the campus. Your task is to protect the sacred tree by using your typing skills to defeat the corrupted trees. Type the words associated with each tree to destroy them and save Stanford! Welcome to CARDINAL CONQUEST!"

# Wrap the lore text
font = pygame.font.Font(None, 36)
wrapped_lore_text = wrap_text(
    lore_text, font, window_size[0] - 40
)  # Adjust width to fit within the window

# Game state variable
game_state = "lore"

# Intro shown flag
intro_shown = False

# Set up the clock to control the frame rate
clock = pygame.time.Clock()

# Main game loop
frame_count = 0  # Initialize a frame counter
while True:
    if game_state == "lore" and not intro_shown:
        pygame.mixer.music.play(-1)  # Start playing the background music
        fade_in(window)
        display_scrolling_text(
            window, wrapped_lore_text, font, (255, 255, 255), 1, logo_image
        )  # Adjust the speed to make it slower
        fade_out(window)
        intro_shown = True
        game_state = "playing"
        trees.clear()
        for _ in range(5):  # Start with fewer trees
            create_tree(random.choice(words))
        typed_word = ""
        lives = 3
        score = 0

    elif game_state == "playing":
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_BACKSPACE:
                    typed_word = typed_word[:-1]
                elif event.key == pygame.K_RETURN:
                    # Check if typed word matches any tree word
                    for tree in trees:
                        if tree["word"] == typed_word:
                            destroy_sound.play()  # Play destruction sound effect
                            flame_animations.append(
                                {"position": tree["position"], "frame": 0}
                            )  # Start flame animation
                            trees.remove(tree)
                            score += 1
                            break
                    typed_word = ""
                else:
                    typed_word += event.unicode

        # Fill the window with the background image
        window.blit(background_image, (0, 0))

        # Calculate the vertical offset using a sine wave
        y_offset = player["amplitude"] * math.sin(player["frequency"] * frame_count)

        # Draw the player with the vertical offset
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

        # Draw and move the trees
        for tree in trees:
            # Draw the tree sprite
            window.blit(
                tree_sprite,
                (
                    tree["position"][0] - tree_sprite.get_width() / 2,
                    tree["position"][1] - tree_sprite.get_height() / 2,
                ),
            )
            tree["position"][0] -= tree["speed"]

            # Draw the word above the tree
            font = pygame.font.Font(None, 36)
            word_text = font.render(tree["word"], True, (255, 255, 255))
            window.blit(
                word_text,
                (
                    tree["position"][0] - word_text.get_width() / 2,
                    tree["position"][1] - 50,
                ),
            )

            # Check if tree reaches the player
            if (
                tree["position"][0]
                < player["position"][0] + student_sprite.get_width() / 2
            ):
                trees.remove(tree)
                lives -= 1
                hit_sound.play()  # Play hit sound effect
                if lives == 0:
                    pygame.mixer.music.stop()  # Stop background music
                    end_sound.play()  # Play end sound effect
                    fade_out(window)
                    game_state = "death"

        # Update and draw flame animations
        for animation in flame_animations[:]:
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
                flame_animations.remove(animation)  # Remove animation when complete

        # Display the typed word
        font = pygame.font.Font(None, 74)
        text = font.render(typed_word, True, (255, 255, 255))
        window.blit(text, (10, 10))

        # Display the score
        score_text = font.render(f"Score: {score}", True, (255, 255, 255))
        window.blit(score_text, (window_size[0] - score_text.get_width() - 10, 10))

        # Display the lives
        for i in range(lives):
            window.blit(heart_sprite, (10 + i * 40, 50))

        # Update the display
        pygame.display.flip()

        # Add new trees less frequently
        if random.randint(1, 200) > 195:
            new_word = random.choice(words)
            create_tree(new_word)

        # Increment the frame counter
        frame_count += 1

        # Control the frame rate
        clock.tick(30)  # Set the frame rate to 30 FPS

    elif game_state == "death":
        display_death_page(window, score)
        fade_out(window)
        game_state = "playing"
        trees.clear()
        for _ in range(5):  # Start with fewer trees
            create_tree(random.choice(words))
        typed_word = ""
        lives = 3
        score = 0
        pygame.mixer.music.play(-1)  # Start playing the background music
