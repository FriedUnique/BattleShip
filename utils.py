import math
from abc import abstractmethod
from typing import List, Dict
from enum import Enum
import pygame

import pyperclip

gridSize = 60
mapSize = 8

DISCONNECT = "!dDd"
SURRENDER = "!gGg"
CONN_TEST = "#"

COLOR_INACTIVE = (100, 116, 125)
COLOR_ACTIVE = (0, 0, 0)


def COPY(event):
    return event.key == pygame.K_c and pygame.key.get_mods() & pygame.KMOD_CTRL

def PASTE(event):
    return event.key == pygame.K_v and pygame.key.get_mods() & pygame.KMOD_CTRL

def BULK_DELETE(event):
    return event.key == pygame.K_BACKSPACE and pygame.key.get_mods() & pygame.KMOD_CTRL


specialMessages = {
    "disconnect": DISCONNECT,
    "surrender": SURRENDER,
    "connection test": CONN_TEST
}




pygame.init()
FONT = pygame.font.Font(None, 32)

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
    def update(self, dt: float):
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

    
    def UpdateAll():
        gos = list(allGOs.values())
        for go in gos:
            if(not go.isActive): continue
            go.update(0)

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

class Text(GameObject):
    def __init__(self, name="TextField", position = Vector2(0, 0), color = (255, 255, 255), font = pygame.font.Font(None, 32), text = "", active=True):
        self.text = text
        self.color = color
        self.font = font

        txt_surface = font.render(self.text, True, self.color) #change

        super().__init__(name, txt_surface, position, active=active)

    def draw(self, surface):
        surface.blit(self.sprite, self.rect) #blit a image
    
    def changeText(self, newText: str):
        self.text = newText
        self.sprite = self.font.render(self.text, True, self.color) #change
        self.rect = self.sprite.get_rect(center=(self.position.x, self.position.y))

