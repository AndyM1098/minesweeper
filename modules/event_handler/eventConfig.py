from typing import Tuple, Set, Dict, Callable, MutableSequence, SupportsInt
from .eventEnums import EventType
import pygame as pg



class EventConfig():

    def __init__(self,):
        self._events_allowed: MutableSequence[SupportsInt] = [pg.MOUSEBUTTONDOWN,
                                                              pg.MOUSEBUTTONUP,
                                                              pg.QUIT,
                                                              pg.KEYDOWN,
                                                              pg.KEYUP,
                                                              pg.WINDOWENTER,
                                                              pg.WINDOWLEAVE,
                                                              pg.WINDOWCLOSE]
        print("Setting events allowed")
        pg.event.set_allowed(self._events_allowed)
        pg.event.set_blocked(pg.MOUSEMOTION)
        self.mouse_buttons = [pg.BUTTON_LEFT, pg.BUTTON_RIGHT]
        
        return
    
    @property
    def events_allowed(self) -> MutableSequence[SupportsInt]:
        return self._events_allowed

    @events_allowed.setter
    def events_allowed(self, value: MutableSequence[SupportsInt]):
        self._events_allowed = value
        pg.event.set_allowed(self._events_allowed)
        return
