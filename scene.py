class Scene:
    def update(self): # either returns None or a Scene
        '''Update this scene's game logic. Usually returns None.

        Can return a Scene; if so, that means that'll be the Scene to switch to next.
        '''
        raise NotImplementedError

    def draw(self, screen):
        '''Render the whole scene to the screen surface.'''
        raise NotImplementedError

