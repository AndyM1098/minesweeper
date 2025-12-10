from typing import List, Tuple
from .eventEnums import Mode

class State:
    """
        Keeps the current state of input.
    """
    def __init__(self):
        
        self._mouse_left_button: bool = False
        self._mouse_right_button: bool = False
        self.button_down = False
        
        self._mouse_pos: Tuple[int] = (0, 0)
        self.on_screen: bool = False # todo implement
        self._mode: Mode = Mode.NONE
        self.restart_pending: bool = False # If r button is down! #todo implement later
    
    @property
    def mode(self):
        return self._mode
    
    @mode.setter
    def mode(self, value: Mode):
        assert isinstance(value, Mode)
        self._mode = value
        return
    

    @property
    def pos(self)-> Tuple[int, int]:
        return self._mouse_pos
    
    @pos.setter
    def pos(self, value: Tuple[int, int]):
        self._mouse_pos = value
        return
    
    @property
    def left_button(self) -> bool:
        return self._mouse_left_button

    @left_button.setter
    def left_button(self, state: bool):
        if not state:
            self._mouse_down = self._mouse_right_button
        else:
            self.button_down = True
        
        self._mouse_left_button = state
        return

    @property
    def right_button(self) -> bool:
        return self._mouse_right_button
    
    @right_button.setter
    def right_button(self, state: bool):
        if not state:
            self._mouse_down = self._mouse_left_button
        else:
            self.button_down = True
        
        self._mouse_right_button = state
        return