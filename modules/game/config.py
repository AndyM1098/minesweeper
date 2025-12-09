import pygame as pg
from ..settings import Settings
import random
from .enums import RevealColors


class Config():
    def __init__(self, p_screen: pg.Surface, settings: Settings):

        self.parent_screen: pg.Surface = p_screen
        
        self.cell_width: int = 0
        if settings.cell_width == None:
            self.cell_width = int(self.parent_screen.get_width() / settings.num_columns)
        else:
            self.cell_width = settings.cell_width

        self.cell_height: int = 0
        if settings.cell_height == None:
            self.cell_height = int(self.parent_screen.get_height() / settings.num_rows)
        else:
            self.cell_height = settings.cell_height
        
        #pg.display.set_caption("Minesweeper")

        self.num_rows: int = settings.num_rows
        self.num_columns: int = settings.num_columns
        self.num_cells = self.num_rows * self.num_columns

        self.off_set_x: int = 0
        self.off_set_y: int = 0

        self.num_mines = settings.num_mines

        random.seed(settings.seed)

        self.render_queue: pg.sprite.Group = pg.sprite.Group()
        self._rq_empty: bool = True

        from .enums import cell_neighbor_increments
        self.cell_neighbors = [v.value for v in list(cell_neighbor_increments)]

        return
    