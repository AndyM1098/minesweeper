from __future__ import annotations
from dataclasses import dataclass
from typing import List, Tuple, Set
import pygame as pg
from enum import Enum, auto
from collections.abc import Callable, Iterator

import time

class Mode(Enum):
    DRAG = auto()
    NONE = auto()
    REVEAL = auto()



@dataclass(frozen=True, slots=True)
class Action():
    action: ActionType
    coords: Tuple[int, int]

    def __str__(self):
        return f'Action(action={self.action}, coords={self.coords})'

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

class EventHandler():
    
    class EventConfig():

        def __init__(self, 
                     blocked_events: Tuple[int, ...] = tuple(),
                     logical_events: Tuple[int, ...] = tuple(),
                     window_events: Tuple[int, ...] = tuple(),
                     mouse_events: Tuple[int, ...] = tuple(),
                     keyboard_events: Tuple[int, ...] = tuple(),
                    ):
            
            self.blocked_events: Set[int] = set(blocked_events)
            if len(self.blocked_events) > 0:
                pg.event.set_blocked(tuple(self.blocked_events))
            
            self.logical_events: Set[int] = set(logical_events)
            self.window_events: Set[int] = set(window_events)
            self.mouse_events: Set[int] = set(mouse_events)
            self.keyboard_events: Set[int] = set(keyboard_events)        

    class State:
        """
            Keeps the current state of input.
        """
        button_state: List[bool] = [False, False, False]
        pos: List[int] = [0, 0]
        on_screen: bool = False # todo implement
        mode: Mode = Mode.NONE
        restart_pending: bool = False 

    def __init__(self, event_function: Callable = pg.event.get, ):
        
        self.state = EventHandler.State() # Holds the current state of input
        self._event_function = event_function
        
        self.config = EventHandler.EventConfig( blocked_events=(pg.MOUSEMOTION,),
                                                logical_events=(pg.MOUSEBUTTONDOWN, 
                                                                pg.MOUSEBUTTONUP,
                                                                pg.QUIT,
                                                                pg.WINDOWCLOSE,
                                                                pg.KEYDOWN,
                                                                pg.KEYUP),
                                                window_events=(),
                                                mouse_events=(pg.MOUSEBUTTONDOWN,
                                                              pg.MOUSEBUTTONUP),
                                                keyboard_events=(pg.KEYDOWN, 
                                                                 pg.KEYUP),
                                                )
       
        # Set generators
        self._mouse_pos_gen = self._get_mouse_pos_gen()
        self._event_gen = self._get_event_gen()

        self._parser = self.EventParser(config = self.config)

        return

    def _parse_button_down(self, e: pg.event.Event) -> ActionType:
        next_action = ActionType.NONE

        if e.button == MouseButtons.LEFT.value:
            assert not self.state.button_state[MouseButtons.LEFT.value]
            self.state.button_state[MouseButtons.LEFT.value] = True
            next_action = ActionType.DRAG
        elif e.button == MouseButtons.RIGHT.value:
            assert not self.state.button_state[MouseButtons.RIGHT.value]
            self.state.button_state[MouseButtons.RIGHT.value] = True
            next_action = ActionType.DRAG

        return next_action

    def _parse_button_up(self, e: pg.event.Event) -> ActionType:
        next_action = ActionType.NONE
        if e.button == MouseButtons.LEFT.value:
            assert self.state.button_state[MouseButtons.LEFT.value] == True
            self.state.button_state[MouseButtons.LEFT.value] = False
            next_action = ActionType.REVEAL
        elif e.button == MouseButtons.RIGHT.value:
            assert self.state.button_state[MouseButtons.RIGHT.value] == True
            self.state.button_state[MouseButtons.RIGHT.value] = False
            next_action = ActionType.FLAG
        return next_action

    def _event_to_action(self, e: pg.event.Event):

        coords: Tuple[int, int] = (-1, -1)
        coords_valid: bool = True
        coords, coords_valid = self._parser.get_event_pos()
        next_action: ActionType = ActionType.NONE

        # Quite the app!
        if e.type in (pg.QUIT, pg.WINDOWCLOSE):
            next_action = ActionType.QUIT

        # Check mouse button down
        elif e.type == pg.MOUSEBUTTONDOWN:
            next_action = self._parse_button_down(e)
        elif e.type == pg.MOUSEBUTTONUP:
            next_action = self._parse_button_up(e)

        # Test for keyboard events!
        elif e.type == pg.KEYDOWN:
            if e.key == pg.K_r:
                print("RESTART GAME BOARD!")
                next_action = ActionType.RESTART
            else:
                print("Sorry, key not registered!")
                next_action = ActionType.NONE
        
        # self.state.action_type = next_action
        
        if next_action == ActionType.DRAG:
            self.state.mode = Mode.DRAG
        else:
            self.state.mode = Mode.NONE
        print(coords)
        print(next_action)
        return coords, next_action
    
    def get_action(self) -> Action:
       return self._get_action()
    
    def _check_mouse_movement(self, nc: Tuple[int,int]):
        """
            Check if mouse has moved since last frame.
        """
        if nc[0] == self.state.pos[0] and nc[1] == self.state.pos[1]:
            return False
        return True
    
    



    def has_mouse_moved(self, e: pg.event.Event) -> bool:
        return self._has_mouse_moved(e)

    def _has_mouse_moved(self, e: pg.event.Event) -> bool:
        m_move_flag = False
        m_pos, m_valid = self._get_event_pos(e)

        if m_valid is True:
            if self._check_mouse_movement(m_pos) is True:
                m_move_flag = True
            m_move_flag = False
        
        return m_move_flag
    
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
        self._parser.set_current_event(event)
        event_valid = self._parser.is_event_valid()
        print(event_valid)
        # If event is valid, assign coords from event
        if event_valid is True:
            coord = self._parser.get_event_pos()
            m_moved = self._check_mouse_movement(coord)
            print("cord: ", coord)
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
        print(action)
        return self._make_action(coord, action)
    
    def _make_action(self, c: Tuple[int, int], a: ActionType):
        assert self._validate_coord(c) == True
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
        e = next(self._event_gen)
        self._parser.set_current_event(e)
        return e

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
    
    def _validate_coord(self, coord: Tuple[int, int]) -> bool:
        if( not isinstance(coord, tuple) or
            len(coord) != 2 or
            not isinstance(coord[0], int) or
            not isinstance(coord[1], int)
            ):
            return False
        return True
    
    class EventParser():

        def __init__(self, config: EventHandler.EventConfig):
            self.config = config
            
            self.event: pg.event.Event            
            return
        
        def validate_event(self, e: pg.event.Event) -> bool:
            return isinstance(e, pg.event.Event)
        
        def set_current_event(self, e: pg.event.Event):
            self.event = e
            
        def get_event_type(self) -> int:
            return self.event.type
        
        
        def get_event_pos(self)-> Tuple[Tuple[int, int], bool]:
            """
                :param self: EventHandler
                :param e: pygame event object. May or may not contain pos, see return type
                :type e: pg.event.Event
                :return: If e.pos exists, return pos and True, otherwise (-1, -1), False
                :rtype: Tuple[Tuple[int, int], bool]
            """
            try:
                return self.event.pos, True # type: ignore
            except AttributeError as err:
                return (-1, -1), False
            except Exception as err:
                print(err)
                exit(1)
        
        def is_event_valid(self) -> bool:
            if self.event is None:
                return False
            return self.get_event_type() in self.config.valid_events

        
        
    # class 
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