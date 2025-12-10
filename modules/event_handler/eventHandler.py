from __future__ import annotations
from dataclasses import dataclass
from typing import List, Tuple, Set, Dict
import pygame as pg
from enum import Enum, auto
from collections.abc import Callable, Iterator

from .eventState import State as es
from .eventParser import EventParser as ep
from .eventConfig import EventConfig as ec
from .eventEnums import ActionType, Mode
from .eventAction import Action

class EventHandler():
    
    State = es
    EventParser = ep
    EventConfig = ec
    
    def __init__(self):
        
        self.state = EventHandler.State() # Holds the current state of input
        self._event_function = pg.event.get

        self.config = EventHandler.EventConfig()
       
        # Set generators
        self._mouse_pos_gen = self._get_mouse_pos_gen()
        self._event_gen = self._get_event_gen()

        self._parser = EventHandler.EventParser(config = self.config, s = self.state)

        return

    # def _event_to_action(self, e: pg.event.Event):

    #     coords: Tuple[int, int] = (-1, -1)
    #     coords_valid: bool = True
    #     coords, coords_valid = self._parser.get_event_pos()
    #     next_action: ActionType = ActionType.NONE

    #     # Quite the app!
    #     if e.type in (pg.QUIT, pg.WINDOWCLOSE):
    #         next_action = ActionType.QUIT

    #     # Check mouse button down
    #     elif e.type == pg.MOUSEBUTTONDOWN:
    #         next_action = self._parse_button_down(e)
    #     elif e.type == pg.MOUSEBUTTONUP:
    #         next_action = self._parse_button_up(e)

    #     # Test for keyboard events!
    #     elif e.type == pg.KEYDOWN:
    #         if e.key == pg.K_r:
    #             print("RESTART GAME BOARD!")
    #             next_action = ActionType.RESTART
    #         else:
    #             print("Sorry, key not registered!")
    #             next_action = ActionType.NONE
        
    #     # self.state.action_type = next_action
        
    #     if next_action == ActionType.DRAG:
    #         self.state.mode = Mode.DRAG
    #     else:
    #         self.state.mode = Mode.NONE

    #     return coords, next_action
    
    def _check_mouse_movement(self, nc: Tuple[int,int]):
        """
            Check if mouse has moved since last frame.
        """
        if nc[0] == self.state.pos[0] and nc[1] == self.state.pos[1]:
            return False
        return True

    def get_action(self) -> Action:
       return self._get_action()
    
    def _get_action(self) -> Action:
        """
            We want to implement a way to constantly get the mouse state!
            We can in fact create another generator that gets the current mouse state, 

            In fact all we need to do is disable mouse motion events. I can just get that on the fly as that isn't as important as a mouse
            click event. If a mouse click event comes in, we proccess that instead.

        """

        coords = (0,0)
        action: ActionType = ActionType.NONE

        skip_event = False
        # First get a valid event from the queue
        event: pg.event.Event | None = self.get_event()
        self._parser.set_current_event(event)
        
        event_valid = self._parser.is_event_valid()

        # If event is valid
        if event_valid is True:
            action = self._parser.get_action_from_event()
            
            if action == ActionType.NONE:
                skip_event = True
            else:
                coords, _ = self._parser.get_event_pos()
        else:
            skip_event = True
        
        if skip_event:

            # If no events. Then we just see if we are still in drag mode.
            coords = self.get_mouse_pos()
            self.state.pos = coords

            if self.state.mode == Mode.DRAG:
                action = ActionType.DRAG
            else:
                action = ActionType.NONE

        return self._make_action(coords, action)
    
    def _make_action(self, c: Tuple[int, int], a: ActionType):
        assert self._validate_coord(c) == True
        assert isinstance(a, ActionType)
        return Action(action = a, coords=c)
    
    # Mouse Generator
    def get_mouse_pos(self) -> Tuple[int, int]:
        return next(self._mouse_pos_gen)
    
    def _get_mouse_pos_gen(self) -> Iterator[Tuple[int, int]]:
        while True:
            yield pg.mouse.get_pos()
    
    # Event generator
    def get_event(self) -> pg.event.Event | None:
        e = next(self._event_gen)
        return e

    def _get_event_gen(self) -> Iterator[pg.event.Event | None]:
        while True:
            event_list = self._event_function()
            if len(event_list) == 0:
                yield None
            for e in event_list:
                yield e
    
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