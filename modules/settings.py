from dataclasses import dataclass

@dataclass
class Settings:
    num_rows: int = 100
    num_columns: int = 100
    grid_width: int = 1080
    grid_height: int = 800
    cell_height = None
    cell_width = None
    frame_rate: int = 240
    num_mines: int = 50
    seed = 1