from .cell import Cell, CellType, CellState, MineCell, EmptyCell
from typing import Tuple, List, Union
import pygame
import random
import sys
from .settings import Settings
from .enums import RevealColors, cell_neighbor_increments, Action
from .enums import CellFlagged, CellRevealed


class GridMetaData:
    def __init__(self):
        
        self.off_set_x: int = 0
        self.off_set_y: int = 0

        self.num_columns:int = 0
        self.num_rows:int = 0

        self.cell_width:int = 0
        self.cell_height:int = 0
        
        # utility variables
        self.num_mines: int = 0
        self.num_cells:int  = 0
        self.num_flags:int  = 0
        self.mine_ids: List[int] = []

        self.parent_screen: pygame.Surface  = None

        self.cell_group: pygame.sprite.Group = None

        # Contains the ids of the cells that contain mines
        self.mine_ids: List[int] = []
        self.mine_ids_group: pygame.sprite.Group = None

        self.color_set = None

        self.cell_neighbors: List[Tuple[int]] = []

        return

    def on_init(self, parent_screen: pygame.Surface, settings: Settings):
        
        self.num_columns: int = settings.num_columns
        self.num_rows: int = settings.num_rows

        self.num_cells: int = self.num_columns * self.num_rows
        self.num_flags: int = 0
        self.num_mines: int = settings.num_mines

        self.parent_screen: pygame.Surface = parent_screen

        if settings.cell_height == None:
            self.row_height = int(self.parent_screen.get_height() / self.num_rows)
        else:
            self.row_height = settings.cell_height
        
        if settings.cell_width == None:
            self.column_width = int(self.parent_screen.get_width() / self.num_columns)
        else:
            self.column_width = settings.cell_width

        self.mine_ids_group = pygame.sprite.Group()
        self.set_mines()

        self.color_set = list(RevealColors)
        self.seed = settings.seed


        # Set the direction of each neighbor
        #   This also defines the order of the visit
        #   If the user users for I in self.cell_neighbors.
        
        self.cell_neighbors = [v.value for v in list(cell_neighbor_increments)]

        print(self.cell_neighbors)

        return
    
    def set_mines(self):
    
        # Clear all mines!
        self.mine_ids.clear()
        self.mine_ids = random.sample(range(0, self.num_cells), self.num_mines)
        print(f"Num of mines: {len(self.mine_ids)}\n\tmines: {self.mine_ids}")

        return

    @property
    def cell_size(self)-> Tuple[int, int]:
        """
            Returns Tuple[cell width, cell height]
                where cell width and cell height are int
        """
        print(f"Cell Size: {self.column_width}, {self.row_height}")
        return (self.column_width, self.row_height)

