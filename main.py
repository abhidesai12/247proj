import pygame
import sys
import random

# Initialize Pygame
pygame.init()

# Set up the game window
window_size = (800, 600)
window = pygame.display.set_mode(window_size)
pygame.display.set_caption("Typing Game")

# Load and play background music
pygame.mixer.music.load('background.mp3')
pygame.mixer.music.play(-1)  # -1 means the music will loop indefinitely

# Load tree sprite
tree_sprite = pygame.image.load('tree.png')
tree_sprite = pygame.transform.scale(tree_sprite, (50, 50))  # Scale to appropriate size

# Define player and tree attributes
player = {
    "position": (50, 300),  # Position the player on the left side
    "color": (255, 255, 255),
    "radius": 30
}

trees = []

# List of words for trees
words = [
    "Stanford", "Cardinal", "Tree", "Hoover", "Quad", "Library", "Dinkelspiel", "Memorial", 
    "Oval", "Cantor", "Fountain", "Engineering", "Humanities", "Economics", "Silicon", 
    "Valley", "Palo", "Alto", "Research", "Innovation", "Campus", "Lecture", "Study", 
    "Professor", "Student", "Graduation", "Ceremony", "Bookstore", "Athletics", "Championship", 
    "Scholar", "Experiment", "Laboratory", "Computer", "Science", "Mathematics", "Physics", 
    "Biology", "Chemistry", "Philosophy", "History", "Art", "Music", "Theater", "Dance", 
    "Symposium", "Conference", "Seminar", "Dormitory", "Fellowship"
]

# Function to create a new tree
def create_tree(word):
    tree = {
        "position": [random.randint(800, 1600), random.randint(50, 550)],
        "radius": 20,
        "speed": random.uniform(0.5, 1.5),  # Reduced speed for trees
        "word": word
    }
    trees.append(tree)

# Function to wrap text
def wrap_text(text, font, max_width):
    words = text.split(' ')
    lines = []
    current_line = ''
    for word in words:
        test_line = current_line + word + ' '
        if font.size(test_line)[0] <= max_width:
            current_line = test_line
        else:
            lines.append(current_line)
            current_line = word + ' '
    lines.append(current_line)
    return lines

# Function to display scrolling text
def display_scrolling_text(window, lines, font, color, speed):
    y = window_size[1]
    line_height = font.get_height()
    surface_height = line_height * len(lines)
    scroll_surface = pygame.Surface((window_size[0], surface_height), pygame.SRCALPHA)
    
    # Render each line of text
    for i, line in enumerate(lines):
        text_surface = font.render(line, True, color)
        scroll_surface.blit(text_surface, (window_size[0] // 2 - text_surface.get_width() // 2, i * line_height))
    
    # Scroll the text
    while y > -surface_height:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
        
        window.fill((0, 0, 0))
        window.blit(scroll_surface, (0, y))
        pygame.display.flip()
        y -= speed
        pygame.time.delay(50)  # Increase the delay to slow down the scrolling

# Lore text
lore_text = "In the mystical land of Stanford, you are the last guardian of the ancient Tree of Knowledge. Evil trees have been corrupted by dark forces and are marching towards the heart of the campus. Your task is to protect the sacred tree by using your typing skills to defeat the corrupted trees. Type the words associated with each tree to destroy them and save Stanford!"

# Wrap the lore text
font = pygame.font.Font(None, 36)
wrapped_lore_text = wrap_text(lore_text, font, window_size[0] - 40)  # Adjust width to fit within the window

# Display the lore scene before starting the game
display_scrolling_text(window, wrapped_lore_text, font, (255, 255, 255), 1)  # Adjust the speed to make it slower

# Create initial trees
for word in words:
    create_tree(word)

typed_word = ""
score = 0

# Set up the clock to control the frame rate
clock = pygame.time.Clock()

# Main game loop
while True:
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
                        trees.remove(tree)
                        score += 1
                        break
                typed_word = ""
            else:
                typed_word += event.unicode

    # Fill the window with a black background
    window.fill((0, 0, 0))

    # Draw the player
    pygame.draw.circle(window, player["color"], player["position"], player["radius"])

    # Draw and move the trees
    for tree in trees:
        # Draw the tree sprite
        window.blit(tree_sprite, (tree["position"][0] - tree_sprite.get_width() / 2, tree["position"][1] - tree_sprite.get_height() / 2))
        tree["position"][0] -= tree["speed"]

        # Draw the word above the tree
        font = pygame.font.Font(None, 36)
        word_text = font.render(tree["word"], True, (255, 255, 255))
        window.blit(word_text, (tree["position"][0] - word_text.get_width() / 2, tree["position"][1] - 50))

        # Check if tree reaches the player
        if tree["position"][0] < player["position"][0] + player["radius"]:
            print("Game Over")
            pygame.quit()
            sys.exit()

    # Display the typed word
    font = pygame.font.Font(None, 74)
    text = font.render(typed_word, True, (255, 255, 255))
    window.blit(text, (10, 10))

    # Display the score
    score_text = font.render(f"Score: {score}", True, (255, 255, 255))
    window.blit(score_text, (window_size[0] - score_text.get_width() - 10, 10))

    # Update the display
    pygame.display.flip()

    # Add new trees
    if random.randint(1, 100) > 98:
        new_word = random.choice(words)
        create_tree(new_word)

    # Control the frame rate
    clock.tick(30)  # Set the frame rate to 30 FPS
