import pygame

from .enums import RevealColors, CellFlagState, CellRevealed
from .config import Config


from enum import Enum

from typing import Tuple


class CellType(Enum):
    EMPTY = 0
    BOMB = 1
    CELL = 3

class CellState(Enum):
    ACTIVE = True
    INACTIVE = False


# Holds the cell sprite, and whether it is inactive or not
class Cell(pygame.sprite.Sprite):

    REVEAL_COLOR_LOOKUP_TABLE = list(RevealColors)

    def __init__(self, cell_num: int, start_pos, cell_size: int, grid_r: int, grid_c: int, config: Config):
        
        super().__init__()

        self.id: int = cell_num
        self._reveal_color: RevealColors = RevealColors.NOT_SET
        self.grid_r: int = grid_r
        self.grid_c: int = grid_c
        self.adjacent_mine_count: int = 0
        
        # Will be changed to a better system later
        self.state = CellState.INACTIVE
        self._cell_type = CellType.CELL

        # Change this to grab an already existing surface
        
        # self.image: pygame.Surface = pygame.Surface((cell_size[0], cell_size[1])) # Original. 
        # self.image.fill((RevealColors.NOT_REVEALED.value))

        # Render will set this!
        self.image: pygame.Surface = None

        self._rect_size = (config.cell_width, config.cell_height)
        
        # Set rectangle
        self.rect: pygame.Rect = None #self.image.get_rect()

        # self.rect.topleft = (start_pos[0], start_pos[1])

        self._revealed: CellRevealed = CellRevealed.NO_REVEAL
        self._flag = CellFlagState.NO_FLAG

        #print(f"Added cell: {self.id}\n\tpos: {self.rect.topleft}\n\tsize: {self.image.get_size()}\n")

        # if self.id == 2:
        #     import sys
        #     sys.exit(0)

        return
    
    @property
    def flag(self) -> bool:
        return self._flag == CellFlagState.FLAG
    
    @flag.setter
    def flag(self, flag: bool) -> None:
        try:
            assert isinstance(flag, bool)
        
        except AssertionError as e:
            print("ERROR: Flag is not a bool!")

        self._flag = CellFlagState.FLAG if flag else CellFlagState.NO_FLAG

    @property
    def revealed(self) -> bool:
        return self._revealed.value

    @revealed.setter
    def revealed(self, r: bool):
        assert isinstance(r, bool)
        self._revealed = CellRevealed.REVEALED if r else CellRevealed.NO_REVEAL
        return

    def flag_cell(self):
        self.flag = True
        self.image.fill(RevealColors.FLAGGED.value)

    def unflag_cell(self):
        self.flag = False
        self.image.fill(RevealColors.NOT_REVEALED.value)

    def reveal_cell(self):
        """adjacent_mine_count
            Fill cell to be of color self._reveal_color.value
        """
        # if self.revealed == CellRevealed.REVEALED.value\
        #     or self.flag == CellFlagState.FLAG.value:
        #     return False

        self.revealed = True
        self.image.fill(self._reveal_color.value)
        return True
    
    def get_cell_type(self):
        return self._cell_type

    def get_grid_coords(self):
        return (self.grid_r, self.grid_c)

    def _update_cell_reveal_color(self):
        self._reveal_color = Cell.REVEAL_COLOR_LOOKUP_TABLE[self.adjacent_mine_count]
        return
        

class EmptyCell(Cell):
    def __init__(self, cell_num: int, start_pos, cell_size, i, j, config):
        super().__init__(cell_num, start_pos, cell_size, i, j, config)
        self._cell_type = CellType.EMPTY
        return
    
    def increment_adjacent_mine_count(self) -> int:
        self.adjacent_mine_count += 1
        if self.adjacent_mine_count > 8:
            print("Error. Neighbors can not be > 8!")
            exit(0)
        
        self._update_cell_reveal_color()
        return self.adjacent_mine_count

    def reveal_cell(self):
        super().reveal_cell()

class MineCell(Cell):
    def __init__(self, cell_num: int, start_pos, cell_size, i, j, config):
        super().__init__(cell_num, start_pos, cell_size, i, j, config)
        self._cell_type = CellType.BOMB
        self.adjacent_mine_count = 9
        return
    
    def increment_adjacent_mine_count(self) -> int:
        # Don't do anything for Mines. 
        return self.adjacent_mine_count

    def reveal_cell(self):
        super().reveal_cell()