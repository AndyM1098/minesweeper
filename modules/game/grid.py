from .cell import Cell, CellType, CellState, MineCell, EmptyCell
from typing import Tuple, List, Union
import pygame
import random
import sys

from ..settings import Settings
from .enums import RevealColors
from .enums import CellFlagState, CellRevealed
from .config import Config
from modules.event_handler.eventAction import Action

from enums import Enum


class cell_neighbor_increments(Enum):
    UPPER_LEFT      = (-1, -1)
    UPPER_MIDDLE    = (-1, 0)
    UPPER_RIGHT     = (-1, 1)
    MIDDLE_LEFT     = (0, -1)
    MIDDLE_RIGHT    = (0, 1)
    LOWER_LEFT      = (1, -1)
    LOWER_MIDDLE    = (1, 0)
    LOWER_RIGHT     = (1, 1)
    """
    Table the above enum is based on!
    row\col -1          0           1
      -1    (-1, -1)    (-1, 0)     (-1, 1)
      0     (0,  -1)    (0,  0)     (0,  1)
      1     (1, -1)     (1,  0)     (1,  1)
    
    """


class GridMetaData:
    def __init__(self, config: Config):
    
        self.num_mines: int = config.num_mines
        self.num_rows: int = config.num_rows
        self.num_columns: int = config.num_columns
        self.num_cells: int = self.num_rows * self.num_columns

        self.num_flags:int  = 0
        # self.cell_group: pygame.sprite.Group = pygame.sprite.Group()

        # Contains the ids of the cells that contain mines
        self.mine_ids: List[int] = []
        self.generate_mine_ids()

        self.cell_neighbors = [v.value for v in list(cell_neighbor_increments)]
        
        return

    def _id_to_grid_coords(self, cell_id: int)-> Tuple[int, int]:
        r = cell_id // self.num_columns
        c = cell_id % self.num_columns
        return (r, c)

    def generate_mine_ids(self):
        self.mine_ids = [id for id in random.sample(range(0, self.num_cells), self.num_mines)]
        return

