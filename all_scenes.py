import pygame
from scene import Scene
from pygame.sprite import Sprite, Group
from game import BIG_FONT, WEE_FONT, WIDTH, HEIGHT
from sprites import Player, Enemy, Health, LevelGauge
from random import randint, choice
from pygame.key import K_RETURN


class Title(Scene):
    title: Sprite
    byline: Sprite

    def __init__(self):
        gray = pygame.Color(150, 150, 150)
        self.title = Sprite()
        self.title.surf = BIG_FONT.render("Avoid", True, gray, (0, 0, 0))
        self.title.rect = self.title.surf.get_rect(centerx=WIDTH / 2, bottom=HEIGHT / 2)

        self.byline = Sprite()
        self.byline.surf = WEE_FONT.render("by m.t.elder", True, gray, (0, 0, 0))
        self.byline.rect = self.byline.surf.get_rect(x=WIDTH / 2, bottom=HEIGHT * 3 / 4)

    def update(self):
        if pygame.key.get_pressed()[K_RETURN]:
            return Play()
        else:
            return None

    def draw(self, screen):
        screen.fill((0, 0, 0))
        screen.blit(self.title.surf, self.title.rect)
        screen.blit(self.byline.surf, self.byline.rect)


class Play(Scene):
    SPAWN_PLAYER_DELAY = 1000  # ms
    LEVEL_DURATION = 10_000  # ms
    MAX_LEVEL = 11  # levels, an int

    victory: Sprite
    health: Health
    player: Player
    level_gauge: LevelGauge

    enemies: Group
    hud: Group
    all_sprites: Group

    level_start_time: float
    level: int

    spawn_player_time: float
    spawn_enemy_time: float

    salvo_parity: int

    def __init__(self):
        self.victory = Sprite()
        self.victory.surf = BIG_FONT.render("Victory!", True, (95, 205, 228))
        self.victory.rect = self.victory.surf.get_rect(
            centerx=WIDTH / 2, centery=HEIGHT / 2
        )

        self.health = Health(5)
        self.level_gauge = LevelGauge(0)

        self.level = 0
        self.level_start_time = None  # unset until player is spawned
        self.spawn_player_time = pygame.time.get_ticks() + Play.SPAWN_PLAYER_DELAY
        self.spawn_enemy_time = None  # set by first update.
        self.end_game_time = None
        self.salvo_parity = 0

    def update(self):
        # write here, based on do_playing()
        t = pygame.time.get_ticks()

        # End game?
        if self.end_game_time and t >= self.end_game_time:
            return Title()

        # Advance level?
        if (
            self.player.alive()
            and t >= self.level_start_time + Play.LEVEL_DURATION
            and self.level < Play.MAX_LEVEL
        ):
            self.level += 1

        # Start new life?
        if self.spawn_player_time and t >= self.spawn_player_time:
            self.level_start_time = t

            self.player.add(self.all_sprites)
            self.player.rect.center = (100, HEIGHT / 2)

            # clear nearby missles
            burst = pygame.sprite.Sprite()
            burst.rect = pygame.Rect((0, 0), (200, 100))
            burst.rect.midleft = self.player.rect.midleft
            pygame.sprite.spritecollide(burst, self.enemies, True)

        # Create enemies
        if self.player.alive() and t >= self.spawn_enemy_time:
            self.create_enemies()

        self.player.update()
        self.enemies.update()

        # Handle collisions
        if self.player.alive():
            coll = pygame.sprite.spritecollideany(self.player, self.enemies)
            if coll:
                self.player.kill()
                coll.kill()

                self.health.amt -= 1
                if self.health.amt > 0:
                    self.spawn_player_time = t + Play.SPAWN_PLAYER_DELAY
                else:
                    self.end_game_time = t + 3000  # Game-over delay

        self.health.update()
        self.level_gauge.update(self.level)

    def draw(self, screen):
        t = pygame.time.get_ticks()
        screen.fill((0, 0, 0))
        if self.level >= 10 and t >= self.level_start_time + 3000:
            screen.blit(self.victory.surf, self.victory.rect)
        screen.blit(self.health.surf, self.health.rect)
        screen.blit(self.level_gauge.surf, self.level_gauge.rect)
        for s in self.all_sprites:
            screen.blit(s.surf, s.rect)

    def next_enemy_in(self, delay):
        self.spawn_enemy_time = pygame.time.get_ticks() + delay

    def create_enemies(self):
        # percentage of the way through the current level
        t = pygame.time.get_ticks()
        dist = (t - self.level_start_time) * 100.0 / Play.LEVEL_DURATION
        level = self.level
        BREAK_DIST = 25

        # The first four levels do just simple generation
        if level < 4:
            for _ in range(self.level + 1):
                pos = (WIDTH + randint(20, 100), randint(0, HEIGHT))
                speed = (randint(3 + level, 8 + level), randint(-level, level))
                Enemy(pos, speed, self.all_sprites, self.enemies)

            if level == 3 and dist >= 100 - BREAK_DIST:
                self.next_enemy_in(Play.LEVEL_DURATION * BREAK_DIST / 100) # the transition time break
            else:
                self.next_enemy_in(250)
        
        elif 4 <= level < 6:  # level == 4, 5
            # jitter the columns a little bit, to eliminate safe rows
            extra = randint(-7, 7)
            for i in range(8):
                pos = (WIDTH, (i*2 + self.salvo_parity) * HEIGHT / 15 + extra)
                speed = (6, 0)
                Enemy(pos, speed, self.all_sprites, self.enemies)
            

            if level == 5 and dist >= 100 - BREAK_DIST:
                self.next_enemy_in(Play.LEVEL_DURATION * BREAK_DIST / 100)
            else:
                adjust_speed = (dist + (level - 4) * 100) / 175 # range: 0.0 (start) to 1.0 (end)
                self.next_enemy_in(400 - 150 * adjust_speed) # start at 400, end at 250

        elif level < 10:
            # fire salvos at the player
            num = 0
            if level <= 7:
                num = randint(4, 7)
            elif level == 8:
                num = randint(3, 5)
            else:
                num = 2
            
            center = (WIDTH + 10, randint(0, HEIGHT))
            speed_x = randint(5, level)

            # aim at the player's current position
            speed_y = int(
                speed_x
                * (center[1] - self.player.rect.centery)
                / (center[0] - self.player.rect.centerx)
            )
            # ... but not too fast
            while abs(speed_y) > 4:
                speed_x /= 2
                speed_y /= 2

            # ... and with some imprecision
            speed_y += choice([1,0,0,0,-1])
            spread = choice([20, 20, 40, 40, 80, 160, 240])

            for i in range(num):
                pos = (center[0], center[1] + (num / 2 - i) * spread)
                Enemy(pos, (speed_x, speed_y), self.all_sprites, self.enemies)
            
            # After level 8, also shoot random missiles like levels 0-3
            if level > 8:
                pos = (WIDTH + 10, randint(0, HEIGHT))
                speed = (randint(4, 10), randint(-3, 3))
                Enemy(pos, speed, self.all_sprites, self.enemies)
            
            # After level 9, also fire a loose missile grid
            if level > 9:
                for i in range(3):
                    pos = (WIDTH, (i*2 + self.salvo_parity) * HEIGHT / 5)
                    Enemy(pos, (4, 0), self.all_sprites, self.enemies)
            
            self.next_enemy_in(200)