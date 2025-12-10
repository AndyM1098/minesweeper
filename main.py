import pygame
from modules.event_handler.eventHandler import EventHandler
from modules.settings import Settings
from modules.game.game import Game
from typing import Tuple
import random
from modules.event_handler.eventEnums import ActionType
from modules.event_handler.eventAction import Action


class App:
    def __init__(self):
        
        # Init pygame
        pygame.init()
        pygame.display.init()
        
        # Init settings
        self.settings: Settings = Settings()
        random.seed(self.settings.seed)

        # Set display surface. --> Might make this it's own thing to manage the surface portion. 
        self._display_surf: pygame.Surface = pygame.display.set_mode((self.settings.grid_width, self.settings.grid_height), pygame.HWSURFACE | pygame.DOUBLEBUF)
        
        self.size: Tuple[int, int] = (0, 0)
        self.clock: pygame.time.Clock = pygame.time.Clock()

        self.game: Game = Game(self._display_surf)
        self.event_handler: EventHandler = EventHandler()

        self._running = True
        pygame.display.flip()

        return
    
    # Returns whether app is running or not!
    def on_init(self):
        return self._running == True

    def on_event(self, event):
        if event.type == pygame.QUIT:
            return 1
        return 0
    
    def on_loop(self, action: Action):
        self.game.apply_action(action)
        return
    
    def on_render(self):
        self.game.game_render()
        pygame.display.flip()
        self.clock.tick(self.settings.frame_rate)
        return
    
    def on_cleanup(self):
        pygame.quit()

    def on_execute(self):
        
        next_action: Action

        if self.on_init() == False:
            self._running = False

        # Render game if not already rendered!
        self.on_render()

        while( self._running ):
            next_action = self.event_handler.get_action()
            
            if next_action.action == ActionType.QUIT:
                self._running = False
                continue
            
            if next_action.action == ActionType.NONE:
                continue
            
            self.on_loop(next_action)
            self.on_render()

        self.on_cleanup()
 
if __name__ == "__main__" :
    theApp = App()
    theApp.on_execute()