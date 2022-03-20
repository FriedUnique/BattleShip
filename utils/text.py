from utils import GameObject, Vector2, Button

import pygame
pygame.init()

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

errorAlpha = 80
errorTextColor = (186, 34, 36)
errorBackground = (100, 245, 67)

class ErrorText(GameObject):
    def __init__(self, sWidth, sHeight):
        self.sDim = (sWidth, sHeight)
        w, h = int(sWidth/2), int(sHeight/2)

        self.text = Text("errorText", Vector2(w, h), color=errorTextColor)
        self.closeButton = Button("acceptErrorButton", Vector2(w, sHeight-50), Vector2(15, 6), onClicked=self.acceptError,
                            text="ok")
        
        self.closeButton.SetActive(False)
        self.text.SetActive(False)

        self.toggled = False

        super().__init__("errorText", None, Vector2(w, h))

    def update(self, _screen):
        if(self.toggled):
            # removed the transparent back
            pygame.draw.rect(_screen, errorBackground, (0, 0, self.sDim[0], self.sDim[1]))
            self.text.draw(_screen)
            self.closeButton.draw(_screen)

            #! important ! if error screen is up, it stops the user from clicking on stuff, including the close button
            self.closeButton.handleEvents(None) # button doesn't use the event anyway

    def acceptError(self, _b):
        # close popup 
        self.toggled = False
        self.text.SetActive(False)
        self.closeButton.SetActive(False)

    def loadError(self, msg: str):
        self.text.SetActive(True)
        self.closeButton.SetActive(True)

        self.text.changeText(msg)
        self.toggled = True


class SplashText(GameObject):
    def __init__(self, sWidth, sHeight):
        self.sDim = (sWidth, sHeight)
        w, h = int(sWidth/2), int(sHeight/2)

        self.text = Text("errorText", Vector2(w, h), color=errorTextColor, active=False, font=pygame.font.Font(None, 40))
        self.closeButton = Button("acceptErrorButton", Vector2(w, sHeight-50), Vector2(15, 6), onClicked=self.accept,
                            text="ok", active=False)

        self.toggled = False
        self.acceptFunction = lambda x: x

        super().__init__("errorText", None, Vector2(w, h))

    def update(self, _screen):
        if(self.toggled):
            # removed the transparent back
            pygame.draw.rect(_screen, (0, 0, 0), (0, 0, self.sDim[0], self.sDim[1]))
            self.text.draw(_screen)
            self.closeButton.draw(_screen)

            #! important ! if error screen is up, it stops the user from clicking on stuff, including the close button
            self.closeButton.handleEvents(None) # button doesn't use the event anyway

    def accept(self, _b):
        # close popup 
        self.acceptFunction()

        self.toggled = False
        self.text.SetActive(False)
        self.closeButton.SetActive(False)

    def loadInfo(self, msg: str, bText: str, f = lambda x: x):
        self.acceptFunction = f
        bTextLen = pygame.font.Font(None, 40).size(bText)[0]
        self.closeButton.changeText(bText)
        self.closeButton.scale = Vector2(int(bTextLen/10)+5, 6)
        self.closeButton.SetActive(True)

        self.text.changeText(msg)
        self.text.SetActive(True)
        self.toggled = True

