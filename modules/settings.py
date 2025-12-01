from dataclasses import dataclass

@dataclass
class Settings:
    num_rows: int = 20
    num_columns: int = 20
    grid_width: int = 1020
    grid_height: int = 800
    cell_height = None
    cell_width = None
    frame_rate: int = 120
    num_mines: int = 50
    seed = 1