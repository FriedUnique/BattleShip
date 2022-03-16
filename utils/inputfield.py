from utils import GameObject, Vector2

import pygame
import pyperclip
from enum import Enum
from typing import List

pygame.init()

def COPY(event):
    return event.key == pygame.K_c and pygame.key.get_mods() & pygame.KMOD_CTRL

def PASTE(event):
    return event.key == pygame.K_v and pygame.key.get_mods() & pygame.KMOD_CTRL

def BULK_DELETE(event):
    return event.key == pygame.K_BACKSPACE and pygame.key.get_mods() & pygame.KMOD_CTRL


COLOR_INACTIVE = (100, 116, 125)
COLOR_ACTIVE = (0, 0, 0)
FONT = pygame.font.Font(None, 32)

class InputField(GameObject):
    """
    The InputField takes four arguments to describe the InputField.

    onEndEdit -> returns text value

    Scale is in this ctx w and h
    """
    class InputFieldEvents(Enum):
        OnEndEdit = 1
    
    def __init__(self, name = "InputField", position = Vector2(0, 0), scale = Vector2(1, 1), text: str = '', onEndEdit=lambda x: x, maxChrs: int = 16, active=True, font=FONT, notAllowedCharacters: List[str] = []):
        self.color = COLOR_INACTIVE
        self.text = text
        self.textSize = 32
        self.selected = False
        self.maxChrs = maxChrs

        self.notChrs = notAllowedCharacters

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

                    if event.unicode in self.notChrs: return
                    
                    self.text += event.unicode

                self.sprite = FONT.render(self.text, True, self.color)

    def update(self, screen):
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

