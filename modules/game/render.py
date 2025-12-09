from .grid import Grid
from .config import Config
from .cell import MineCell
import pygame as pg

class Render():
    def __init__(self, grid: Grid, config: Config):

        self._parent_screen = config.parent_screen
        self._grid = Grid

        self._to_render: pg.sprite.Group = pg.sprite.Group()
        self._mines: pg.sprite.Group = pg.sprite.Group()

        for r in range(0, config.num_rows):
            for c in range(0, config.num_columns):
                self._to_render.add(grid.board[r][c])
                if isinstance(grid.board[r][c], MineCell):
                    self._mines.add(grid.board[r][c])



        return
    
    def add_sprite_to_render_queue(self, c: pg.surface.Surface):
        self._to_render.add(c)
        return True

    def render_all_mines(self):
        self._mines.draw(self._parent_screen)
        return


    def render(self):
        self._to_render.draw(self._parent_screen)
        self._to_render.empty()
        return

