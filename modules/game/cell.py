import pygame

from .enums import RevealColors
from enum import Enum

from typing import Tuple


# Holds the cell sprite, and whether it is inactive or not
class Cell(pygame.sprite.Sprite):

    def __init__(self, cell_num: int):
        
        super().__init__()

        self.id: int = cell_num
        self.reveal_color: RevealColors = RevealColors.NOT_SET
        self.adjacent_mine_count: int = 0
        
        self.revealed: bool = False
        self.flagged: bool = False

        # Renderer will set the following fields
        self.image: pygame.Surface = None

        # Set rectangle
        self.rect: pygame.Rect = None
        self.rect.topleft = (0, 0)

        return

    def reveal_cell(self):
        """ adjacent_mine_count
            Fill cell to be of color self.reveal_color.value
        """
        # if self.revealed == CellRevealed.REVEALED.value\
        #     or self.flagged == CellFlagState.FLAG.value:
        #     return False

        self.revealed = True

    def get_display_coords(self):
        return (self.rect.topleft[0], self.rect.topleft[1])

class EmptyCell(Cell):

    def __init__(self, cell_num: int):
        super().__init__(cell_num)
        return
    
    def increment_adjacent_mine_count(self) -> int:
        self.adjacent_mine_count += 1
        assert self.adjacent_mine_count <= 8
        return self.adjacent_mine_count

    def reveal_cell(self):
        super().reveal_cell()

class MineCell(Cell):
    def __init__(self, cell_num: int):
        super().__init__(cell_num)
        self.reveal_color = RevealColors.MINE
        self.adjacent_mine_count = 9
        return
    
    def increment_adjacent_mine_count(self) -> int:
        # Don't do anything for Mines.
        assert self.adjacent_mine_count == 9
        return self.adjacent_mine_count

    def reveal_cell(self):
        super().reveal_cell()