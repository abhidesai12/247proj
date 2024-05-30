import pygame

from levels.level3.player import Player
from levels.level3.enemy import Enemy
from levels.level3.field import Field
from g import window_size, window, game_state


def run_level3():
    SCREEN_WIDTH = window_size[0]
    SCREEN_HEIGHT = window_size[1]

    FIELD_X = 100
    FIELD_Y = 100
    FIELD_WIDTH = 600
    FIELD_HEIGHT = 500

    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

    isRunning = True

    start_zone = Field(FIELD_X, FIELD_Y, 100, 70)
    player = Player(
        start_zone.x + start_zone.width // 2,
        start_zone.y + start_zone.height // 2,
        FIELD_X,
        FIELD_Y,
        FIELD_WIDTH,
        FIELD_HEIGHT,
    )

    enemies = [
        Enemy(
            [(100, 100), (100, 200), (200, 200), (200, 100)],
            vel=9,
            color=(255, 0, 0),
            field_x=FIELD_X,
            field_y=FIELD_Y,
        ),
        Enemy(
            [(150, 150), (150, 300), (300, 300), (300, 150)],
            vel=12,
            color=(0, 255, 0),
            field_x=FIELD_X,
            field_y=FIELD_Y,
        ),
        Enemy(
            [(200, 200), (200, 400), (400, 400), (400, 200)],
            vel=15,
            color=(0, 0, 255),
            field_x=FIELD_X,
            field_y=FIELD_Y,
        ),
        Enemy(
            [(250, 240), (250, 490), (500, 490), (500, 240)],
            vel=18,
            color=(255, 255, 0),
            field_x=FIELD_X,
            field_y=FIELD_Y,
        ),
        Enemy(
            [(300, 100), (300, 400)],
            vel=6,
            color=(255, 0, 255),
            field_x=FIELD_X,
            field_y=FIELD_Y,
        ),
        Enemy(
            [(400, 100), (400, 400)],
            vel=6,
            color=(0, 255, 255),
            field_x=FIELD_X,
            field_y=FIELD_Y,
        ),
    ]

    finish_zone = Field(600, 575, 100, 70, color=(255, 165, 0))
    field_image = pygame.image.load("./levels/level3/bg.png")
    field_image = pygame.transform.scale(field_image, (FIELD_WIDTH, FIELD_HEIGHT))

    font = pygame.font.Font("freesansbold.ttf", 18)

    def update():
        keys = pygame.key.get_pressed()
        player.move(keys)
        for enemy in enemies:
            enemy.move()

        if player.draw(screen).collidelist([enemy.draw(screen) for enemy in enemies]) != -1:
            player.reset()
            player.deaths += 1
        if player.draw(screen).collidelist([finish_zone.draw(screen)]) != -1:
            print("Finished")

    def draw():
        screen.fill((255, 255, 255))
        screen.blit(field_image, (FIELD_X, FIELD_Y))
        start_zone.draw(screen)
        finish_zone.draw(screen)
        player.draw(screen)
        for enemy in enemies:
            enemy.draw(screen)

        deathCounter = font.render("YOU'VE DIED " + str(player.deaths) + " TIMES. HAHA", True, (0, 0, 0))
        screen.blit(deathCounter, (300, 50))

        pygame.display.update()

    while isRunning:
        pygame.time.delay(50)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                isRunning = False

        update()
        draw()

    game_state["current_level"] = "intro"
