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
    "Scholar", "Experiment", "Laboratory", "Computer", "Science", "Mathematics"]


# Function to create a new tree
def create_tree(word):
    tree = {
        "position": [random.randint(800, 1600), random.randint(50, 550)],
        "color": (0, 255, 0),
        "radius": 20,
        "speed": random.uniform(0.5, 1.5),  # Reduced speed for trees
        "word": word
    }
    trees.append(tree)

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
        pygame.draw.circle(window, tree["color"], tree["position"], tree["radius"])
        tree["position"][0] -= tree["speed"]

        # Draw the word above the tree
        font = pygame.font.Font(None, 36)
        word_text = font.render(tree["word"], True, (255, 255, 255))
        window.blit(word_text, (tree["position"][0] - word_text.get_width() / 2, tree["position"][1] - 30))

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
