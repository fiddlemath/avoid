# Following along with the tutorial at https://realpython.com/pygame-a-primer/

import pygame

from sprites import (Player, Enemy, Health, Level)
from random import randint, choice
from enum import (Enum, auto)

pygame.init()

class GameState(Enum):
    TITLE = auto()
    STARTING = auto()
    PLAYING = auto()
    VICTORY = auto()
    QUITTING = auto()

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

# Game state, all of which is global here
# In a bigger game, the game-state storage thing would be a whole subsystem
screen = pygame.display.set_mode(
    size=(SCREEN_WIDTH, SCREEN_HEIGHT), flags=pygame.SCALED
)

player = Player()
health = Health()
level = Level()
game_state = GameState.TITLE
start_diff = 0.0

enemies = pygame.sprite.Group()
all_sprites = pygame.sprite.Group()

def main():
    global screen
    pygame.display.set_caption("Avoid")
    pygame.mouse.set_visible(False)

    clock = pygame.time.Clock()

    # Whole game loop
    while True:
        match game_state:
            case GameState.TITLE:
                do_title()
            case GameState.STARTING:
                do_starting()
            case GameState.PLAYING:
                do_playing()
            case GameState.VICTORY:
                do_victory()
            case GameState.QUITTING:
                pygame.quit()
                break
        clock.tick(60)

event_handlers = {}

def start_life():
    global start_time
    # just in case the player's still around somewhere
    player.add(all_sprites)
    player.rect.center = (100, SCREEN_HEIGHT / 2)

    #clear any nearby missiles on starting
    burst = pygame.sprite.Sprite()
    burst.rect = pygame.Rect((0, 0), (200, 100))
    burst.rect.midleft = player.rect.midleft
    start_time = pygame.time.get_ticks()

    pygame.sprite.spritecollide(burst, enemies, True)

start_life.EVENT = pygame.event.custom_type()
event_handlers[start_life.EVENT] = start_life


def add_enemy():
    global player
    global salvo_parity
    d = difficulty()

    if d < 3.75:
        for _ in range(int(d)+1):
            enemy = Enemy(all_sprites, enemies)
            enemy.rect.left = SCREEN_WIDTH + randint(20, 100)
            enemy.rect.top = randint(0, SCREEN_HEIGHT-enemy.rect.height)
            enemy.speed = (randint(3 + int(d), 8 + int(d)), randint(-int(d), int(d)))
            pygame.time.set_timer(add_enemy.EVENT, int(250), 0)
    elif d < 4:
        # a pause
        pygame.time.set_timer(add_enemy.EVENT, 200, 0)
    elif d < 5.75:
        t = d - 4 #ranges from 0 to 1.5
        extra = randint(-7,7)
        for i in range(8):
            enemy = Enemy(all_sprites, enemies)
            enemy.rect.midleft = (SCREEN_WIDTH, (i*2 + add_enemy.salvo_parity) * SCREEN_HEIGHT / 15 + extra)
            enemy.speed = (6, 0)
        add_enemy.salvo_parity = (add_enemy.salvo_parity + 1) % 2
        pygame.time.set_timer(add_enemy.EVENT, int(400 - (t * 90)), 0)
    elif d < 6:
        # pause
        pygame.time.set_timer(add_enemy.EVENT, 200, 0)
    else:
        # salvos aimed at the player
        num = 0
        if d <= 7: num = randint(4, 7)
        elif 7 < d < 9: num = randint(3, 5)
        else: num = 2

        center = (SCREEN_WIDTH + 10, randint(0, SCREEN_HEIGHT))
        speed_x = randint(5, int(d))

        # speed_y should make it so that, if the player doesn't move,
        # the center of these missile's path will go straight through
        # the player's center.

        # That is: (center.y - player.y) / (center.x - player.x) == speed_y / speed_x
        # player's center will never be right of screen, so div-by-zero should never happen
        speed_y = int(speed_x * (center[1] - player.rect.centery) / (center[0] - player.rect.centerx) )
        while abs(speed_y) > 4:
            speed_x /= 2
            speed_y /= 2

        match randint(0,5):
            case 0:
                speed_y += 1
            case 1:
                speed_y -= 1


        spread = choice([20, 20, 40, 40, 80, 160, 240])
        for i in range(num):
            enemy = Enemy(all_sprites, enemies)
            enemy.rect.midleft = (center[0], center[1] + (num/2 - i) * spread)
            enemy.speed = (speed_x, speed_y)

        if d > 8:
