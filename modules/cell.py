import pygame

from .enums import RevealColors, CellFlagged, CellRevealed

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

    def __init__(self, cell_num: int, start_pos, cell_size: int, grid_r: int, grid_c: int):
        
        super().__init__()

        self._id: int = cell_num
        self._reveal_color: RevealColors = RevealColors.NOT_SET
        self._grid_r: int = grid_r
        self._grid_c: int = grid_c
        self._number_of_neighbors:int = 0
        
        # Will be changed to a better system later
        self.state = CellState.INACTIVE
        self._cell_type = CellType.CELL

        self.image: pygame.Surface = pygame.Surface((cell_size[0], cell_size[1]))
        self.image.fill((RevealColors.NOT_REVEALED.value))
        self.rect: pygame.Rect = self.image.get_rect()

        self.rect.topleft = (start_pos[0], start_pos[1])

        self._revealed: CellRevealed = CellRevealed.NO_REVEAL
        self._flag = CellFlagged.NO_FLAG

        #print(f"Added cell: {self.id}\n\tpos: {self.rect.topleft}\n\tsize: {self.image.get_size()}\n")

        # if self.id == 2:
        #     import sys
        #     sys.exit(0)

        return
    
    # Cell.id
    @property
    def id(self) -> int:
        return self._id
    @id.setter
    def id(self, new_id: int):
        assert isinstance(new_id, int)
        self._id = new_id

    #Cell.grid_r
    @property
    def grid_r(self) -> int:
        return self._grid_r
    
    # Cell.grid_c
    @property
    def grid_c(self) -> int:
        return self._grid_c
    
    @property
    def flag(self) -> bool:
        return self._flag == CellFlagged.FLAG
    
    @flag.setter
    def flag(self, flag: bool) -> None:
        
        try:
            assert isinstance(flag, bool)
        
        except AssertionError as e:
            print("ERROR: Flag is not a bool!")

        self._flag = CellFlagged.FLAG if flag else CellFlagged.NO_FLAG

    @property
    def revealed(self) -> bool:
        print(self._revealed)
        return self._revealed.value

    @revealed.setter
    def revealed(self, r: bool):
        assert isinstance(r, bool)
        self._revealed = CellRevealed.REVEALED if r else CellRevealed.NO_REVEAL
        return

    def update_to_flagged(self):
        print("Flaggin!")
        self.flag = True
        self.image.fill(RevealColors.FLAGGED.value)

    def update_to_unflagged(self):
        print("Unflaggin")
        self.flag = False
        self.image.fill(RevealColors.NOT_REVEALED.value)

    def reveal_cell(self):
        """
            Fill cell to be of color self._reveal_color.value
        """
        if self.revealed == CellRevealed.REVEALED.value\
            or self.flag == CellFlagged.FLAG.value:
            return False

        self.revealed = CellRevealed.REVEALED.value
        print(f"Reveal color: {self._reveal_color.value}")
        self.image.fill(self._reveal_color.value)
        return True
    
    def get_cell_type(self):
        return (self._cell_type)

    def get_grid_coords(self):
        return (self.grid_i, self.grid_j)

    def _update_cell_reveal_color(self):
        self._reveal_color = Cell.REVEAL_COLOR_LOOKUP_TABLE[self.number_of_neighbors]
        return
        


class EmptyCell(Cell):
    def __init__(self, cell_num: int, start_pos, cell_size, i, j):
        super().__init__(cell_num, start_pos, cell_size, i, j)
        self._cell_type = CellType.EMPTY
        self.number_of_neighbors = 0
        return
    
    def increment_mine_count(self) -> int:
        self.number_of_neighbors += 1
        if self.number_of_neighbors > 8:
            print("Error. Neighbors can not be > 8!")
            import sys
            sys.exit(0)
        
        self._update_cell_reveal_color()
        return self.number_of_neighbors

    def reveal_cell(self):
        super().reveal_cell()
        
        return

class MineCell(Cell):
    def __init__(self, cell_num: int, start_pos, cell_size, i, j):
        super().__init__(cell_num, start_pos, cell_size, i, j)
        self._cell_type = CellType.BOMB
        self.number_of_neighbors = 9
        self._update_cell_reveal_color()
        return
    
    def reveal_cell(self):
        super().reveal_cell()