class Button(GameObject):
    """
    Rect will be constructed around the position provided
    """
    class TextAlignement(Enum):
        TopLeft = 1
        TopMiddle = 2
        TopRight = 3

        CenterLeft = 4
        CenterMiddle = 5
        CenterRight = 6
        BottomLeft = 7
        BottomMiddle = 8
        BottomRight = 9

    class ButtonStates(Enum):
        Idle = 1
        Hover = 2
        Pressing = 3

    class ButtonEvents(Enum):
        """
        OnClick -> Button
        """
        OnClick = 1

    def __init__(self, name = "Button", position = Vector2(0, 0), scale = Vector2(1, 1), 
            text = "Button", textColor = (0, 0, 0), font = pygame.font.Font(None, 32), textAlignment = TextAlignement.CenterMiddle, 
            normalBackground = (255, 255, 255), onHoverBackground = (220, 230, 235), onPressedBackground = (220, 230, 235), 
            onClicked = lambda x: x, onHover = lambda y: y, active=True):

        position = Vector2(position.x - int(10*scale.x/2), position.y - int(10*scale.y/2))

        self.buttonRect = pygame.Rect((position.x, position.y, 10*scale.x, 10*scale.y))
        self.state: self.ButtonStates = self.ButtonStates.Idle
        self.textColor = textColor
        self.font = font
        self.txt_surface = font.render(text, True, textColor)
        self.ta = textAlignment

        self.textPos = (position.x, position.y)
        
        #customization
        self.text = text
        #? make a dictionary for these values (or list)
        self.normalBackground = normalBackground
        self.onHoverBackground = onHoverBackground
        self.onPressedBackground = onPressedBackground

        super().__init__(name, self.txt_surface, position, scale, active=active)

        # event
        self.onClickEventListeners = list()
        self.AddEventListener(self.ButtonEvents.OnClick, onClicked)

        self.alignText()

    def alignText(self):
        textW, textH = self.font.size(self.text)
        x = self.position.x
        y = self.position.y
        w = self.scale.x*10
        h = self.scale.y*10

        #* Top
        if(self.ta == self.TextAlignement.TopLeft):
            self.textPos = (x, y)
        elif(self.ta == self.TextAlignement.TopMiddle):
            self.textPos = (x + w/2 - textW/2, y)
        elif(self.ta == self.TextAlignement.TopRight):
            self.textPos = (x + textW/2 + 5, y)

        #*Center
        elif(self.ta == self.TextAlignement.CenterLeft):
            self.textPos = (x, y + h/2 - textH/2)
        elif(self.ta == self.TextAlignement.CenterMiddle):
            self.textPos = (x + w/2 - textW/2, y + h/2 - textH/2)
        elif(self.ta == self.TextAlignement.CenterRight):
            self.textPos = (x + textW/2 + 5, y + h/2 - textH/2)

        #*Bottom
        elif(self.ta == self.TextAlignement.BottomLeft):
            self.textPos = (x, y + h - textH)
        elif(self.ta == self.TextAlignement.BottomMiddle):
            self.textPos = (x + w/2 - textW/2, y + h - textH)
        elif(self.ta == self.TextAlignement.BottomRight):
            self.textPos = (x + textW/2 + 5, y + h - textH)

        else:
            raise ValueError(f"{self.ta.name} not implemented yet, or it is a bad type!")

        self.textPos = roundTupleValues(self.textPos)

    def draw(self, surface):
        if(self.state == self.ButtonStates.Idle):
            pygame.draw.rect(surface, self.normalBackground, self.buttonRect)
        elif(self.state == self.ButtonStates.Hover):
            pygame.draw.rect(surface, self.onHoverBackground, self.buttonRect)
        elif(self.state == self.ButtonStates.Pressing):
            pygame.draw.rect(surface, self.onPressedBackground, self.buttonRect)
        else:
            raise ValueError(f"The button-state {self.state.name} is not accepted!")

        surface.blit(self.txt_surface, self.textPos)
    
    def handleEvents(self, event):
        try:
            if pygame.mouse.get_pressed()[0]:
                if self.buttonRect.collidepoint(pygame.mouse.get_pos()):
                    self.state = self.ButtonStates.Pressing
                    #* calling all listeners
                    for listener in self.onClickEventListeners:
                        listener(self) # calls the event Listener with the parameter self

                else:
                    self.state = self.ButtonStates.Idle
            elif not pygame.mouse.get_pressed()[0]:
                if self.buttonRect.collidepoint(pygame.mouse.get_pos()):
                    self.state = self.ButtonStates.Hover
                else:
                    self.state = self.ButtonStates.Idle
        except AttributeError:
            pass
    
    def changeTa(self, alignement: TextAlignement):
        self.ta = alignement
        self.alignText()

    def changeText(self, newText: str):
        self.text = newText
        self.txt_surface = self.font.render(self.text, True, self.textColor)

    def AddEventListener(self, event: ButtonEvents, function):
        if(event == self.ButtonEvents.OnClick):
            self.onClickEventListeners.append(function);
        else:
            raise ValueError("kadlsamlsdklsa")

    def RemoveEventListener(self, event: ButtonEvents, function):
        if(event == self.ButtonEvents.OnClick):
            for i in range(len(self.onClickEventListeners)):
                if(self.onClickEventListeners[i].__name__ == function.__name__):
                    del self.onClickEventListeners[i]
                    break
        else:
            raise ValueError("asdnjsakldsajkldsad")

