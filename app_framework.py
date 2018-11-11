import pygame
import numpy as np

class App:

    def __init__(self):
        self._running = True
        self._display_surf = None
        self.size = self.width, self.height = 640, 400
        self.fps = 30
        self.playtime = 0

    def on_init(self):
        # initialize game and create window
        pygame.init()
        self._display_surf = pygame.display.set_mode(
            self.size,
            pygame.HWSURFACE | pygame.DOUBLEBUF
        )


    def on_event(self, event):
        # event handling
        if event.type == pygame.QUIT:
            self._running = False

    def on_loop(self):
        self.playtime += self.clock.tick(self.fps) / 1000
        # define game loop here

    def on_render(self):
        # use for render function calls
        self._display_surf.fill((255,255,255)) #creates white background

        #fill logic here

        pygame.display.flip()

    def on_cleanup(self):
        # Called to save and exit game
        pygame.quit()

    def on_execute(self):
        # Call this function to start game
        if self.on_init() == False:
            self._running = False
        while self._running:
            for event in pygame.event.get():
                self.on_event(event)
            self.on_loop()
            self.on_render()
        self.on_cleanup()


    ################# GAME LOGIC FUNCTIONS ################


    ################# RENDER FUNCTIONS ###################