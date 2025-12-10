import pygame as pg
from typing import Tuple
from .eventState import State
from .eventConfig import EventConfig
from .eventEnums import ActionType, MouseButtons, Mode

class EventParser():
        """
            Defines the parsing. Essentially, parse event to an action. 
        """
        def __init__(self, config: EventConfig, s: State):
            self.config = config
            
            self._event_to_func_map = dict()
            self._init_event_to_func_map()
            
            self.e: pg.event.Event
            self.state: State = s
            return
        
        """
            Event types from System:
                QUIT              none -> Just exit game
                ACTIVEEVENT       gain, state
                KEYDOWN           key, mod, unicode, scancode -> _parse_key_down
                KEYUP             key, mod, unicode, scancode -> _parse_key_up
                MOUSEMOTION       pos, rel, buttons, touch -> Ignore for right now
                MOUSEBUTTONUP     pos, button, touch -> _parse_mouse_up
                MOUSEBUTTONDOWN   pos, button, touch -> _parse_mouse_down

            Window Events
                WINDOWENTER            Mouse entered the window
                WINDOWLEAVE            Mouse left the window
        """
        def _init_event_to_func_map(self):
            self._event_to_func_map = {
                pg.MOUSEBUTTONDOWN: self._mouse_down,
                pg.MOUSEBUTTONUP: self._mouse_up,
                pg.QUIT: self._exit,
                pg.WINDOWCLOSE: self._exit,
                pg.KEYDOWN: self._key_down,
                pg.KEYUP: self._key_up,
                pg.WINDOWENTER: self._window_enter,
                pg.WINDOWLEAVE: self._window_leave
            }

            for m in self._event_to_func_map:
                assert m in self.config.events_allowed
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

        def get_action_from_event(self) -> ActionType:
            return self._event_to_func_map[self.event.type]()
    
        def _parse_left_mouse_down(self) -> ActionType:
            assert not self.state.left_button
            self.state.left_button = True
            return ActionType.DRAG

        def _parse_right_mouse_down(self) -> ActionType:
            assert not self.state.right_button
            self.state.right_button = True
            return ActionType.DRAG

        def _mouse_down(self) -> ActionType:
            at: ActionType = ActionType.NONE

            # Exclude middle mouse for now!
            if self.event.button in self.config.mouse_buttons:
                if self.event.button == pg.BUTTON_LEFT:
                    at = self._parse_left_mouse_down()
                elif self.event.button == pg.BUTTON_RIGHT:
                    at =  self._parse_right_mouse_down()

                self.state.mode = Mode.DRAG
                self.state.pos = self.event.pos
                
            return at
        
        def _parse_left_mouse_up(self) -> ActionType:
            assert self.state.left_button
            self.state.left_button = False
            return ActionType.REVEAL

        def _parse_right_mouse_up(self) -> ActionType:
            assert self.state.right_button
            self.state.right_button = False
            return ActionType.FLAG

        def _mouse_up(self) -> ActionType:
            at: ActionType = ActionType.NONE

            if self.event.button in self.config.mouse_buttons:
                if self.event.button == pg.BUTTON_LEFT:
                    at = self._parse_left_mouse_up()
                elif self.event.button == pg.BUTTON_RIGHT:
                    at =  self._parse_right_mouse_up()

                self.state.pos = self.event.pos
                self.state.mode = Mode.DRAG if self.state._mouse_down else Mode.NONE

            return at
        
        def _window_enter(self) -> ActionType:
            # Update mouse state. Depending on state of previous mouse,
            #   If mouse if pressed down, then we go into drag.
            #   Otherwise, we do nothing
            self.state.on_screen = True
            return ActionType.NONE

        def _window_leave(self) -> ActionType:
            self.state.on_screen = False
            return ActionType.NONE

        def _exit(self) -> ActionType:
            return ActionType.QUIT
        
        def is_event_valid(self) -> bool:
            if self.event is None:
                return False
            return self.get_event_type() in self.config.events_allowed
        
        def _key_down(self) -> ActionType:
            return ActionType.NONE
        
        def _key_up(self) -> ActionType:
            return ActionType.NONE