class Grid:
    """
        Class that holds the grid information.

        The grid is comprised of a 2d array of cells.

    """
    # todo
    #   Fix parameter list!
    def __init__(self, App: pygame.Surface, settings: Settings):
        
        # Contains the grid metadata
        self.metadata: GridMetaData = GridMetaData()
        self.metadata.on_init(App._display_surf, settings)

        # Cell groups
        self.cell_group: pygame.sprite.Group = pygame.sprite.Group()
        self.mine_group: pygame.sprite.Group = pygame.sprite.Group()

        # Group of cells that will need to be rendered!
        self.render_queue: pygame.sprite.Group = pygame.sprite.Group()
        # Flag to determine whether or not render_queue empty
        self._rq_empty: bool = True

        # 2d matrix of Cells representing each cell!
        self.grid: List[List[Union[MineCell, EmptyCell]]] = self._init_grid()
        self._grid_init = True

        return

    # getters
    @property
    def rq_empty(self)-> bool:
        return self._rq_empty
    
    def get_render_queue(self)-> pygame.sprite.Group:
        return self.render_queue

    # Utilities
    def get_grid_coords_from_cell_num(self, cell_num: int)->Tuple[int, int]:
        r = cell_num // self.metadata.num_columns
        c = cell_num % self.metadata.num_columns
        return r, c
    """

        Below are functions used in __init__()
    
    """
    def _init_grid(self) -> List[List[Cell]]:
        
        ret_grid = [
                        [
                            None for _ in range(0, self.metadata.num_columns)
                        ]
                            for _ in range(0, self.metadata.num_rows)
                    ]
        
        self._init_mines(ret_grid)
        self._init_empty(ret_grid)

        # Once grid is set, we want to render every cell made!
        self.render_queue.add(self.cell_group)
        self._rq_empty = len(self.render_queue) == 0

        return ret_grid
    
    def _init_mines(self, g: List[List[Cell]]):

        self.metadata.set_mines(seed=1)
        cell_size = self.metadata.cell_size

        for id in self.metadata.mine_ids:
            r, c = self.id_to_grid_coords(id)
            new_mine = MineCell(id,
                                  self.compute_cell_pos(r, c),
                                  cell_size,
                                  r,
                                  c,)
                
            g[r][c] = new_mine
            self.mine_group.add(new_mine)
            self.cell_group.add(new_mine)

        return True
          
    def _init_empty(self, g: List[List[Cell]]):

        for r in range(0, self.metadata.num_rows):
            for c in range(0, self.metadata.num_columns):
                
                if g[r][c] == None:
                    cell_id = r * self.metadata.num_columns + c
                    cell_pos = self.compute_cell_pos(r, c)
                    
                    new_cell = EmptyCell(cell_id,
                                            cell_pos,
                                            self.metadata.cell_size,
                                            r,
                                            c,)
                    
                    g[r][c] = new_cell
                    self.cell_group.add(new_cell)

        print(f"Lower Right Cell info:")
        print(f"\tpos = {self.grid[-1][-1].rect.x, self.grid[-1][-1].rect.y}")
        print(f"\tcell size = {self.grid[-1][-1].rect.w, self.grid[-1][-1].rect.h}")
        print(f"\tScreen size: {self.metadata.parent_screen.get_size()}")
        
        # print(f"\tpos = {self.grid[-1][-1].grid_r, self.grid[-1][-1].grid_c}\n")
        return

    def _determine_neighbor_cells(self):
        """
            Function goes through all mines

            For each mine, update all surronding cells
                If a surronding cell is a Mine, ignore it!
        """

        n = self.metadata.num_rows
        m = self.metadata.num_columns

        for mine in self.mine_group:
            r = mine.grid_r
            c = mine.grid_c

            for dr, dc in self.metadata.cell_neighbors:
                nr = r + dr
                nc = c + dc

                if 0 <= nr < n and 0 <= nc < m and isinstance(self.grid[nr][nc], EmptyCell):
                    self.grid[nr][nc].increment_mine_count()
    
    
    
    def _reveal_cells(self):
        for r in range(0, self.metadata.num_rows):
            for c in range(0, self.metadata.num_columns):
                self.grid[r][c].reveal_cell()
        return
    
    def id_to_grid_coords(self, cell_id: int)-> Tuple[int, int]:
        r = cell_id // self.metadata.num_columns
        c = cell_id % self.metadata.num_columns
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

            if self.grid[r][c].number_of_neighbors > 0:
                self.grid[r][c].reveal_cell()
                self.render_queue.add(self.grid[r][c])
                self._rq_empty = False
                continue
            else:
                for dir in self.metadata.cell_neighbors:
                    stack.append((r + dir[0], c + dir[1]))
                
            self.grid[r][c].reveal_cell()
            self.render_queue.add(self.grid[r][c])
            self._rq_empty = False
        
        return
    
    def _update_logic_reveal_mines(self):
        """
            We essentially want to update ALL mines here!
        """

        for mine in self.mine_group:
            mine.reveal_cell()
            self.render_queue.add(mine)
            self._rq_empty = False

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

    def _logic_reveal(self, cell_id: int):
        cell = self.get_cell_from_id(cell_id)

        if cell.flag:
            return False

        if isinstance(cell, EmptyCell):
            # Only reveal the one cell!
            if cell.number_of_neighbors > 0:
                cell.reveal_cell()
                self.render_queue.add(cell)
                self._rq_empty = False
            # Reveal ALL surrounding EMPTY cells
            else:
                self._update_logic_empty_cells(*self.get_grid_coords_from_cell_num(cell_id))
        else:
            if cell.flag == CellFlagged.NO_FLAG:
                cell.reveal_cell()
            self._update_logic_reveal_mines()
        
        return True

    def get_cell_from_id(self, cell_id: int):
        r, c = self.id_to_grid_coords(cell_id)
        return self.grid[r][c]


    def update_logic(self, sprite_num: int, action: Action):

        assert isinstance(action, Action)
        assert isinstance(sprite_num, int)

        res = False

        if action == Action.FLAG:
            print("DDDD")
            res = self._logic_flag(sprite_num)
        
        elif action == Action.REVEAL:
            res = self._logic_reveal(sprite_num)
    
        return res
    
    def update_render(self):
        print("Updating render!")

        assert isinstance(self.render_queue, pygame.sprite.Group)

        if(self._rq_empty == False):
            self.render_queue.draw(self.metadata.parent_screen)
            self.render_queue.empty()
            self._rq_empty = True

        return

    @property
    def cell_size(self)-> any:
        return self.metadata.cell_size

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
    
