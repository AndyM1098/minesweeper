from __future__ import annotations
from dataclasses import dataclass
from typing import List, Tuple
import pygame as pg
# from .enums import MouseButtons, ActionType
from enum import Enum, auto
from collections.abc import Callable, Iterator

import time


class Mode(Enum):
    DRAG = auto()
    NONE = auto()
    REVEAL = auto()

class State:
    button_state: List[bool] = [False, False, False]
    pos: List[int] = [0, 0]
    on_screen: bool = False
    _mode: Mode = Mode.NONE

    @property
    def mode(self) -> Mode:
        return self._mode
    
    @mode.setter
    def mode(self, m: Mode) -> bool:
        if not isinstance(m, Mode):
            return False
        self._mode = m
        return True

@dataclass(frozen=True, slots=True)
class Action():
    action: ActionType
    coords: Tuple[int, int]

    def __str__(self):
        return f'Action(action={self.action}, coords={self.coords})'

class MouseButtons(Enum):
    LEFT    = 0
    MIDDLE  = 1
    RIGHT   = 2

class ActionType(Enum):
    REVEAL  = auto()
    FLAG    = auto()
    DRAG    = auto()
    NONE    = auto()
    RESTART = auto()
    QUIT    = auto()

class EventHandler():

    def __init__(self, event_function: Callable = pg.event.get, ):
        self.state = State() # Holds the current state of input
        self._event_function = event_function
        
        # Set generators
        self._mouse_pos_gen = self._get_mouse_pos_gen()
        self._event_gen = self._get_event_gen()
        
        # set up way to accept these. 
        pg.event.set_blocked(pg.MOUSEMOTION)

        return

    def _parse_event(self, event):

        coords: Tuple[int, int] = (-1, -1)
        ACTION: ActionType = ActionType.NONE
        print(event)
        
        # Quite the app!
        if event.type == pg.QUIT:
            ACTION = ActionType.QUIT
        elif event.type == pg.WINDOWCLOSE:
            ACTION = ActionType.QUIT

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
            elif event.button == MouseButtons.RIGHT.value:
                assert self.state.button_state[MouseButtons.RIGHT.value] == False
                self.state.button_state[MouseButtons.RIGHT.value] = True
            coords = event.pos
            ACTION = ActionType.DRAG
        elif event.type == pg.MOUSEBUTTONUP:
            if event.button == MouseButtons.LEFT.value:
                assert self.state.button_state[MouseButtons.LEFT.value] == True
                self.state.button_state[MouseButtons.LEFT.value] = False
                ACTION = ActionType.REVEAL
            elif event.button == MouseButtons.RIGHT.value:
                assert self.state.button_state[MouseButtons.RIGHT.value] == True
                self.state.button_state[MouseButtons.RIGHT.value] = False
                ACTION = ActionType.FLAG
            coords = event.pos

        # Test for keyboard events!
        elif event.type == pg.KEYDOWN:
            if event.key == pg.K_r:
                print("RESTART GAME BOARD!")
                ACTION = ActionType.RESTART
            else:
                print("Sorry, key not registered!")
                ACTION = ActionType.NONE
        
        self.state.action = ACTION
        
        if ACTION == ActionType.DRAG:
            self.state.mode = Mode.DRAG
        else:
            self.state.mode = Mode.NONE
        
        return coords, ACTION
    
    def get_action(self) -> Action:
       return self._get_action()
    
    def _check_mouse_movement(self, nc: Tuple[int,int]):
        """
            Check if the mouse movement
        """
        if nc[0] == self.state.pos[0] and nc[1] == self.state.pos[1]:
            return False
        return True
    
    def _get_event_pos(self, e: pg.event.Event):
        pos: Tuple[int, int] | None = None
        try:
            pos = e.pos
        except AttributeError as error:
            print(error)
        return pos
        
    def _get_action(self) -> Action: 
        """
            We want to implement a way to constantly get the mouse state!
            We can in fact create another generator that gets the current mouse state, 

            In fact all we need to do is disable mouse motion events. I can just get that on the fly as that isn't as important as a mouse
            click event. If a mouse click event comes in, we proccess that instead.

        """

        coord = (0,0)
        action: ActionType = ActionType.NONE

        # First get a valid event from the queue
        event: pg.event.Event | None = self.get_event()
        event_valid = self._validate_event(event)
        
        # Did Mouse move since last frame
        m_move_flag = self._check_mouse_movement(self._get_event_pos(event))
        # If a valid event, go ahead and see if it is an event we need
        #   to proccess, or update state. 
        #       Like, going off screen, does that clear what we have on the screen, or what
        if event_valid is True:
            coord, action = self._parse_event(event)
            assert self._validate_coord(coord) == True
            print(event)
        else:
            coord = self.get_mouse_pos()
            if self.state.mode == Mode.DRAG:
                action = ActionType.DRAG
            else:
                action = ActionType.NONE

        pos = self.get_mouse_pos()
        
        # self._get_mouse_action(pos)
        
        return self._make_action(coord, action)
    
    def _make_action(self, c: Tuple[int, int], a: ActionType):
        assert isinstance(c, tuple)
        assert isinstance(c[0], int)
        assert isinstance(c[1], int)
        assert isinstance(a, ActionType)
        return Action(action = a, coords=c)
    
    """
        Generator Functions
    """
    
    # Mouse Generator
    def get_mouse_pos(self) -> Tuple[int, int]:
        return next(self._mouse_pos_gen)
    
    def _get_mouse_pos_gen(self) -> Iterator[Tuple[int, int]]:
        while True:
            yield pg.mouse.get_pos()
    
    # Event generator
    def get_event(self) -> pg.event.Event | None:
        return next(self._event_gen)

    def _get_event_gen(self) -> Iterator[pg.event.Event | None]:
        while True:
            event_list = self._event_function()
            if len(event_list) == 0:
                yield None
            for e in event_list:
                yield e

    """
        Validation functions
    """
    def _validate_event(self, e: pg.event.Event | None) -> bool:
        if e is None:
            return False
        if not isinstance(e, pg.event.Event):
            return False
        return True
    
    def _validate_coord(self, coord: Tuple[int, int]) -> bool:
        if( not isinstance(coord, tuple) or
            len(coord) != 2 or
            not isinstance(coord[0], int) or
            not isinstance(coord[1], int)
            ):
            return False
        return True
"""


What we essentially want for the event handler to do is get events from the pg queue, process event
which entails parsing the event. We will return a eventAction object that contains more readable information.

The event handler should be able to take in a function that returns event objects.

    That function will be called in a generator function. 


    We got all the mouse and keyboard clicks being registered forthe most part. 
    
    What we want to work on next is getting the correct action. 
    
    Example:
    
    Mouse button up always means reveal / flag
    
    On MOUSE DOWN:
        We must register the drag event IF the mouse button is down
        If there are no events in the pygame queue to process, 
            we simply check the state of the mouse to see if we are still on a drag event
            This just means one of the buttons are still being pressed!
    
"""