class Grid:
    """
        Class that holds the grid information.

        The grid is comprised of a 2d array of cells.

    """

    def __init__(self, config: Config):
        
        self._config: Config = config
        # Contains the grid metadata
        self.metadata: GridMetaData = GridMetaData(config)

        # Cell groups
        self.mine_group: pygame.sprite.Group[MineCell] = pygame.sprite.Group()

        # 2d matrix of Cells representing each cell!
        self.board: List[List[Union[MineCell, EmptyCell]]] = self._init_board(config)
        self._grid_init = True

        return

    # Utilities
    def get_board_rcs_cell_id(self, cell_num: int)->Tuple[int, int]:
        r = cell_num // self.metadata.num_columns
        c = cell_num % self.metadata.num_columns
        return r, c



    """
        Below are functions used in __init__()
    """
    def _init_board(self, config: Config) -> List[List[Union[MineCell, EmptyCell]]]:
        
        ret_grid = [
                        [
                            None for _ in range(0, self._config.num_columns)
                        ]
                            for _ in range(0, self._config.num_rows)
                    ]
        
        self._init_mines(ret_grid)
        self._init_empty(ret_grid)

        return ret_grid
    
    def _init_mines(self, g: List[List[Cell]]):
        for id in self.metadata.mine_ids:
            r, c = self.id_to_grid_coords(id)
            g[r][c] = MineCell(id)
            self.mine_group.add(g[r][c])
          
    def _init_empty(self, g: List[List[Cell]]):
        for r in range(0, self._config.num_rows):
            for c in range(0, self._config.num_columns):
                if g[r][c] == None:
                    g[r][c]= EmptyCell(r * self._config.num_columns + c)

    def _determine_neighbor_cells(self):
        """
            Function goes through all mines

            For each mine, update all surronding cells
                If a surronding cell is a Mine, ignore it!
        """

        n = self.metadata.num_rows
        m = self.metadata.num_columns

        for mine in self.mine_group:
            r, c = self.id_to_grid_coords(mine)

            for dr, dc in self.metadata.cell_neighbors:
                nr = r + dr
                nc = c + dc

                if 0 <= nr < n and 0 <= nc < m and isinstance(self.board[nr][nc], EmptyCell):
                    self.board[nr][nc].increment_mine_count()
    
    
    
    def _reveal_cells(self):
        for r in range(0, self.metadata.num_rows):
            for c in range(0, self.metadata.num_columns):
                self.board[r][c].reveal_cell()
        return
    
    def id_to_grid_coords(self, cell_id: int)-> Tuple[int, int]:
        r = cell_id // self._config.num_columns
        c = cell_id % self._config.num_columns
        return r, c


    def compute_offset(self)-> Tuple[int, int]:
        
        # Simple offset. Determined by current settings of grid
        # For right now. We will make all cells start at 0,0
        return (0, 0)

    def compute_cell_pos(self, r: int, c: int)-> Tuple[int, int]:
        off_set = self.compute_offset()
        # x, y --> X pixeles left, y pixels down
        cell_pos = (off_set[0] + (c * self.cell_size[0]), off_set[1] + (r * self.cell_size[1]))
        print(cell_pos)
        return cell_pos

    def _update_logic_empty_cells(self, r:int, c: int):
        # We essentially recurse. 
        # Every time we recurse, we attempt to check cells that are empty

        _visited = [[False for _ in range(0, self.metadata.num_columns)] for _ in range(0, self.metadata.num_columns)]

        self._update_logic_empty_cells_rec(_visited, r, c)

    def _update_logic_empty_cells_rec(self, v: List[List[bool]], r: int, c: int):
        
        # Do no want to add already proccessed nodes!
        
        stack: List[Tuple[int, int]] = []
        _visited = [[False for _ in range(0, self.metadata.num_columns)] for _ in range(0, self.metadata.num_columns)]
        
        stack.append((r, c))
        
        while(len(stack)):
            # Get current cell
            r, c = stack.pop()
            
            if r < 0 or r >= self.metadata.num_rows or c < 0 or c >= self.metadata.num_columns:
                continue
            elif v[r][c] == True:
                continue

            v[r][c] = True

            if self.board[r][c].number_of_neighbors > 0:
                self.board[r][c].reveal_cell()
                self.render_queue.add(self.board[r][c])
                self._rq_empty = False
                continue
            else:
                for dir in self.metadata.cell_neighbors:
                    stack.append((r + dir[0], c + dir[1]))
                
            self.board[r][c].reveal_cell()
            self.render_queue.add(self.board[r][c])
            self._rq_empty = False
        
        return

    def _logic_flag(self, cell_id: int):
        
        res = False
        cell: Cell = self.get_cell_from_id(cell_id)
        print(cell.revealed)
        if cell.revealed is not True:
            print("TTTTTTTTTTTt")
            if cell.flag:
                cell.update_to_unflagged()
            else:
                print("Updating to flagged")
                cell.update_to_flagged()

            res = True
            self.render_queue.add(cell)
            self._rq_empty = False

        return res

    def get_cell_from_id(self, cell_id: int):
        r, c = self.id_to_grid_coords(cell_id)
        return self.board[r][c]

    @property
    def cell_size(self)-> Tuple[int, int]:
        return self._config.cell_width, self._config.cell_height

    def get_cell_from_coords(self, coords: Tuple[int, int]):
        assert(coords != (-1, -1))
        cell_num = self._get_cell_from_coords(coords)
        return cell_num
    
    def _get_cell_from_coords(self, coords: Tuple[int, int])-> int:

        """"
            We want to get the cell number that the user clicked on based on the pixel coords

            If every cell is n pixels, we can divide the x coordinate to determine where
                on the x axis we are
                

        """

        x_coord = coords[0]
        y_coord = coords[1]

        x_cell = x_coord // self.metadata.cell_size[0]
        y_cell = y_coord // self.metadata.cell_size[1]

        cell_num = y_cell * self.metadata.num_columns + x_cell

        print(f"{coords} --> {cell_num}")

        return cell_num
    
