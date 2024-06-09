import pygame
import sys
from levels.level3.player import Player
from levels.level3.enemy import Enemy
from levels.level3.field import Field
from g import window_size, window, game_state


pygame.mixer.init()
hit_sound = pygame.mixer.Sound("./sound/hit.mp3")


def fade_in(window, color=(0, 0, 0)):
    """Function to fade in."""
    fade_surface = pygame.Surface(window.get_size())
    fade_surface.fill(color)
    for alpha in range(0, 255, 5):
        fade_surface.set_alpha(alpha)
        window.blit(fade_surface, (0, 0))
        pygame.display.update()
        pygame.time.delay(10)


def fade_out(window, color=(0, 0, 0)):
    """Function to fade out."""
    fade_surface = pygame.Surface(window.get_size())
    fade_surface.fill(color)
    for alpha in range(255, -1, -5):
        fade_surface.set_alpha(alpha)
        window.blit(fade_surface, (0, 0))
        pygame.display.update()
        pygame.time.delay(10)


def show_win_screen(screen):
    fade_in(screen)
    font = pygame.font.Font(None, 74)
    win_text = font.render("Congrats you won!", True, (0, 255, 0))

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if exit_rect.collidepoint(event.pos):
                    return

        screen.fill((0, 0, 0))
        screen.blit(win_text, (screen.get_width() // 2 - win_text.get_width() // 2, screen.get_height() // 2 - win_text.get_height() // 2))
        pygame.display.flip()


def run_level3():
    SCREEN_WIDTH = window_size[0]
    SCREEN_HEIGHT = window_size[1]

    FIELD_X = 150
    FIELD_Y = 80
    FIELD_WIDTH = 500
    FIELD_HEIGHT = 500

    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

    walk1_img = pygame.image.load("./images/walk1.png")
    walk2_img = pygame.image.load("./images/walk2.png")

    class Player:
        def __init__(self, x, y, field_x, field_y, field_width, field_height, width=50, height=50, vel=5, color=(0, 255, 0), deaths=0):
            self.start_x = x
            self.start_y = y
            self.x = x
            self.y = y
            self.width = width
            self.height = height
            self.vel = vel
            self.color = color
            self.deaths = deaths
            self.field_x = field_x
            self.field_y = field_y
            self.field_width = field_width
            self.field_height = field_height

            self.walk1_img = pygame.transform.scale(walk1_img, (self.width, self.height))
            self.walk2_img = pygame.transform.scale(walk2_img, (self.width, self.height))
            self.current_image = self.walk1_img
            self.walking = False
            self.walk_count = 0
            self.facing_left = False

        def move(self, keys):
            self.walking = False
            if keys[pygame.K_a] and self.x > self.field_x + self.width:
                self.x -= self.vel
                self.walking = True
                self.facing_left = True
            if keys[pygame.K_d] and self.x < self.field_x + self.field_width - self.width:
                self.x += self.vel
                self.walking = True
                self.facing_left = False
            if keys[pygame.K_s] and self.y < self.field_y + self.field_height - self.height:
                self.y += self.vel
                self.walking = True
            if keys[pygame.K_w] and self.y > self.field_y + self.height:
                self.y -= self.vel
                self.walking = True

        def update(self):
            if self.walking:
                self.walk_count = (self.walk_count + 1) % 20
                if self.walk_count < 10:
                    self.current_image = self.walk1_img
                else:
                    self.current_image = self.walk2_img

                if self.facing_left:
                    self.current_image = pygame.transform.flip(self.current_image, True, False)
            else:
                self.current_image = self.walk1_img

        def draw(self, screen):
            self.update()
            return screen.blit(self.current_image, (self.x, self.y))

        def reset(self):
            self.x = self.start_x
            self.y = self.start_y

    def play_level(speed_multiplier, background_image, base_color, music_path=None):
        if music_path:
            pygame.mixer.music.load(music_path)
            pygame.mixer.music.play(-1)

        is_running = True

        start_zone = Field(FIELD_X + 235, FIELD_Y + 5, 60, 10)

        finish_zone = Field(FIELD_X + 235, FIELD_Y + FIELD_HEIGHT - 50, 60, 10, color=(60, 163, 5))
        player = Player(
            start_zone.x + start_zone.width // 2,
            start_zone.y + start_zone.height // 2,
            FIELD_X,
            FIELD_Y,
            FIELD_WIDTH,
            FIELD_HEIGHT - 10,
        )

        enemies = [
            Enemy(
                [(200, 210), (300, 260), (250, 260), (250, 310)],
                vel=2 * speed_multiplier,
                color=(255, 0, 0),
                field_x=FIELD_X,
                field_y=FIELD_Y,
            ),
            Enemy(
                [(200, 210), (200, 360), (350, 360), (350, 210)],
                vel=4 * speed_multiplier,
                color=(0, 255, 0),
                field_x=FIELD_X,
                field_y=FIELD_Y,
            ),
            Enemy(
                [(250, 260), (250, 460), (450, 460), (450, 260)],
                vel=6 * speed_multiplier,
                color=(0, 0, 255),
                field_x=FIELD_X,
                field_y=FIELD_Y,
            ),
            Enemy(
                [(300, 300), (300, 500), (550, 500), (550, 300)],
                vel=7 * speed_multiplier,
                color=(255, 255, 0),
                field_x=FIELD_X,
                field_y=FIELD_Y,
            ),
            Enemy(
                [(350, 160), (350, 460)],
                vel=1 * speed_multiplier,
                color=(255, 0, 255),
                field_x=FIELD_X,
                field_y=FIELD_Y,
            ),
            Enemy(
                [(450, 160), (450, 460)],
                vel=1 * speed_multiplier,
                color=(0, 255, 255),
                field_x=FIELD_X,
                field_y=FIELD_Y,
            ),
            Enemy(
                [(FIELD_X, FIELD_Y + FIELD_HEIGHT // 2 + 10), (FIELD_X + FIELD_WIDTH, FIELD_Y + FIELD_HEIGHT // 2 + 10)],
                vel=3 * speed_multiplier,
                color=(128, 0, 128),
                field_x=FIELD_X,
                field_y=FIELD_Y,
            ),
            Enemy(
                [(FIELD_X, FIELD_Y + FIELD_HEIGHT // 3 + 10), (FIELD_X + FIELD_WIDTH, FIELD_Y + FIELD_HEIGHT // 3 + 10)],
                vel=5 * speed_multiplier,
                color=(0, 128, 128),
                field_x=FIELD_X,
                field_y=FIELD_Y,
            ),
        ]

        heart_image = pygame.image.load("./images/heart.png")
        heart_image = pygame.transform.scale(heart_image, (30, 30))
        lives = 3

        font = pygame.font.Font("freesansbold.ttf", 18)

        def update():
            nonlocal lives
            nonlocal is_running
            keys = pygame.key.get_pressed()
            player.move(keys)
            for enemy in enemies:
                enemy.move()

            if player.draw(screen).collidelist([enemy.draw(screen) for enemy in enemies]) != -1:
                hit_sound.play()
                player.reset()
                player.deaths += 1
                lives -= 1
                if lives <= 0:
                    show_death_screen()
                    game_state["current_level"] = "level_3"
                    is_running = False
                    return

            if player.draw(screen).collidelist([finish_zone.draw(screen)]) != -1:
                is_running = False
                return

        def draw():
            screen.fill(base_color)
            screen.blit(background_image, (FIELD_X, FIELD_Y))
            start_zone.draw(screen)
            finish_zone.draw(screen)
            player.draw(screen)
            for enemy in enemies:
                enemy.draw(screen)

            deathCounter = font.render("WELCOME UPSTAIRS! YOU'VE DIED " + str(player.deaths) + " TIMES." if base_color == (0, 0, 0) else "YOU'VE DIED " + str(player.deaths) + " TIMES. HAHA", True, (255, 255, 255) if base_color == (0, 0, 0) else (0, 0, 0))
            screen.blit(deathCounter, (225, 50))

            for i in range(lives):
                screen.blit(heart_image, (10 + i * 40, 10))

            pygame.display.update()

        def show_death_screen():
            fade_in(screen)
            death_font = pygame.font.Font(None, 74)
            death_text = death_font.render("You Died", True, (255, 0, 0))
            score_text = death_font.render(f"Score: " + str(player.deaths), True, (255, 255, 255))
            replay_text = death_font.render("Replay Game", True, (255, 255, 255))
            replay_rect = replay_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 100))

            while True:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        sys.exit()
                    elif event.type == pygame.MOUSEBUTTONDOWN:
                        if replay_rect.collidepoint(event.pos):
                            game_state["current_level"] = "level_3"
                            run_level3()
                            return

                screen.fill((0, 0, 0))
                screen.blit(
                    death_text,
                    (
                        SCREEN_WIDTH // 2 - death_text.get_width() // 2,
                        SCREEN_HEIGHT // 2 - death_text.get_height() - 75 // 2,
                    ),
                )
                screen.blit(
                    score_text,
                    (SCREEN_WIDTH // 2 - score_text.get_width() // 2, SCREEN_HEIGHT // 2),
                )
                screen.blit(replay_text, replay_rect.topleft)
                pygame.display.flip()

        while is_running:
            pygame.time.delay(50)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    is_running = False

            update()
            draw()

        if music_path:
            pygame.mixer.music.stop()
        return lives > 0

    field_image = pygame.image.load("./images/bg2.png")
    field_image = pygame.transform.scale(field_image, (FIELD_WIDTH, FIELD_HEIGHT))

    new_background_image = pygame.image.load("./images/bg2.png")
    new_background_image = pygame.transform.scale(new_background_image, (FIELD_WIDTH, FIELD_HEIGHT))

    if not play_level(1, field_image, (255, 255, 255)):
        return

    fade_out(screen)
    fade_in(screen)

    if not play_level(2, new_background_image, (0, 0, 0), "sound/dunk.mp3"):
        return

    pygame.mixer.music.load("sound/background.mp3")
    pygame.mixer.music.play(-1)

    game_state["current_level"] = "final_level"
