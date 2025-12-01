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

class EventParser():
    def __init__(self):
        self.current_state = State()

        return
    
    def parse_event(self, event: pygame.event.Event) -> Tuple[Tuple[int, int], Action]:
        """
            Takes in event.

            returns coordinates, and if it was a mouse click. 

            Will be updating.
        """
        print(event)
        # What is the action indeed...?
        coords: Tuple[int, int] = (-1, -1)
        ACTION: Action = Action.NONE

        # Quite the app! --> Implemented!
        if event.type == pygame.QUIT:
            ACTION = Action.QUIT
        
        # Test for mouse events
        elif event.type == pygame.MOUSEMOTION:
            # Mouse is clicked down!
            print(self.current_state.left_down)
            print(self.current_state.right_down)
            if self.current_state.left_down or self.current_state.right_down:
                ACTION = Action.DRAG
                print("Dragging!")
            else:
                ACTION = ACTION.NONE
                print("Nothing!")
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
            print("Entering Drag Mode!")
        elif event.type == pygame.MOUSEBUTTONUP:
            print("Leaving Drag Mode")
            # Leave drag mode
            if event.button == MouseButtons.LEFT.value:
                # Left mouse
                self.current_state.left_down = False
                ACTION = Action.REVEAL
                print("ACTION: REVEAL")
            elif event.button == MouseButtons.RIGHT.value:
                self.current_state.right_down = False
                ACTION = Action.FLAG
                print("ACTION: REVEAL")
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

        return coords, ACTION

class EventHandler():

    def __init__(self):
        self.current_state = State()
        self.event_parser = EventParser()

    def process_event(self, event: pygame.event.Event):
        # This should return a value, with a coordinate!
        coord, action = self.event_parser.parse_event(event)
        return coord, action
