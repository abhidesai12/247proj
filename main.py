import pygame
import sys
import random

# Initialize Pygame
pygame.init()

# Set up the game window
window_size = (800, 600)
window = pygame.display.set_mode(window_size)
pygame.display.set_caption("Typing Game")

# Define player and tree attributes
player = {
    "position": (400, 500),
    "color": (255, 255, 255),
    "radius": 30
}

trees = []

# List of words for trees
words = ["tree", "bark", "leaf", "wood"]

# Function to create a new tree
def create_tree(word):
    tree = {
        "position": [random.randint(800, 1600), random.randint(50, 550)],
        "color": (0, 255, 0),
        "radius": 20,
        "speed": random.randint(1, 3),
        "word": word
    }
    trees.append(tree)

# Create initial trees
for word in words:
    create_tree(word)

typed_word = ""

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
        pygame.draw.circle(window, tree["color"], tree["position"], tree["radius"])
        tree["position"][0] -= tree["speed"]

        # Check if tree reaches the player
        if tree["position"][0] < player["position"][0]:
            print("Game Over")
            pygame.quit()
            sys.exit()

    # Display the typed word
    font = pygame.font.Font(None, 74)
    text = font.render(typed_word, True, (255, 255, 255))
    window.blit(text, (10, 10))

    # Update the display
    pygame.display.flip()

    # Add new trees
    if random.randint(1, 100) > 98:
        new_word = random.choice(words)
        create_tree(new_word)
