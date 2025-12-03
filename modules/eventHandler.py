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

# Get basic event handler going!

class EventHandler():

    class ActionType():
        def __init__(self, coords: Tuple[int, int], action: Action):
            self.action = action
            self.coords = coords
            return
        def __str__(self):
            return f'ActionType(action={self.action}, coords={self.coords})'

    def __init__(self, event_function: callable = pygame.event.get):
        self.state = State()
        self._event_function = event_function
        return

    def get_event(self):
        return next(self._get_event())

    def _get_event(self) -> any:
        while True:
            for e in self._event_function():
                yield e

    def _parse_event(self, event):
        
        coords: Tuple[int, int] = (-1, -1)
        ACTION: Action = Action.NONE
        print(event)
        
        # Quite the app!
        if event.type == pygame.QUIT:
            ACTION = Action.QUIT
        elif event.type == pygame.WINDOWCLOSE:
            ACTION = Action.QUIT


        # Test for mouse events
        elif event.type == pygame.MOUSEMOTION:
            # Mouse is clicked down!
            if self.state.left_down or self.state.right_down:
                ACTION = Action.DRAG
            else:
                ACTION = ACTION.NONE
            coords = event.pos
        elif event.type == pygame.MOUSEBUTTONDOWN:
            # If user presses down. We go into drag mode. 
            #   This will essentially make sure that the 
            #   current cell we are on is highlighted or something
            if event.button == MouseButtons.LEFT.value:
                assert self.state.left_down == False
                self.state.left_down = True
            elif event.button == MouseButtons.RIGHT.value:
                assert self.state.right_down == False
                self.state.right_down = True
            coords = event.pos
            ACTION = Action.DRAG
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == MouseButtons.LEFT.value:
                assert self.state.left_down == True
                self.state.left_down = False
                ACTION = Action.REVEAL
            elif event.button == MouseButtons.RIGHT.value:
                assert self.state.right_down == True
                self.state.right_down = False
                ACTION = Action.FLAG
            coords = event.pos
        # Test for keyboard events!
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r:
                print("RESTART GAME BOARD!")
                ACTION = Action.RESTART
            else:
                print("Sorry, key not registered!")
                ACTION = Action.NONE
        
        self.state.action = ACTION
        
        if ACTION == Action.DRAG:
            self.state.mode = Mode.DRAG
        else:
            self.state.mode = Mode.NONE
        
        return coords, ACTION
    
    def _make_action(self, coord: Tuple[int, int], action: Action):
        assert isinstance(coord, tuple)
        assert isinstance(action, Action)
        return EventHandler.ActionType(coord, action)
    
    def process_event(self, event: pygame.event.Event) -> ActionType:
        # This should return a value, with a coordinate!
        self._validate_event(event)
        coord, action = self._parse_event(event)
        return self._make_action(coord, action)
    
    def get_action(self):
        event = self.get_event()
        assert self._validate_event(event) == True
        coord, action = self._parse_event(event)
        assert self._validate_coord(coord) == True
        return self._make_action(coord, action)
    
    # Validation functions
    def _validate_event(self, e: pygame.event.Event) -> bool:
        if not isinstance(e, pygame.event.Event):
            raise TypeError(f"Expected pygame.event.Event, got {type(e)}")
        return True
    
    def _validate_coord(self, coord: Tuple[int, int]) -> bool:
        assert(
            isinstance(coord, tuple) and
            len(coord) == 2 and
            isinstance(coord[0], int) and
            isinstance(coord[1], int)
        )

        return True
"""


What we essentially want for the event handler to do is get events from the pygame queue, process event
which entails parsing the event. We will return a eventAction object that contains more readable information.

The event handler should be able to take in a function that returns event objects.

    That function will be called in a generator function. 




"""