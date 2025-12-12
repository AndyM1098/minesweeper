from .grid import Grid
from .config import Config
from .cell import MineCell, EmptyCell, Cell
import pygame as pg
from dataclasses import dataclass
from .enums import RevealColors

from typing import Union, List, Tuple

class RenderImageSet():

    def __init__(self, config: Config):

        self._image_width = config.cell_width
        self._image_height = config.cell_height
        self._image_size = (self._image_width, self._image_height)

        self._image_set = {key: pg.surface.Surface(self._image_size) for key in RevealColors}
        self._int_mapping: list[RevealColors] = [key for key in RevealColors]
        
        for image in RevealColors:
            self._image_set[image].fill(image.value)

    def __getitem__(self, key):
        # Case 1: key is a RevealColors enum
        if isinstance(key, RevealColors):
            print("RenderImageSet[RevealColors]")
            return self._image_set[key]

        # Case 2: key is an integer
        if isinstance(key, int):
            print("RenderImageSet[int]")
            if not (0 <= key < len(self._image_set)):
                raise IndexError("RenderImageSet index out of range")

            # Convert dict values to a list (order is enum definition order)
            return list(self._image_set.values())[key]

        raise TypeError(
            f"RenderImageSet indices must be RevealColors or int, not {type(key)}"
        )

class RenderGroup(pg.sprite.Group):
    def __init__(self, config: Config):
        super().__init__()
        self._sprite_reveal_change_queue: List[Tuple[Union[MineCell, EmptyCell], RevealColors]] = []
        self._image_set = RenderImageSet(config)
        
        # Will hold a list of cell sprites that we want to change the image for
        #   Since it will be a reveal cell!
        return
    
    def mark_dirty(self, cell: Union[MineCell, EmptyCell]):
        self.add(cell)

    def queue_sprite_reveal(self, cell_sprite: Union[MineCell, EmptyCell]):
        # Logic will add sprites that need to be changed to this queue.
        #   On render, the render class will update the color.
        assert isinstance(cell_sprite, Cell) # type: ignore
        cell_sprite.image = self._image_set[cell_sprite.reveal_color]
        self.mark_dirty(cell_sprite)
        return
        
    
class Render():
    def __init__(self, grid: Grid, config: Config):\
    
        self._parent_screen = config.parent_screen
        self._to_render: RenderGroup = RenderGroup(config)
        self._mines: pg.sprite.Group = pg.sprite.Group()
    

        # Initialize all cells as needed.
        for r in range(0, config.num_rows):
            for c in range(0, config.num_columns):
                
                curr_cell: Union[MineCell, EmptyCell] = grid.board[r][c]
                
                curr_cell.image = self._to_render._image_set[curr_cell.reveal_color]
                curr_cell.rect = curr_cell.image.get_rect()
                curr_cell.rect.topleft = grid.compute_cell_pos(r, c)

                self._to_render.add(grid.board[r][c])
                
                # Gather all mines in one group
                if isinstance(grid.board[r][c], MineCell):
                    self._mines.add(grid.board[r][c])
                

        return
    
    def get_render_group(self):
        return self._to_render

    def add_sprite_to_render_queue(self, c: pg.surface.Surface):
        assert isinstance(c, pg.surface.Surface)
        self._to_render.add(c)
        return True

    def render_all_mines(self):
        self._mines.draw(self._parent_screen)
        return

    def update_mines(self, grid: Grid):
        pass

    def render(self):
        self._to_render.draw(self._parent_screen)
        return

    # def draw_render_group(self, group: RenderGroup = None):
    #     """
    #         If None is used, it will use the internal state
    #     """
    #     if group is None:
    #         exit(0)
    #         group = self._to_render
        
    #     group.draw(self._parent_screen)
    #     return