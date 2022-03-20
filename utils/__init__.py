from .base import GameObject, Vector2
from .base import roundTupleValues, starPattern
from .base import specialMessages, MAPSIZE

from .button import Button
from .inputfield import InputField
from .text import Text, SplashText, ErrorText


"""


def starPattern(_grid: list, s: int):
    l = max(s-1, 0)
    r = min(s+1, mapSize**2-1)
    u = max(s-mapSize, 0)
    d = min(s+mapSize, mapSize**2-1)

    if s % mapSize != 0:
        if _grid[l] != 1 and _grid[l] != 2:
            _grid[l] = 3
    if s % mapSize != mapSize-1:
        if _grid[r] != 1 and _grid[r] != 2:
            _grid[r] = 3
    
    if _grid[u] != 1 and _grid[u] != 2:
        _grid[u] = 3

    if _grid[d] != 1 and _grid[d] != 2:
        _grid[d] = 3
    
    return [str(_grid[l]), str(_grid[r]), str(_grid[u]), str(_grid[d])] # 4

"""