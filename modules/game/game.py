from modules.settings import Settings
from modules.event_handler.eventAction import Action, ActionType
import pygame.surface

from .render import Render as Game_Render
from .logic import Logic as Game_Logic
from .grid import Grid as Game_Grid
from modules.settings import Settings as Game_Settings
from .config import Config as Game_Config


class Game():

    Settings = Game_Settings
    Grid = Game_Grid
    Render = Game_Render
    Logic = Game_Logic
    Config = Game_Config

    def __init__(self, parent_screen: pygame.Surface):
        
        """
            Will contain ALL the game information / modules including logic and rendering modules
        """

        # Grab the current settings. Update this to 
        self._settings: Settings = self.Settings()
        self._config: Game_Config = self.Config(parent_screen, self._settings)
        self._grid: Game_Grid = self.Grid(self._config)
        self._renderer: Game_Render = self.Render(self._grid, self._config)
        self._render_group = self._renderer.get_render_group()
        self._logic: Game_Logic = self.Logic(self._grid, self._config, self._render_group)
        
        self._render_group.draw(parent_screen)


        return

    def game_render(self):
        self._renderer.render()

    def apply_action(self, a: Action):
        self._logic.update_board(a)
