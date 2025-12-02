from enum import Enum, auto

class RevealColors(Enum):
    ZERO    = (56,64,72)
    ONE     = (124,199,255)
    TWO     = (102,194,102)
    THREE   = (255,119,136)
    FOUR    = (38,136,255)
    FIVE    = (221,170,34)
    SIX     = (102,204,204)
    SEVEN   = (0, 0, 0)
    EIGHT   = (128, 128, 128)
    MINE    = (255, 0, 0)
    NOT_SET = (249, 6, 249)
    NOT_REVEALED = (125,125,125)
    FLAGGED = (225, 225, 225)

    LOWER_RIGHT_CORNER_CELL = (75, 254, 62)

    # Define regulary used values perhaps...?
    WHITE = (255, 255, 255)
    RED = (255, 0, 0)
    GREEN = (0, 255, 0)
    BLUE = (0, 0, 255)
    BLACK = (0, 0, 0)

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

class Action(Enum):
    REVEAL  = 0
    FLAG    = 1
    DRAG    = 2
    NONE    = auto()
    RESTART = auto()
    QUIT    = auto()

class MouseButtons(Enum):
    LEFT    = 1
    MIDDLE  = 2
    RIGHT   = 3


class CellFlagged(Enum):
    """
        Use to set and determine if a cell has been flagged or not
    """
    FLAG    = True
    NO_FLAG = False

class CellRevealed(Enum):
    """
        Use to set and determine if a cell has been revealed
    """
    REVEALED = True
    NO_REVEAL = False