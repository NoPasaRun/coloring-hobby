from enum import Enum
from typing import Tuple


class BezierFunctions(Enum):
    ease_in: Tuple = ((.42, 0), (1, 1))
    ease_out: Tuple = ((0, 0), (.58, 1))
    ease_in_out: Tuple = ((.42, 0), (.58, 1))
    stop_in_center: Tuple = ((0, 1), (1, 0))


class States(Enum):
    menu: int = 0
    level: int = 1
