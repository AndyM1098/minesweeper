from .settings import Settings
from .grid import Grid
from pygame import event

class Logic():
    def __init__(self):
        pass

class Render():
    def __init__(self):
        pass

class Game():
    def __init__(self):
        
        """
            Will contain ALL the game information / modules inclduing logic and rendering modules
        """
        self._settings = Settings()
        self._grid = Grid(self._settings)
        self._renderer = Render(self._grid)
        self._logic = Logic(self._grid)
        
        return
    
    def post_action(self, a: Action):
        if a == Action.REVEAL:
            
        # Take
        pass

# class App():

#     Game()
#     EventHandler()
