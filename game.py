import pygame
from typing import Callable, Dict, Tuple

from scene import Scene

from pygame import KEYDOWN, KEYUP, JOYBUTTONDOWN, JOYBUTTONUP, QUIT
from pygame.event import Event

# EventPat: an event pattern
EventPat = int | Tuple[int, int]


def pat(e: pygame.event.Event) -> EventPat:
    """Turn this event into an EventPats needed for matching event handlers."""
    if e.type in (KEYDOWN, KEYUP):
        return (e.type, e.key)
    elif e.type in (JOYBUTTONUP, JOYBUTTONDOWN):
        return (e.type, e.button)
    return e.type


# Fonts
pygame.init()
BIG_FONT = pygame.font.Font(None, size=64)
WEE_FONT = pygame.font.Font(None, size=16)
WIDTH = 800
HEIGHT = 600


class Game:
    # Member annotations
    event_handlers: Dict[EventPat, Callable[[Event], None]]
    screen: pygame.Surface
    scene: Scene
    clock: pygame.time.Clock

    _running: bool

    def __init__(self, first_scene: Scene):
        pygame.init()
        self.clock = pygame.time.Clock()

        self.screen = pygame.display.set_mode(size=(WIDTH, HEIGHT), flags=pygame.SCALED)

        self._running = True

        self.event_handlers = {
            QUIT: self.quit,
            (KEYDOWN, pygame.K_ESCAPE): self.quit,
        }
        self.scene = first_scene

    def run(self):
        """Do the game loop. Be the game loop."""

        while self._running:
            self.handle_events()
            next_scene = self.scene.update()

            self.scene.draw(self.screen)
            pygame.display.flip()
            if next_scene:
                self.scene = next_scene

            self.clock.tick(60)

    def quit(self):
        """Stop looping that game loop"""
        self._running = False

    def handle_events(self):
        for event in pygame.event.get():
            pattern = pat(event)
            if pattern in self.event_handlers:
                self.event_handlers[pattern](event)
            elif type(pattern) == tuple and pattern[0] in self.event_handlers:
                self.event_handlers[pattern[0]](event)

    def switch_scene(self, scene: Scene):
        """Enter the given scene, and exit the previous scene"""
        self.scene = scene

    def exit(self, scene: Scene):
        """Exit the given scene"""
        # drop event handlers from scene