#            for _ in range(2):
                enemy = Enemy(all_sprites, enemies)
                enemy.rect.midleft = (center[0], randint(0, SCREEN_HEIGHT))
                enemy.speed = (randint(4, 10), randint(-3, 3))

        if d > 9:
            for i in range(3):
                enemy = Enemy(all_sprites, enemies)
                enemy.rect.midleft = (SCREEN_WIDTH, (i*2 + add_enemy.salvo_parity) * SCREEN_HEIGHT / 5)
                enemy.speed = (4, 0)
            add_enemy.salvo_parity = (add_enemy.salvo_parity + 1) % 2

        pygame.time.set_timer(add_enemy.EVENT, 200, 0)

add_enemy.salvo_parity = 0

add_enemy.EVENT = pygame.event.custom_type()
event_handlers[add_enemy.EVENT] = add_enemy

def end_game():
    global game_state
    enemies.empty()
    all_sprites.empty()
    game_state = GameState.TITLE
end_game.EVENT = pygame.event.custom_type()
event_handlers[end_game.EVENT] = end_game


gray = pygame.Color(150, 150, 150)
big_font = pygame.font.Font(None, size=64)
small_font = pygame.font.Font(None, size=16)
title = big_font.render("Avoid", True, gray, (0, 0, 0))
title_pos = title.get_rect(centerx = SCREEN_WIDTH/2, bottom=SCREEN_HEIGHT/2)
byline = small_font.render("by m.t.elder", True, gray, (0, 0, 0))
byline_pos = title.get_rect(x = SCREEN_WIDTH/2, bottom = SCREEN_HEIGHT*3/4)

def do_title():
    global game_state
    global title, title_pos, byline, byline_pos
    # event handling
    for event in pygame.event.get():
        match event.type:
            case pygame.KEYDOWN if event.key == pygame.K_ESCAPE:
                game_state = GameState.QUITTING
            case pygame.KEYDOWN:
                game_state = GameState.STARTING
            case pygame.QUIT:
                game_state = GameState.QUITTING
            case start_life.EVENT:
                start_life()

    screen.fill((0,0,0))
    screen.blit(title, title_pos)
    screen.blit(byline, byline_pos)
    pygame.display.flip()


def difficulty():
    """A mostly-increasing difficulty counter, as a measure of current game time.

    Starts at 0.0.
    Increases by 1 every 10 seconds.
    Decreases by 1 each time the player dies.
    """
    global start_time
    global start_diff
    global health
    global player

    if not player.alive(): return start_diff

    curr_time = pygame.time.get_ticks()
    return (curr_time - start_time)/10_000 + start_diff

def do_starting():
    """This state won't be the loop itself; it'll just set up a new
    game and then transfer to do_playing()"""
    global game_state
    global start_time
    global start_diff

    health.amt = 5

    pygame.time.set_timer(add_enemy.EVENT, 200, 0) # until it stops
    pygame.time.set_timer(start_life.EVENT, 1000, 1) # once

    start_time = pygame.time.get_ticks()
    start_diff = 0.0

    game_state = GameState.PLAYING

    do_playing()

blue = pygame.Color(95, 205, 228)
victory = big_font.render("Victory!", True, blue)

def do_playing():
    global game_state
    global player
    global level
    global start_diff

    # event handling, much duplication of event handlers, shrug
    for event in pygame.event.get():
        match event.type:
            case pygame.KEYDOWN if event.key == pygame.K_ESCAPE:
                game_state = GameState.QUITTING
            case pygame.QUIT:
                game_state = GameState.QUITTING
            case event_type if event_type > pygame.USEREVENT:
                event_handlers[event_type]()

    #### Update World!
    # Move sprites
    pressed_keys = pygame.key.get_pressed()
    player.update(pressed_keys)
    enemies.update()

    # Handle collisions
    diff = difficulty()
    if player.alive():
        coll = pygame.sprite.spritecollideany(player, enemies)
        if coll:
            player.kill()
            coll.kill()
            start_diff = int(diff)

            health.amt -= 1
            if health.amt > 0:
                pygame.time.set_timer(start_life.EVENT, 2000, 1)
                pygame.time.set_timer(add_enemy.EVENT, 1500, 0)
            else:
                pygame.time.set_timer(end_game.EVENT, 3000, 1)

    health.update()
    level.update(diff)

    if difficulty() > 10.0:
        pygame.time.set_timer(add_enemy.EVENT, 0)

    # Render
    screen.fill((0, 0, 0))
    if difficulty() > 10.3:
        screen.blit(victory, title_pos)

    screen.blit(health.surf, health.rect)
    screen.blit(level.surf, level.rect)
    for s in all_sprites:
        screen.blit(s.surf, s.rect)

    pygame.display.flip()

if __name__ == "__main__":
    main()
