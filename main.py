import pygame
from modules.grid import Grid
from modules.settings import Settings
from modules.eventHandler import EventHandler, Action
from modules.eventHandler import State
from modules.game import Game
from typing import Tuple
import random

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

        self.game: Game = Game()
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
        # coords, action = self.event_handler.process_event(event)
        return coords, action
    
    def on_loop(self, coords, action: bool):

        if(action == ActionType.REVEAL):
            sprite_num = self.grid.get_cell_from_coords(coords)
            self.grid.update_logic(sprite_num, action)
        elif action == ActionType.DRAG:
            # TODO
            pass
        elif action == ActionType.FLAG:
            sprite_num = self.grid.get_cell_from_coords(coords)
            self.grid.update_logic(sprite_num, action)
        return
    
    def on_render(self):
        # self.game.update_render()
        pygame.display.flip()
        self.clock.tick(self.settings.frame_rate)
        return
    
    def on_cleanup(self):
        pygame.quit()

    def on_execute(self):
        
        a_e: EventHandler.ActionType = None # type: ignore
        
        if self.on_init() == False:
            self._running = False

        while( self._running ):
            a_e = self.event_handler.get_action()
            if a_e.action == ActionType.QUIT:
                self._running = False
                continue
            
            # print(a_e, "\n\n\n")

            # self.game.apply_action(a_e)
            # self.game.update_render()

            # for event in pygame.event.get():
            #     action = self.on_event(event)

            #     if action == 1:
            #         self._running = False
            #         continue
            
            # if action is not ActionType.NONE:
            #     self.on_loop(coords, action)
            self.on_render()

        self.on_cleanup()
 
if __name__ == "__main__" :
    theApp = App()
    theApp.on_execute()