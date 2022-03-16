from utils import GameObject, Vector2, roundTupleValues

import pygame
from enum import Enum

pygame.init()


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

