from .grid import Grid
from .config import Config
from .cell import MineCell
import pygame as pg
from dataclasses import dataclass
from .enums import RevealColors


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
            return self._image_set[key]

        # Case 2: key is an integer
        if isinstance(key, int):
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
        self._dirty = pg.sprite.Group()
        self._render_image_set = RenderImageSet(config)

    def mark_dirty(self, sprite):
        self._dirty.add(sprite)

    def draw(self, surface):
        self._dirty.draw(surface)
        self._dirty.empty()   # clear queue after drawing

    def change_sprite_image(self, sprite: pg.sprite.Sprite, c: RevealColors | int):
        assert isinstance(sprite, pg.sprite.Sprite)
        assert isinstance(c, RevealColors) or isinstance(c, int)
        sprite.image = self._render_image_set[c]
        print(sprite)
        return

class Render():
    def __init__(self, grid: Grid, config: Config) -> RenderImageSet:

         
        self._parent_screen = config.parent_screen
        # self._grid = grid

        self._to_render: RenderGroup = RenderGroup(config)
        self._mines: pg.sprite.Group = pg.sprite.Group()

        # Initialize all cells as needed. 
        for r in range(0, config.num_rows):
            for c in range(0, config.num_columns):

                self._to_render.add(grid.board[r][c])
                
                # Gather all mines in one group
                if isinstance(grid.board[r][c], MineCell):
                    self._mines.add(grid.board[r][c])
                
                # Because we want all images to be shared so we aren't creating images with a million
                #   Cells or whatever. 
                self._to_render.change_sprite_image(grid.board[r][c], 0)
                grid.board[r][c].rect = grid.board[r][c].image.get_rect()
                grid.board[r][c].rect.topleft = grid.compute_cell_pos(r, c)

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