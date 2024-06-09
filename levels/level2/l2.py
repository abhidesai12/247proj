import pygame as pg
import sys
import random
from os import path
from .settings import *
from .sprites import *
from .tmap import *
from .gui import *
from time import sleep
from random import randint, randrange, uniform
from g import game_state


def fade_in(window, color=(0, 0, 0)):
    """Function to fade in."""
    fade_surface = pg.Surface(window.get_size())
    fade_surface.fill(color)
    for alpha in range(0, 255, 5):
        fade_surface.set_alpha(alpha)
        window.blit(fade_surface, (0, 0))
        pg.display.update()
        pg.time.delay(10)


def fade_out(window, color=(0, 0, 0)):
    """Function to fade out."""
    fade_surface = pg.Surface(window.get_size())
    fade_surface.fill(color)
    for alpha in range(255, -1, -5):
        fade_surface.set_alpha(alpha)
        window.blit(fade_surface, (0, 0))
        pg.display.update()
        pg.time.delay(10)


class Game:
    """The main game class: Contains main game loop."""

    def __init__(self):
        """Initialize the game and its attributes."""
        pg.init()
        self.screen = pg.display.set_mode((WIDTH, HEIGHT))
        pg.display.set_caption(TITLE)
        self.clock = pg.time.Clock()
        pg.key.set_repeat(30, 30)
        self.load_data()
        self.spawn_rate = 3000
        self.last_spawn_time = pg.time.get_ticks()
        self.start_time = pg.time.get_ticks()

    def load_data(self):
        """Loads data from file, such as images, sounds, etc."""
        game_folder = path.dirname(__file__)
        img_folder = path.join(game_folder, "img")
        sound_folder = path.join(path.dirname(game_folder), "sound")
        self.map = Map(path.join(game_folder, "map_small.txt"))
        self.walk1_img = pg.image.load(path.join(img_folder, "walk1.png")).convert_alpha()
        self.walk2_img = pg.image.load(path.join(img_folder, "walk2.png")).convert_alpha()
        self.bullet_img = pg.image.load(path.join(img_folder, BULLET_IMG)).convert_alpha()
        self.mob_img = pg.image.load(path.join(img_folder, MOB_IMG)).convert_alpha()
        self.mob2_img = pg.image.load(path.join(img_folder, MOB_IMG2)).convert_alpha()
        self.mob3_img = pg.image.load(path.join(img_folder, MOB_IMG3)).convert_alpha()
        self.heart_img = pg.image.load(path.join(img_folder, "heart.png")).convert_alpha()
        self.heart_img = pg.transform.scale(self.heart_img, (30, 30))
        self.pausedScreen = pg.Surface(self.screen.get_size()).convert_alpha()
        self.pausedScreen.fill((0, 0, 0, 180))

        self.hit_sound = pg.mixer.Sound("sound/hit.mp3")
        self.end_sound = pg.mixer.Sound("sound/end.mp3")
        self.destroy_sound = pg.mixer.Sound("sound/destroy.wav")

    def new(self):
        """Initialize all variables and set up for new game."""
        self.all_sprites = pg.sprite.Group()
        self.walls = pg.sprite.Group()
        self.mobs = pg.sprite.Group()
        self.bullets = pg.sprite.Group()
        self.player = Player(self, 3, 3)
        self.player.librarians_killed = 0
        self.lives = 3
        for row, tiles in enumerate(self.map.map_data):
            for col, tile in enumerate(tiles):
                self.map_row = row
                self.map_col = col
                if tile == "1":
                    Wall(self, col, row)
                if tile == "2":
                    Wall2(self, col, row)
                if tile == "M":
                    Mob(self, col, row)
                if tile == "H":
                    Mob2(self, col, row)
                if tile == "T":
                    Mob3(self, col, row)

        self.camera = Camera(self.map.width, self.map.height)
        self.paused = False

    def run(self):
        """Runs the game, setup conditions for when to run and when not."""
        self.playing = True
        while self.playing:
            self.dt = self.clock.tick(FPS) / 1000
            self.events()
            if not self.paused:
                self.update()
            self.draw()

    def quit(self):
        """Call this when you quit the game."""
        pg.quit()
        sys.exit()

    def update(self):
        """Updates the loop for every frame, etc."""
        self.all_sprites.update()
        self.camera.update(self.player)

        hits = pg.sprite.spritecollide(self.player, self.mobs, False, collide_hit_rect)
        if hits:
            self.lives -= 1
            self.hit_sound.play()
            if self.lives <= 0:
                self.show_death_screen()
                game_state["current_level"] = "level_2"
                self.playing = False
                return
            self.player.pos = vec(3, 3) * TILESIZE
            self.player.hp = PLAYER_HP

        hits = pg.sprite.groupcollide(self.mobs, self.bullets, False, True)
        for hit in hits:
            hit.hp = 0
            hit.vel = vec(0, 0)
            self.destroy_sound.play()
            self.player.librarians_killed += 1

        current_time = pg.time.get_ticks()
        if current_time - self.start_time > 300000:
            self.spawn_rate = 200
        elif current_time - self.last_spawn_time > self.spawn_rate:
            self.spawn_mob()
            self.last_spawn_time = current_time
            self.spawn_rate = max(2000, self.spawn_rate - 50)

        if self.player.librarians_killed >= 25:
            game_state["current_level"] = "level_3"
            self.playing = False

    def draw(self):
        """Draws things on the screen."""
        self.screen.blit(BACKGROUND, (0, 0))
        for sprite in self.all_sprites:
            if isinstance(sprite, Mob):
                draw_hp(sprite)
            self.screen.blit(sprite.image, self.camera.apply(sprite))

        mouse = FONT.render("Librarians killed: " + str(self.player.librarians_killed), True, RED)
        self.screen.blit(mouse, (10, 30))

        for i in range(self.lives):
            self.screen.blit(self.heart_img, (10 + i * 40, 50))

        if self.paused:
            self.screen.blit(self.pausedScreen, (0, 0))
            p_screen = FONT2.render("PAUSED!", True, GREEN)
            self.screen.blit(p_screen, (WIDTH / 2 - 75, HEIGHT / 2 - 20))

        pg.display.flip()

    def events(self):
        """Part of the main game loop - has game events."""
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.quit()
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_ESCAPE:
                    self.quit()
                if event.key == pg.K_p:
                    self.paused = not self.paused

    def show_death_screen(self):
        """Display the death screen when the player runs out of lives."""
        fade_in(self.screen)
        font = pg.font.Font(None, 74)
        death_text = font.render("You Died", True, (255, 0, 0))
        score_text = font.render(f"Score: {self.player.librarians_killed}", True, (255, 255, 255))
        replay_text = font.render("Replay Game", True, (255, 255, 255))
        replay_rect = replay_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 100))

        while True:
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    pg.quit()
                    sys.exit()
                elif event.type == pg.MOUSEBUTTONDOWN:
                    if replay_rect.collidepoint(event.pos):
                        return

            self.screen.fill((0, 0, 0))
            self.screen.blit(
                death_text,
                (
                    WIDTH // 2 - death_text.get_width() // 2,
                    HEIGHT // 2 - death_text.get_height() - 75 // 2,
                ),
            )
            self.screen.blit(replay_text, replay_rect.topleft)
            pg.display.flip()

    def show_start_screen(self):
        """Call this at the start of the game."""
        pass

    def show_go_screen(self):
        """Call this when game is over."""
        pass

    def spawn_mob(self):
        """Function to spawn a new mob."""
        mob_type = random.choice(["M", "H", "T"])
        if mob_type == "M":
            Mob(self, random.randint(0, self.map_col), random.randint(0, self.map_row))
        elif mob_type == "H":
            Mob2(self, random.randint(0, self.map_col), random.randint(0, self.map_row))
        elif mob_type == "T":
            Mob3(self, random.randint(0, self.map_col), random.randint(0, self.map_row))


def run_level2():
    g = Game()
    g.show_start_screen()
    while True:
        g.new()
        g.run()
        if game_state["current_level"] == "level_3":
            break
        g.show_go_screen()
