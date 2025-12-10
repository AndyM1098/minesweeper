from enum import Enum, auto
import pygame as pg

class MouseButtons(Enum):
    LEFT    = pg.BUTTON_LEFT - 1
    MIDDLE  = pg.BUTTON_MIDDLE - 1
    RIGHT   = pg.BUTTON_RIGHT - 1

class ActionType(Enum):
    REVEAL  = auto()
    FLAG    = auto()
    DRAG    = auto()
    NONE    = auto()
    RESTART = auto()
    QUIT    = auto()

class EventType(Enum):
    EXIT  = auto()
    MOUSE = auto()
    KEY   = auto()
    WINDOW= auto()
    OTHER = auto()

class Mode(Enum):
    # Are we having to update game every frame
    DRAG = auto() # One or both buttons are in the down position
    NONE = auto() # Neither are in the down position