class InputField(GameObject):
    """
    The InputField takes four arguments to describe the InputField.

    onEndEdit -> returns text value

    Scale is in this ctx w and h
    """
    class InputFieldEvents(Enum):
        OnEndEdit = 1
    
    def __init__(self, name = "InputField", position = Vector2(0, 0), scale = Vector2(1, 1), text: str = '', onEndEdit=lambda x: x, maxChrs: int = 16, active=True, font=FONT):
        self.color = COLOR_INACTIVE
        self.text = text
        self.textSize = 32
        self.selected = False
        self.maxChrs = maxChrs

        super().__init__(name, font.render(text, True, self.color), position, scale, active=active)

        self.rect = pygame.Rect(position.x-10*scale.x, position.y-10*scale.y, 10*scale.x, 10*scale.y)

        self.onEndEditListeners = list()
        self.AddEventListener(self.InputFieldEvents.OnEndEdit, onEndEdit)

    def handleUIEvents(self, event):
        # TODO: Handle the case of crtl + v and ctr + c

        if(not self.isActive): return

        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(pygame.mouse.get_pos()):
                self.selected = not self.selected
            else:
                for listener in self.onEndEditListeners:
                        listener(self.text)
                self.selected = False
                
            self.color = COLOR_ACTIVE if self.selected else COLOR_INACTIVE
        if event.type == pygame.KEYDOWN:
            if self.selected:
                if event.key == pygame.K_RETURN:
                    #* onEndEdit event
                    for listener in self.onEndEditListeners:
                        listener(self.text)

                    #self.text = ''

                elif BULK_DELETE(event): # delete whole words
                    if len(self.text) <= 0: return

                    textList = self.text.split(" ")
                    del textList[len(textList)-1]
                    self.text = " ".join(textList)

                elif event.key == pygame.K_BACKSPACE:
                    self.text = self.text[:-1]

                elif COPY(event):
                    pyperclip.copy(self.text)

                elif PASTE(event):
                    self.text += pyperclip.paste()

                else:
                    if len(self.text) >= self.maxChrs: return
                    
                    self.text += event.unicode

                self.sprite = FONT.render(self.text, True, self.color)

    def update(self, deltaTime):
        # Resize the box if the text is too long.
        width = max(200, self.sprite.get_width()+10)
        self.rect.w = width
        self.sprite = FONT.render(self.text, True, self.color)

    def draw(self, surface):
        surface.blit(self.sprite, (self.rect.x+5, self.rect.y+5))
        pygame.draw.rect(surface, self.color, self.rect, 2)

    def AddEventListener(self, event: InputFieldEvents, function):
        if(event == self.InputFieldEvents.OnEndEdit):
            self.onEndEditListeners.append(function);
        else:
            raise ValueError("kadlsamlsdklsa")

    def RemoveEventListener(self, event: InputFieldEvents, function):
        if(event == self.InputFieldEvents.OnEndEdit):
            for i in range(len(self.onEndEditListeners)):
                if(self.onEndEditListeners[i].__name__ == function.__name__):
                    del self.onEndEditListeners[i]
                    break
        else:
            raise ValueError("asdnjsakldsajkldsad")


def roundTupleValues(t: tuple):
    ts = list(t)
    for i in range(len(ts)):
        ts[i] = round(ts[i])

    return tuple(ts)


allGOs: Dict[str, GameObject] = dict()
allActiveGOs: Dict[str, GameObject] = dict()


"""
    checkCoords: List[int] = [
        max(startCheck, -1),
        max(startCheck + 1, -1),
        max(startCheck + 2, -1),

        square-1 if str(yGridPos)[0] == str(square-1)[0] or len(str(square-1)) == 1 else -1, # have to be on the same line as square
        square+1 if str(yGridPos)[0] == str(square+1)[0] or len(str(square+1)) == 1 else -1,

        min(startCheck + (mapSize*2), mapSize**2),
        min(startCheck + (mapSize*2) + 1, mapSize**2),
        min(startCheck + (mapSize*2) + 2, mapSize**2)
    ]
    #t2 = startCheck + 1 if startCheck + 1 > 0 else -1
    #t3 = startCheck + 2 if str(startCheck+1)[0] == str(startCheck+2)[0] and len(str(startCheck)) >= len(str(startCheck+1)) else -1

    #l2 = yLow + 1 if yLow+1 < mapSize**2 else -1
    #l3 = yLow+2 if str(yLow+1)[0] == str(yLow+2)[0] and yLow+2 < mapSize**2 else -1

    checkCoords.append(startCheck + x if startCheck + x > 0 else -1) # top side check

    bottomCheck = (self.normDim.y+1)*mapSize + startCheck + x
    checkCoords.append(bottomCheck + x if bottomCheck < mapSize**2 else -1) #  bottom
"""