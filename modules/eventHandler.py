from dataclasses import dataclass
from typing import List, Tuple
import pygame as pg
from .enums import MouseButtons, Action
from enum import Enum, auto
from collections.abc import Callable, Generator

import time

class Mode(Enum):
    DRAG = auto()
    NONE = auto()
    REVEAL = auto()

class State:
    button_state: List[bool] = [False, False, False]
    pos: Tuple[int, int] = [0, 0]
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

    def __init__(self, event_function: Callable = pg.event.get):
        self.state = State()
        self._event_function = event_function
        self._event_gen = self._get_event()
        pg.event.set_blocked(pg.MOUSEMOTION)
        return

    def get_event(self):
        return next(self._event_gen)

    def _get_event(self) -> Generator[pg.event.Event, None, None]:
        while True:
            event_list = self._event_function()
            if len(event_list) == 0:
                yield None
            for e in event_list:
                yield e
            

    def _parse_event(self, event):
        
        coords: Tuple[int, int] = (-1, -1)
        ACTION: Action = Action.NONE
        print(event)
        
        # Quite the app!
        if event.type == pg.QUIT:
            ACTION = Action.QUIT
        elif event.type == pg.WINDOWCLOSE:
            ACTION = Action.QUIT

        elif event.type == pg.MOUSEBUTTONDOWN:
            # If user presses down. We go into drag mode.
            #   This will essentially make sure that the 
            #   current cell we are on is highlighted or something
            # print("DOWNN")
            # print(event.button)
            # exit(0)
            if event.button == MouseButtons.LEFT.value:
                assert self.state.button_state[MouseButtons.LEFT.value] == False
                self.state.button_state[MouseButtons.LEFT.value] = True
                print(self.state.button_state[MouseButtons.LEFT.value])
            elif event.button == MouseButtons.RIGHT.value:
                assert self.state.button_state[MouseButtons.RIGHT.value] == False
                self.state.button_state[MouseButtons.RIGHT.value] = True
            coords = event.pos
            ACTION = Action.DRAG
        elif event.type == pg.MOUSEBUTTONUP:
            if event.button == MouseButtons.LEFT.value:
                assert self.state.button_state[MouseButtons.LEFT.value] == True
                self.state.button_state[MouseButtons.LEFT.value] = False
                ACTION = Action.REVEAL
            elif event.button == MouseButtons.RIGHT.value:
                assert self.state.button_state[MouseButtons.RIGHT.value] == True
                self.state.button_state[MouseButtons.RIGHT.value] = False
                ACTION = Action.FLAG
            coords = event.pos

        # Test for keyboard events!
        elif event.type == pg.KEYDOWN:
            if event.key == pg.K_r:
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
    
    def process_event(self, event: pg.event.Event) -> ActionType:
        # This should return a value, with a coordinate!
        self._validate_event(event)
        coord, action = self._parse_event(event)
        return self._make_action(coord, action)
    
    def _get_mouse_coords(self):
        while True:
            yield pg.mouse.get_pos()
    
    def get_mouse_pos(self) -> Tuple[int, int]:
        return next(self._get_mouse_coords())

    def _get_mouse_action(self, buttons, pos):

        print(buttons, pos)

    def get_action(self):
        
        """
            We want to implement a way to constantly get the mouse state!
            We can in fact create another generator that gets the current mouse state, 

            In fact all we need to do is disable mouse motion events. I can just get that on the fly as that isn't as important as a mouse
            click event. If a mouse click event comes in, we proccess that instead.

        """

        coord = (0,0)
        action = Action.NONE

        event = self.get_event()
        if self._validate_event(event):
            coord, action = self._parse_event(event)
            assert self._validate_coord(coord) == True
            print(event)
        else:
            pass # print(None)
            
        
        pos = self.get_mouse_pos()
        # print(pos)
        
        # self._get_mouse_action(pos)
        
        
        
        
        return self._make_action(coord, action)
    
    # Validation functions
    def _validate_event(self, e: pg.event.Event | None) -> bool:
        if e is None:
            return False
        if not isinstance(e, pg.event.Event):
            raise TypeError(f"Expected pg.event.Event, got {type(e)}")
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


What we essentially want for the event handler to do is get events from the pg queue, process event
which entails parsing the event. We will return a eventAction object that contains more readable information.

The event handler should be able to take in a function that returns event objects.

    That function will be called in a generator function. 




"""