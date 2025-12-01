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

        self.parent_screen: pygame.Surface = None

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
        #   If the user users for i in self.cell_neighbors.
        
        self.cell_neighbors = [v.value for v in list(cell_neighbor_increments)]

        print(self.cell_neighbors)

        return
    
    def set_mines(self, seed: int = None):
    
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
    def __init__(self):
        
        # Contains the grid metadata
        self.metadata: GridMetaData = None

        # 2d matrix of Cells representing each cell!
        self.grid: List[List[Union[MineCell, EmptyCell]]] = None

        # Cell groups
        self.cell_group: pygame.sprite.Group = None
        self.mine_group: pygame.sprite.Group = None

        #Group of cells that will need to be rendered!
        self.render_queue: pygame.sprite.Group = None
        #Flag to determine whether or not render_queue empty
        self._rq_empty: bool = True

        return

    def _init_metadata(self, settings: Settings, App):
        self.metadata = GridMetaData()
        self.metadata.on_init(App._display_surf, settings)
        return True
    
    def get_grid_coords_from_cell_num(self, cell_num: int)->Tuple[int, int]:
        r = cell_num // self.metadata.num_columns
        c = cell_num % self.metadata.num_columns
        return r, c

    def _init_grid(self):
        
        self.grid = [[None for _ in range(0, self.metadata.num_columns)] for _ in range(0, self.metadata.num_rows)]
        
        # First set all bombs!
        for m in self.mine_group:
            row, col = self.get_grid_coords_from_cell_num(m.id)

            self.grid[row][col] = MineCell(m.id, self.compute_cell_pos(row, col), self.metadata.cell_size, row, col)
            self.cell_group.add(self.grid[row][col])
            self.render_queue.add(self.grid[row][col])
        
        if(len(self.render_queue) > 0):
            self._rq_empty = False
        
        # Next set all Empty Cells!

        for i in range(0, self.metadata.num_rows):
            for j in range(0, self.metadata.num_columns):
                
                if self.grid[i][j] == None:
                    self.grid[i][j] = EmptyCell(i * self.metadata.num_columns + j,
                                                self.compute_cell_pos(i, j),
                                                self.metadata.cell_size, i, j)
                    self.cell_group.add(self.grid[i][j])
                    self.render_queue.add(self.grid[i][j])
                    self._rq_empty = False
        
        return
    
    def _init_groups(self):
        self.cell_group = pygame.sprite.Group()
        self.mine_group = pygame.sprite.Group()
        self.render_queue = pygame.sprite.Group()
        return True

    def _init_mines(self):

        self.metadata.set_mines(seed=1)
        mines = []

        for mine_id in self.metadata.mine_ids:
            r, c = self.convert_id_to_grid_coords(mine_id)
            mines.append(MineCell(mine_id, self.compute_cell_pos(r, c), self.metadata.cell_size, r, c))

        self.mine_group.add(mines)
        self.cell_group.add(mines)

        return True

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

    def on_init(self, settings: Settings, App):
        
        self._init_metadata(settings, App)
        self._init_groups()
        self._init_mines()
        self._init_grid()
        self._determine_neighbor_cells()
        
        # self._reveal_cells()
        self.update_render()
        return
    
    def convert_id_to_grid_coords(self, cell_id: int)-> Tuple[int, int]:
        row = cell_id // self.metadata.num_columns
        col = cell_id % self.metadata.num_columns
        return row, col
    
    def is_rq_empty(self)-> bool:
        return len(self.render_queue) == 0

    def determine_cell_size(self)-> Tuple[int, int]:
        """
            Based on the smallest dimension. We will make all cells the same size.
        """

        #First determine smallest dimension

        smallest_dim = min(self.metadata.parent_screen.get_width(), self.metadata.parent_screen.get_height())

        largest_cell_dim = min(self.metadata.num_columns, self.metadata.num_rows)

        cell_size = int(smallest_dim / largest_cell_dim)

        return cell_size

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
        
        if r < 0 or r >= self.metadata.num_rows or c < 0 or c >= self.metadata.num_columns:
            return
        elif v[r][c] == True:
            return

        v[r][c] = True

        if self.grid[r][c].number_of_neighbors > 0:
            self.grid[r][c].reveal_cell()
            self.render_queue.add(self.grid[r][c])
            self._rq_empty = False
            return
        
        for dir in self.metadata.cell_neighbors:
            self._update_logic_empty_cells_rec(v, r + dir[0], c + dir[1])
        
        self.grid[r][c].reveal_cell()
        self.render_queue.add(self.grid[r][c])
        
        self._rq_empty = False
        
        self.update_render()
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
        row, col = self.convert_id_to_grid_coords(cell_id)
        return self.grid[row][col]


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
    