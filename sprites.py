import pygame

from pygame import K_UP, K_DOWN, K_LEFT, K_RIGHT

# duplicated constants. ew.
WIDTH = 800
HEIGHT = 600

SCREEN = pygame.Rect(0, 0, WIDTH, HEIGHT)


class Player(pygame.sprite.Sprite):
    def __init__(self, *groups):
        super().__init__(groups)
        self.surf = pygame.image.load("img/blue-plane-right.png").convert_alpha()
        self.rect = self.surf.get_rect()

    def update(self):
        p = pygame.key.get_pressed()
        self.rect.move_ip(5 * (p[K_RIGHT] - p[K_LEFT]), 5 * (p[K_DOWN] - p[K_UP]))
        self.rect.clamp_ip(SCREEN)


class Enemy(pygame.sprite.Sprite):
    surf = None

    def __init__(self, position, speed, *groups):
        super().__init__(groups)
        if not self.surf:
            Enemy.surf = pygame.image.load("img/left-missile.png").convert_alpha()
        self.rect = self.surf.get_rect()
        self.rect.midleft = position
        self.speed = speed

    def update(self):
        self.rect.move_ip(-self.speed[0], -self.speed[1])
        if self.rect.right < 0:
            self.kill()


class Health(pygame.sprite.Sprite):
    """Heart counter"""

    spacing = 10

    def __init__(self, amt=5):
        self.img = pygame.image.load("img/heart.png").convert_alpha()
        self.rect = self.img.get_rect()
        self.rect.top = 20
        self.rect.left = 20
        self.amt = amt
        self.draw()

    def draw(self):
        self.drawn_amt = self.amt
        if self.amt < 0:
            self.amt = 0
        if self.amt == 0:
            self.surf = pygame.Surface((1, 1))
            self.surf.fill((0, 0, 0))
        else:
            ht = self.img.get_height()
            wd = (self.img.get_width() + Health.spacing) * self.amt - Health.spacing
            self.surf = pygame.Surface((wd, ht))
            for i in range(self.amt):
                self.surf.blit(
                    self.img, ((self.img.get_width() + Health.spacing) * i, 0)
                )

    def update(self):
        if self.drawn_amt != self.amt:
            self.draw()


class LevelGauge(pygame.sprite.Sprite):
    """Level Counter"""

    spacing = 10

    def __init__(self, amt=0):
        self.img = pygame.image.load("img/level.png").convert_alpha()
        self.img_gray = pygame.image.load("img/not-level.png").convert_alpha()
        self.amt = amt
        self.draw()

    def draw(self):
        self.drawn_amt = self.amt
        if self.amt < 0:
            self.amt = 0

        ht = self.img.get_height()
        wd = (self.img.get_width() + self.spacing) * 10 - self.spacing
        self.surf = pygame.Surface((wd, ht))
        for i in range(10):
            img = self.img if i < self.amt else self.img_gray
            self.surf.blit(img, ((img.get_width() + self.spacing) * i, 0))

        self.rect = self.surf.get_rect()
        self.rect.midtop = (WIDTH / 2, 20)

    def update(self, diff):
        self.amt = int(diff)
        if self.drawn_amt != self.amt:
            self.draw()
