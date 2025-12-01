from dataclasses import dataclass
from typing import List, Tuple
import pygame
from .enums import MouseButtons, Action
from enum import Enum, auto

class Mode(Enum):
    DRAG = auto()
    NONE = auto()
    REVEAL = auto()


@dataclass
class State:
    left_down: bool = False
    right_down: bool = False
    pos: Tuple[int, int] = (0, 0)
    on_screen: bool = False
    action: Action = None
    _mode: Mode = Mode.NONE
    
    @property
    def mode(self):
        return self._mode
    
    @mode.setter
    def mode(self, m: Mode) -> None:
        assert isinstance(m, Mode)
        self._mode = m


class EventHandler():

    def __init__(self):
        self.current_state = State()

    def _validate_event(self, e: pygame.event.Event) -> None:
        if not isinstance(e, pygame.event.Event):
            raise TypeError(f"Expected pygame.event.Event, got {type(e)}")
    
    def _parse_event(self, event):
        
        coords: Tuple[int, int] = (-1, -1)
        ACTION: Action = Action.NONE

        # Quite the app! --> Implemented!
        if event.type == pygame.QUIT:
            ACTION = Action.QUIT
        
        # Test for mouse events
        elif event.type == pygame.MOUSEMOTION:
            # Mouse is clicked down!
            if self.current_state.left_down or self.current_state.right_down:
                ACTION = Action.DRAG
            else:
                ACTION = ACTION.NONE
            coords = event.pos
        elif event.type == pygame.MOUSEBUTTONDOWN:
            # If user presses down. We go into drag mode. 
            #   This will essentially make sure that the 
            #   current cell we are on is highlighted or something
            if event.button == MouseButtons.LEFT.value:
                self.current_state.left_down = True
            elif event.button == MouseButtons.RIGHT.value:
                self.current_state.right_down = True
            coords = event.pos
            ACTION = Action.DRAG
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == MouseButtons.LEFT.value:
                self.current_state.left_down = False
                ACTION = Action.REVEAL
                print("ACTION: REVEAL")
            elif event.button == MouseButtons.RIGHT.value:
                self.current_state.right_down = False
                ACTION = Action.FLAG
                print("ACTION: FLAG")
            coords = event.pos
        # Test for keyboard events!
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r:
                print("RESTART GAME BOARD!")
                ACTION = Action.RESTART
            else:
                print("Sorry, key not registered!")
                ACTION = Action.NONE
        
        
        self.current_state.action = ACTION
        
        if ACTION == Action.DRAG:
            self.current_state.mode = Mode.DRAG
        else:
            self.current_state.mode = Mode.NONE
        

        return coords, ACTION
    
    def process_event(self, event: pygame.event.Event):
        # This should return a value, with a coordinate!
        self._validate_event(event)
        coord, action = self._parse_event(event)
        return coord, action
