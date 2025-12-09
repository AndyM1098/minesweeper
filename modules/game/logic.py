from .grid import Grid
from .config import Config
from .render import Render
import pygame as pg
from ..event_handler.eventAction import Action
from ..event_handler.eventEnums import ActionType
from dataclasses import dataclass
from typing import Union, List, Tuple
from .cell import MineCell, EmptyCell


class Logic():
    def __init__(self, grid: Grid, config: Config, render: Render):
        
        self._render = render
        self._grid: Grid = grid
        self._config: Config = config
        
        self._curr_action: ActionType = None
        self._curr_action_x: int = 0
        self._curr_action_y: int = 0
        self._curr_action_grid_row: int = 0
        self._curr_action_grid_col: int = 0

        self.determine_adjacent_mine_count()

    def _set_current_event(self, a: Action):
        self._curr_action = a.action
        self._curr_action_x: int = a.coords[0]
        self._curr_action_y: int = a.coords[1]
        r, c = self._get_cell_grid_coords()
        self._curr_action_grid_row = r
        self._curr_action_grid_col = c

    def _get_cell_grid_coords(self):
        r = self._curr_action_y // self._config.cell_height
        c = self._curr_action_x // self._config.cell_width
        return r, c

    def update_board(self, a: Action):
        
        self._set_current_event(a)

        if self._curr_action == ActionType.REVEAL:
            print("REVEAL!")
            self._reveal_cell()
        
        elif self._curr_action == ActionType.FLAG:
            #print("FLAG")
            self._flag_cell()
        
        elif self._curr_action == ActionType.DRAG:
            #print("DRAG")
            self._drag_cell()

    def _reveal_cell_bfs(self, r, c):
        
        stack: List[Tuple[int, int]] = []
        v = [[False for _ in range(0, self._config.num_columns)] for _ in range(0, self._config.num_rows)]
        
        stack.append((r, c))
        
        while len(stack):
            r, c = stack.pop()
            
            if r < 0 or r >= self._config.num_rows or c < 0 or c >= self._config.num_columns:
                continue
            elif v[r][c]:
                continue
            
            v[r][c] = True

            self._grid.board[r][c].reveal_cell()
            self._render.add_sprite_to_render_queue(self._grid.board[r][c])

            if self._grid.board[r][c].adjacent_mine_count == 0:
                for dr, dc in self._config.cell_neighbors:
                    stack.append((r + dr, c + dc))
                
        return

    def _reveal_cell(self):
        r, c = self._curr_action_grid_row, self._curr_action_grid_col
        cell: Union[MineCell, EmptyCell] = self._grid.board[r][c]
        
        print(self._grid.board[r][c].adjacent_mine_count)
        print(self._grid.board[r][c].grid_r, self._grid.board[r][c].grid_c)

        if cell.flag:
            print("Cell is flagged!")
            return False
        elif cell.revealed:
            print("Cell is Already Revealed!")
            return False
        
        if isinstance(cell, MineCell):
            # First reveal all mines
            print("BOOM")
        else:
            self._reveal_cell_bfs(r, c)

    def _flag_cell(self):
        pass

    def _drag_cell(self):
        pass
    
    def get_cell_rc_from_id(self, id: int) -> Tuple[int, int]:
        return (id // self._config.num_columns, id % self._config.num_columns)
    
    def determine_adjacent_mine_count(self):

        for cell_id in self._grid.metadata.mine_ids:
            r, c = self.get_cell_rc_from_id(cell_id)

            for rx, cx in self._grid.metadata.cell_neighbors:
                nr = r + rx
                nc = c + cx

                try:
                    assert nr >= 0 and nc >= 0
                    self._grid.board[nr][nc]
                except Exception as e:
                    print(e)
                    continue
                
                self._grid.board[nr][nc].increment_adjacent_mine_count()
