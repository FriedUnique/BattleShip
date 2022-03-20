import math
from abc import abstractmethod
from typing import Dict
import pygame

pygame.init()
FONT = pygame.font.Font(None, 32)

DISCONNECT = "!dDd"
SURRENDER = "!gGg"
CONN_TEST = "#"

MAPSIZE = 10

specialMessages = {
    "disconnect": DISCONNECT,
    "surrender": SURRENDER,
    "connection test": CONN_TEST
}

class Vector2:    
    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y

    def __add__(self, other):
        if isinstance(other, self.__class__):
            return Vector2(self.x + other.x, self.y + self.y)
        return Vector2(self.x + other, self.y + other)
    
    def __sub__(self, other):
        if isinstance(other, self.__class__):
            return Vector2(self.x - other.x, self.y - self.y)
        return Vector2(self.x - other, self.y - other)
    
    def __mul__(self, other):
        if isinstance(other, self.__class__):
            return Vector2(self.x * other.x, self.y * self.y)
        return Vector2(self.x * other, self.y * other)

    def __truediv__(self, other):
        if isinstance(other, self.__class__):
            return Vector2(self.x / other.x, self.y / self.y)
        return Vector2(self.x / other, self.y / other)

    def switch(self):
        x = self.x
        self.x = self.y
        self.y = x


    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.x == other.x and self.x == other.y
        return self.x == other, self.y == other

    def __neg__(self):
        return -self.x, -self.y

    def __str__(self): # returns a value when this class is printed
        return f"(x: {self.x}, y: {self.y})"



    def Dot(vec1, vec2):
        return vec1.x * vec2.x + vec1.y * vec2.y

    def sqrLenght(vec):
        return vec.x**2 + vec.y**2

    def sqrDist(vec1, vec2):
        v = vec1 - vec2
        return v.x**2 + v.y**2

    def lenght(vec):
        return math.sqrt(vec.x**2 + vec.y**2)

    def distance(vec1, vec2):
        v = vec1 - vec2
        return math.sqrt(v.x**2 + v.y**2)

    def normalize(vec):
        vecLen = Vector2.lenght(vec)
        return Vector2(vec.x/vecLen, vec.y/vecLen)

    def negative(vec):
        return Vector2(-vec.x, -vec.y)

    def right(vec):
        return Vector2(-vec.y, vec.x)

    def angle_between_vec(vec1, vec2):
        return math.acos(Vector2.Dot(vec1, vec2))


class GameObject:
    def __init__(self, name, goSprite, position: Vector2 = (10, 10), scale = Vector2(1, 1), active = True):
        self.name = self.nameing(name)
        self.sprite = goSprite
        self.position: Vector2 = position
        self.scale: Vector2 = scale

        if self.sprite != None:
            self.rect = self.sprite.get_rect(center=(position.x, position.y)) #topleft
        else:
            self.rect = pygame.Rect(self.position.x, self.position.y, self.scale.x, self.scale.y)

        self.isActive = active

    def nameing(self, targetName) -> str:
        allVals = list(allGOs.keys())
        targetLen = len(targetName)

        count = 0
        for i in range(len(allVals)):
            if(allVals[i][:targetLen] == targetName):
                count += 1
        
        if(count > 0):
            n = targetName + f"{count}"
            allGOs[n] = self
            return n
            #print(f'Warning! GameObject "{targetName}" has been instantiated with a already existing name. The name changed to {n}!')
        else:
            allGOs[targetName] = self
            return targetName

    def SetActive(self, activate):
        self.isActive = activate        

    def Destroy(self, time: float = 0):
        if self.name in allGOs:
            del allGOs[self.name]
            del self

    @abstractmethod
    def update(self, screen):
        pass

    @abstractmethod
    def handleUIEvents(self, event):
        pass

    @abstractmethod
    def draw(self, surface):
        pass

    @abstractmethod
    def handleEvents(self, event):
        pass

    def Find(name: str):
        if name in allGOs:
            return allGOs[name]
        else:
            print(f"Provided value does not exist ({name})!")
            return None

    
    def UpdateAll(_screen):
        gos = list(allGOs.values())
        for go in gos:
            if(not go.isActive): continue
            go.update(_screen)

    def HandleEventsAll(event):
        gos = list(allGOs.values())
        for go in gos:
            if(not go.isActive): continue
            go.handleEvents(event)
            go.handleUIEvents(event)

    def DrawAll(s):
        gos = list(allGOs.values())
        for go in gos:
            if(not go.isActive): continue
            go.draw(s)


def roundTupleValues(t: tuple):
    ts = list(t)
    for i in range(len(ts)):
        ts[i] = round(ts[i])

    return tuple(ts)

allGOs: Dict[str, GameObject] = dict()
allActiveGOs: Dict[str, GameObject] = dict()

def starPattern(_grid: list, s: int, starList: list = None):
    l = max(s-1, 0)
    r = min(s+1, MAPSIZE**2-1)
    u = max(s-MAPSIZE, 0)
    d = min(s+MAPSIZE, MAPSIZE**2-1)

    if starList != None:
        _grid[l] = int(starList[0]) if int(starList[0]) != 1 else 0
        _grid[r] = int(starList[1]) if int(starList[1]) != 1 else 0
        _grid[u] = int(starList[2]) if int(starList[2]) != 1 else 0
        _grid[d] = int(starList[3]) if int(starList[3]) != 1 else 0
        return

    if s % MAPSIZE != 0:
        if _grid[l] != 1 and _grid[l] != 2:
            _grid[l] = 3
    if s % MAPSIZE != MAPSIZE-1:
        if _grid[r] != 1 and _grid[r] != 2:
            _grid[r] = 3
    
    if _grid[u] != 1 and _grid[u] != 2:
        _grid[u] = 3

    if _grid[d] != 1 and _grid[d] != 2:
        _grid[d] = 3