from dataclasses import dataclass
from typing import Tuple
from .eventEnums import ActionType

@dataclass(frozen=True, slots=True)
class Action():
    action: ActionType
    coords: Tuple[int, int]

    def __str__(self):
        return f'Action(action={self.action}, coords={self.coords})'