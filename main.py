from math import floor, ceil
import pygame
from utils import Button, GameObject, InputField, Text, Vector2, ErrorText, SplashScreen, specialMessages
from typing import List
import json

import socket
from time import sleep
from threading import Thread
from pyperclip import copy

import sys

saveData: dict = {}
with open('data.json') as data_file:
    saveData = json.load(data_file)


pygame.init()

# region global variable declaration

# map stuff
mapSize = 10 #int(width/GRIDSIZE) # always a square grid!
GRIDSIZE = 50 # min 40
screenOffset = Vector2(mapSize * GRIDSIZE + 10, 0)

width, height = ((mapSize*GRIDSIZE)*2+10, mapSize*GRIDSIZE+100) # 600
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Battle Ship Game.")
clock = pygame.time.Clock()

#alphaSurface = pygame.Surface((width, height), pygame.SRCALPHA)

# colors
EMPTY = (160, 193, 217) # 0
BOAT = (79, 78, 77) # 1
HIT = (217, 84, 54) # 2
MISS = (114, 129, 140) # 3

BLACK = (0, 0, 0)
menuColor = (145, 149, 156)

fontSize = 38 - ceil(700/height)*2


# networking
FORMAT = 'utf-8'
HOST = '127.0.0.1'
PORT = 5050
ADDR = (HOST, PORT)

ROOM_LINK = saveData["inviteLink"]
ROOM_NAME = saveData["roomName"]
USER = saveData["playerName"]

pygame.display.set_caption(f"Battle Ship Game. [USERNAME]: {USER}")

DISCONNECT = specialMessages["disconnect"]
SURRENDER = specialMessages["surrender"]
CONN_TEST = specialMessages["connection test"]

def blancMap():
    return [0] * (mapSize**2)

def save():
    global ROOM_LINK, ROOM_NAME, USER, GRIDSIZE
    
    if joinMethod == "j":
        saveData["inviteLink"] = roomInputField.text
        ROOM_LINK = saveData["inviteLink"]
    elif joinMethod == "c":
        saveData["roomName"] = roomInputField.text
        ROOM_NAME = saveData["roomName"]
    

    saveData["playerName"] = usernameInputField.text
    USER = saveData["playerName"]

    l = []
    for boat in boats:
        l.append([int(boat.pos.x/GRIDSIZE), int(boat.pos.y/GRIDSIZE), int(boat.normDim.x), int(boat.normDim.y)])
    saveData[f"boats{mapSize}"] = list(l)

    with open('data.json', 'w') as outfile:
        json.dump(saveData, outfile)


def testConnection():
    try:
        client.send(CONN_TEST.encode(FORMAT))
    except:
        return False

    return True


grid = blancMap()
otherGrid = blancMap()

isRunning = True
canEdit = True # will change if game starts
isTurn = False
isFinished = None
menu = True

selectedIndex: int = None # index can be 0, has to do with the boat-dragging mechanic
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
joinMethod = ""

# endregion

class Boat():
    def __init__(self, position: Vector2, dimensions: Vector2):
        pos = Vector2(floor(position.x/GRIDSIZE)*GRIDSIZE, floor(position.y/GRIDSIZE)*GRIDSIZE) # so the boats end up in a good square
        self.pos = pos
        self.oldPos = Vector2(pos.x, pos.y)

        dimensions = Vector2(int(dimensions.x), int(dimensions.y))
        self.dim = dimensions*GRIDSIZE
        self.normDim = dimensions
        
        self.rect = pygame.Rect(self.pos.x-1, self.pos.y-1, self.dim.x, self.dim.y)
        boats.append(self)

    def rotate(self):
        self.dim.switch()
        self.normDim.switch()

    def check(self):
        global grid
        checkCoords = []
        square = int(self.pos.y/GRIDSIZE) * mapSize + int(self.pos.x/GRIDSIZE)
        startCheck = square - mapSize - 1

        # top, grid skipping
        """if not len(str(yLow)) > 1:
            t1 = startCheck if not str(startCheck+1)[0] > str(startCheck)[0] and len(str(startCheck)) >= len(str(startCheck+1)) else -1
        else:
            t1 = startCheck if not str(startCheck+1)[0] > str(startCheck)[0] and len(str(startCheck)) >= len(str(startCheck+1)) else -1"""
        t1 = startCheck if len(str(startCheck)) >= len(str(startCheck+1)) else -1

        yLow = startCheck + (mapSize* (1+self.normDim.y))
        if not len(str(yLow)) > 1:
            l1 = yLow if yLow < mapSize**2 else -1
        else:
            l1 = yLow if str(yLow+1)[0] == str(yLow)[0] and yLow < mapSize**2 else -1

        checkCoords.append(t1)
        checkCoords.append(l1)

        for y in range(self.normDim.y):
            for x in range(self.normDim.x):
                pX = (self.pos.x + (GRIDSIZE*x))
                pY = (self.pos.y + (GRIDSIZE*y))

                s = min(int(pY/GRIDSIZE) * mapSize + int(pX/GRIDSIZE), mapSize**2-1)
                checkCoords.append(s)

        for y in range(0, self.normDim.y+1):
            for x in range(0, self.normDim.x+1):
                checkCoords.append(startCheck+1+x if len(str(startCheck+1+x)) >= len(str(startCheck+1)) else -1)# right most upper check
                checkCoords.append(yLow+1+x if yLow+1+x < mapSize**2 else -1) # right most lower check

            leftCheck = startCheck + (mapSize*y)
            if not len(str(leftCheck)) > 1:
                checkCoords.append(leftCheck) # left side check
            else:
                checkCoords.append(leftCheck if str(leftCheck+1)[0] == str(leftCheck)[0] else -1)


            rightCheck = startCheck + (mapSize*y)+self.normDim.x+1
            if not len(str(rightCheck)) > 1:
                checkCoords.append(rightCheck)
            else:
                checkCoords.append(rightCheck if str(rightCheck-1)[0] == str(rightCheck)[0] else -1) # right side check


        for i in range(len(checkCoords)):
            if checkCoords[i] <= -1 or checkCoords[i] >= mapSize**2:
                continue

            grid = blancMap()

            for boat in boats:
                if boat == self: continue
                boat.addToGrid()

            if grid[max(min(checkCoords[i], 100), 0)] == 1:
                self.pos = Vector2(self.oldPos.x, self.oldPos.y)
                grid = blancMap()

                for boat in boats:
                    boat.addToGrid()
                return True

        self.oldPos = Vector2(self.pos.x, self.pos.y)
        self.addToGrid()
        return False

    def draw(self, _screen):
        self.rect = pygame.Rect(self.pos.x-1, self.pos.y-1, self.dim.x, self.dim.y)
        pygame.draw.rect(_screen, BOAT, self.rect)

    def addToGrid(self):
        # all boats must be placed
        for y in range(self.normDim.y):
            for x in range(self.normDim.x):
                pX = (self.pos.x + (GRIDSIZE*x))
                pY = (self.pos.y + (GRIDSIZE*y))

                square = min(int(pY/GRIDSIZE) * mapSize + int(pX/GRIDSIZE), mapSize**2-1)
                grid[square] = 1


errorMsg = ErrorText(width, height)
splashText = SplashScreen(width, height)

boats: List[Boat] = []
# 40: 4*1, 3*2, 2*3
# 50: 4*1, 4*2, 3*3

def fetchBoatData():
    if f"boats{mapSize}" not in saveData:
        searchList = list(saveData.keys())
        searchList.sort()
        if f"boats{mapSize}" > searchList[len(searchList)-1]: 
            print(f"Did not found the correct data for {mapSize}! Using {len(searchList)-1}")
            return searchList[len(searchList)-1]

        for index, key in enumerate(searchList):
            try:
                if key < f"boats{mapSize}" < searchList[index]:
                    return key
            
            except IndexError:
                pass

        return searchList[0]
    else:
        return f"boats{mapSize}"


def genBoats():
    Boat(Vector2(40, 40), Vector2(1, 1)).addToGrid()
    
    """sTerm = fetchBoatData()

    for i in range(len(saveData[sTerm])):
        b = saveData[sTerm][i]
        Boat(Vector2(b[0]*GRIDSIZE, b[1]*GRIDSIZE), Vector2(b[2], b[3]))
    
    for boat in boats:
        boat.addToGrid()"""


if canEdit:
    genBoats()

def n():
    print("engegegegeggege")

# region main menu

def connectClient():
    global client
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        client.connect(ADDR)
        return True
        
    except ConnectionRefusedError:
        print(f"Connection actively refused by host @ {HOST}!")
        errorMsg.loadError(f"Connection actively refused by host @ {HOST}!")
        return False

    except OSError:
        print("OSError")
        return False

def start():
    global menu, roomInputField, usernameInputField
    menu = False
    createButton.SetActive(False)
    quitButton.SetActive(False)
    joinOtherButton.SetActive(False)
    roomInputField.SetActive(False)
    usernameInputField.SetActive(False)
    backToMenu.SetActive(False)
    roomIFDesc.SetActive(False)
    userIFDesc.SetActive(False)

    startButton.SetActive(True)
    youShipsText.SetActive(True)
    otherShipsText.SetActive(True)
    mainMenuButton.SetActive(True)

    save()

def enterNames(active: bool):
    createButton.SetActive(not active)
    quitButton.SetActive(not active)
    joinOtherButton.SetActive(not active)

    if joinMethod == "j":
        roomInputField.text = saveData["inviteLink"]
    elif joinMethod == "c":
        roomInputField.text = saveData["roomName"]

    roomInputField.SetActive(active)
    usernameInputField.SetActive(active)
    continueButton.SetActive(active)
    backToMenu.SetActive(active)
    roomIFDesc.SetActive(active)
    userIFDesc.SetActive(active)

def connectToGame(b: Button):
    global ROOM_LINK, USER, ROOM_NAME, menu, canEdit
    if not connectClient():
        return

    room = roomInputField.text # name or inviteLink
    userName = usernameInputField.text

    if joinMethod == "j" and len(roomInputField.text) < 16:
        errorMsg.loadError("Invite Link has to be 16 chrs long")
        return
    elif joinMethod == "c":
        ROOM_NAME = room

    client.send(f"{joinMethod}{room},{userName}".encode(FORMAT))

    responce = client.recv(2048).decode(FORMAT) # if error, then message is provideds
    if responce.startswith(DISCONNECT):
        errorMsg.loadError(responce[len(DISCONNECT):])
        client.close()
        return

    ROOM_LINK = responce[0:16]
    USER = responce[16:]

    save()

    b.SetActive(False)
    print("Room Name: ", ROOM_LINK)
    copy(ROOM_LINK)

    menu = False
    canEdit = True

    start()


def create(b):
    global joinMethod
    joinMethod = "c"
    enterNames(True)

def join(b):
    global joinMethod
    joinMethod = "j"
    enterNames(True)

def back(b):
    save()
    enterNames(False)
    
def quit(b):
    global isRunning, canEdit, menu
    save()

    isRunning = False
    canEdit = False
    menu = False


# region UI setup

textFont = pygame.font.Font(None, fontSize)
buttonFont = pygame.font.Font(None, fontSize+15)

joinOtherButton = Button("joinOtherButton", Vector2((mapSize*GRIDSIZE)+5, height/6), Vector2(20, 8), "JOIN", font=buttonFont, 
                normalBackground=menuColor, onHoverBackground=(111, 115, 120), onPressedBackground=(63, 66, 69), onClicked=join)

createButton = Button("createButton", Vector2((mapSize*GRIDSIZE)+5, height/6*3), Vector2(20, 8), "CREATE", font=buttonFont, 
                normalBackground=menuColor, onHoverBackground=(111, 115, 120), onPressedBackground=(63, 66, 69), onClicked=create)

quitButton = Button("quitButton", Vector2((mapSize*GRIDSIZE)+5, height/6*5), Vector2(20, 8), "QUIT", font=buttonFont,
                    normalBackground=menuColor, onHoverBackground=(111, 115, 120), onPressedBackground=(63, 66, 69), onClicked=quit)

roomInputField = InputField("roomIF", Vector2((mapSize*GRIDSIZE)+5, height/10*6), scale=Vector2(10, 3.5), maxChrs=16 , active=False, font=textFont, text=saveData["roomName"],
                            notAllowedCharacters=["#", "$", "!", "@"])

usernameInputField = InputField("nameIF", Vector2((mapSize*GRIDSIZE)+5, height/10*8), scale=Vector2(10, 3.5), maxChrs=8, active=False, font=textFont, text=saveData["playerName"],
                        onEndEdit = lambda userNameEntered: pygame.display.set_caption(f"Battle Ship Game. [USERNAME]: {userNameEntered}"),
                        notAllowedCharacters=["#", "$", "!", "@"]) #460 ,560

roomIFDesc = Text("roomIFDesc", Vector2((mapSize*GRIDSIZE)-200, height/10*6-20), BLACK, text="ROOM NAME", active=False, font=textFont)
userIFDesc = Text("userIFDesc", Vector2((mapSize*GRIDSIZE)-200, height/10*8-20), BLACK, text="USER NAME", active=False, font=textFont)


continueButton = Button("continue", Vector2(width-100, height-50), Vector2(18, 8), "continue", font=buttonFont,
                    normalBackground=menuColor, onHoverBackground=(111, 115, 120), onPressedBackground=(63, 66, 69), onClicked=connectToGame, active=False)

backToMenu = Button("back", Vector2(80, height-50), Vector2(15, 8), "back", font=buttonFont,
                    normalBackground=menuColor, onHoverBackground=(111, 115, 120), onPressedBackground=(63, 66, 69), onClicked=back, active=False)

# endregion

def menuLoop():
    global isRunning, canEdit, menu

    while menu:
        clock.tick(30)
        for event in pygame.event.get():
            if not errorMsg.toggled: # so you cant click though the error layer
                GameObject.HandleEventsAll(event)

            if event.type == pygame.QUIT:
                isRunning = False
                canEdit = False
                menu = False

        screen.fill(menuColor)

        GameObject.DrawAll(screen)

        GameObject.UpdateAll(screen)

        pygame.display.update()

# endregion


# region edit the boat loadout

def draw():
    #! improve this function
    for y in range(mapSize):
        for x in range(mapSize):
            square = y * mapSize + x

            # empty slot
            if(grid[square] == 0):
                pygame.draw.rect(screen, EMPTY, (x * GRIDSIZE, y * GRIDSIZE + screenOffset.y, GRIDSIZE - 2, GRIDSIZE - 2))
            elif(grid[square] == 1):
                #? boat is drawn two times, here and in down in the dedicated for loop
                pygame.draw.rect(screen, BOAT, (x * GRIDSIZE, y * GRIDSIZE + screenOffset.y, GRIDSIZE - 2, GRIDSIZE - 2))
            elif(grid[square] == 2):
                pygame.draw.rect(screen, HIT, (x * GRIDSIZE, y * GRIDSIZE + screenOffset.y, GRIDSIZE - 2, GRIDSIZE - 2))
            elif(grid[square] == 3):
                pygame.draw.rect(screen, MISS, (x * GRIDSIZE, y * GRIDSIZE + screenOffset.y, GRIDSIZE - 2, GRIDSIZE - 2))


            # other grid
            if(otherGrid[square] == 0):
                pygame.draw.rect(screen, EMPTY, (x * GRIDSIZE + screenOffset.x, y * GRIDSIZE + screenOffset.y, GRIDSIZE - 2, GRIDSIZE - 2))
            elif(otherGrid[square] == 2):
                pygame.draw.rect(screen, HIT, (x * GRIDSIZE + screenOffset.x, y * GRIDSIZE + screenOffset.y, GRIDSIZE - 2, GRIDSIZE - 2))
            elif(otherGrid[square] == 3):
                pygame.draw.rect(screen, MISS, (x * GRIDSIZE + screenOffset.x, y * GRIDSIZE + screenOffset.y, GRIDSIZE - 2, GRIDSIZE - 2))

    
    pygame.draw.rect(screen, (145, 149, 156), (0, mapSize*GRIDSIZE, width, 100))

    GameObject.DrawAll(screen)

    if canEdit:
        for boat in boats:
            boat.draw(screen)

# listener in the startButton
def startGame(b: Button):
    global grid, canEdit, isRunning, isTurn, client, startButton, menu
    
    try:
        grid = blancMap()
        for boat in boats:
            boat.addToGrid()

        x = [str(int) for int in grid]
        #x = list(map(str, grid))
        msg = ",".join(x)
        client.send(msg.encode(FORMAT))
        startButton.SetActive(False)
        canEdit = False

        copy(ROOM_LINK) # pyperclip.copy()

        recvThread = Thread(target=recv)
        recvThread.start()
        sleep(0.1) # so fully started
        
    except ConnectionRefusedError:
        print(f"Connection actively refused by host @ {HOST}!")
    except Exception as e:
        print(e)

def passToMainMenu(b):
    global canEdit, menu, youShipsText, otherShipsText, grid, otherGrid, isTurn
    menu = True
    canEdit = False
    isTurn = False

    startButton.SetActive(False)
    youShipsText.SetActive(False)
    otherShipsText.SetActive(False)
    turnText.SetActive(False)
    mainMenuButton.SetActive(False)

    grid = blancMap()
    otherGrid = blancMap()

    if testConnection():
        client.send(DISCONNECT.encode(FORMAT))
    client.close() # how to leave the recv thread? through an exception, which will break out of the loop

    enterNames(False)
    sleep(0.1)



x = int((mapSize*GRIDSIZE)/2)
y = mapSize*GRIDSIZE + 50

youShipsText = Text("yShipsText", Vector2(x-75, y-15), text="Your ships", color=(0, 0, 0), font=pygame.font.Font(None, fontSize), active=False)
otherShipsText = Text("otherShipsText", Vector2((mapSize*GRIDSIZE)*1.5+75, y-15), text="Oponent Ships", color=(0, 0, 0), font=pygame.font.Font(None, fontSize), active=False)
startButton = Button("startButton", Vector2(mapSize*GRIDSIZE, y-20), Vector2(10, 4), onClicked=startGame,
            normalBackground=menuColor, onHoverBackground=(111, 115, 120), onPressedBackground=(63, 66, 69), text="START", active=False)

turnText = Text("turnText", Vector2(mapSize*GRIDSIZE, y-15), text="HHHHHHHH TURN", color=(0, 0, 0), font=pygame.font.Font(None, fontSize), active=False)
mainMenuButton = Button("mainMenuButton", Vector2(mapSize*GRIDSIZE, y+25), Vector2(9, 4), text="BACK",
                normalBackground=menuColor, onHoverBackground=(111, 115, 120), onPressedBackground=(63, 66, 69), onClicked=passToMainMenu, active=False)
# placing boats
def editBoats():
    global isRunning, grid, canEdit, selectedIndex, boats, joinButton

    while canEdit:
        clock.tick(30)
        
        for event in pygame.event.get():
            GameObject.HandleEventsAll(event)

            if event.type == pygame.QUIT:
                isRunning = False
                canEdit = False

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:   
                    #print(int(event.pos[0]/GRIDSIZE)*GRIDSIZE, int(event.pos[1]/GRIDSIZE)*GRIDSIZE)
                    for i, boat in enumerate(boats):
                        if boat.rect.collidepoint(event.pos):
                            grid = blancMap()
                            selectedIndex = i
                            x = boat.pos.x - event.pos[0]
                            y = boat.pos.y - event.pos[1]

                if selectedIndex == None: continue

                
                # scroll
                if event.button == 4 or event.button == 5: boats[selectedIndex].rotate() 

            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    if selectedIndex == None: continue
                    for i, boat in enumerate(boats):
                        boat.addToGrid()

                    boats[selectedIndex].check()

                    selectedIndex = None

            elif event.type == pygame.MOUSEMOTION:
                if selectedIndex is not None: # selected can be '0'
                    dimensions: Vector2 = boats[selectedIndex].normDim
                    boats[selectedIndex].pos.y = min(int(event.pos[1]/GRIDSIZE), mapSize-dimensions.y) * GRIDSIZE # y
                    
                    if(event.pos[0] < screenOffset.x):
                        boats[selectedIndex].pos.x = min(int(event.pos[0]/GRIDSIZE), mapSize-dimensions.x) * GRIDSIZE # x


        screen.fill((0, 0, 0)) #(160, 193, 217)
        draw()

        GameObject.UpdateAll(screen)

        pygame.display.update()

# endregion

# region main game loop (communitcation with server)

def starPattern(_grid: list, s: int, starList: list = None):
    l = max(s-1, 0)
    r = min(s+1, mapSize**2-1)
    u = max(s-mapSize, 0)
    d = min(s+mapSize, mapSize**2-1)

    if starList != None:
        _grid[l] = int(starList[0]) if int(starList[0]) != 1 else 0
        _grid[r] = int(starList[1]) if int(starList[1]) != 1 else 0
        _grid[u] = int(starList[2]) if int(starList[2]) != 1 else 0
        _grid[d] = int(starList[3]) if int(starList[3]) != 1 else 0
        return

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


def resetToMenu():
    global menu, canEdit, youShipsText, otherShipsText, grid, otherGrid, isTurn, isFinished
    print("menu time")
    isTurn = False
    menu = True
    isFinished = False

    youShipsText.SetActive(False)
    otherShipsText.SetActive(False)
    turnText.SetActive(False)

    grid = blancMap()
    otherGrid = blancMap()

    if testConnection():
        client.send(DISCONNECT.encode())
    
    sleep(0.1)
    client.close() # should be safe, because it is called after the recv thread is break out of

def recv():
    global isTurn, isFinished, isRunning, grid, otherGrid
    received = ""
    startMsg = ""
    otherPlayerName = ""

    while isRunning:
        try:
            startMsg = client.recv(10).decode(FORMAT)

            if startMsg == DISCONNECT:
                isRunning = False
                isTurn = False
                isFinished = True
                print("Force quit! Press space")
                break

            elif not startMsg.startswith(specialMessages["connection test"]):
                break
        except ConnectionAbortedError:
            #print("Connection aborted")
            pass
        except OSError:
            return # stops the function here


    if isRunning:
        isTurn = bool(int(startMsg[1]))
        name = startMsg[2:]
        turnText.SetActive(True)
        turnText.changeText(f"{'Your' if isTurn==True else name} turn")

    while isRunning:
        try:
            received = client.recv(8+8).decode(FORMAT) # max user name lenght
            #print(received)
            if len(received) < 3:
                continue

            if received.startswith("!"):
                if received == DISCONNECT:
                    isTurn = False
                    isFinished = True
                    print("Disconnect: ", client.recv(1024).decode(FORMAT)) # reason
                    client.close()
                    # go to main menu
                    break
                elif received == SURRENDER:
                    print("surrender")
                    isTurn = False
                    isFinished = True
                    break

            elif received.startswith("#"): # is just for testing the connection
                continue
            
            # end of game, win/loose
            # 2{playerIndex}{bool: didWin}
            if int(received[0]) > 1:
                isWin = int(received[2])
                client.send(DISCONNECT.encode(FORMAT))

                splashText.loadInfo(f"Game finished! {'You won' if isWin==1 else {otherPlayerName, 'won. You lost!'}}!", "back to main menu", lambda: passToMainMenu("a"))

                isFinished = True # in the main loop, the splash screen will be handled
                client.close()
                break

            isTurn = bool(int(received[0]))
            square = int(received[1:3])
            isHit = bool(int(received[3]))

            # if hit a boat (handled on the server) grid slot is a 2
            if isTurn == False:
                # this is called right after your turn
                #? check around the hit point and mark the other spots, like in the browser game
                otherStarSquares = received[4:8]
                otherPlayerName = received[8:]

                otherGrid[square] = 2 if isHit == True else 3
                if isHit:
                    starPattern(otherGrid, square, list(otherStarSquares))

            else:
                grid[square] = 2 if isHit == True else 3
                otherPlayerName = received[4:]
                if isHit:
                    starPattern(grid, square)

            turnText.changeText(f"{'Your' if isTurn==True else received[8:]} turn")
        
        except OSError:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            print(exc_type, exc_tb.tb_lineno)
            #client.close()
            isFinished = True
            break
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            print(e, exc_tb.tb_lineno)


# actual attacking draw your attacks
while isRunning:
    clock.tick(30)

    menuLoop()
    editBoats()

    for event in pygame.event.get():
        if not splashText.toggled:
            GameObject.HandleEventsAll(event)
        
        if event.type == pygame.QUIT:
            isTurn = False
            isRunning = False
            canEdit = False
            client.send(DISCONNECT.encode(FORMAT))
            break

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                pass

        elif event.type == pygame.MOUSEBUTTONDOWN:
            if(event.pos[0] < screenOffset.x): continue

            # on the right side
            #square = max(min(int(event.pos[1]/GRIDSIZE) * mapSize + int(max(event.pos[0]-600, 0)/GRIDSIZE), mapSize**2-1), 0)
            square = max(min(int(event.pos[1]/GRIDSIZE) * mapSize + int(max(event.pos[0]-(mapSize*GRIDSIZE), 0)/GRIDSIZE), mapSize**2-1), 0)
            square = min(square, mapSize**2-1)

            if otherGrid[square] == 2 or otherGrid[square] == 3: continue # not click on hit positions

            msg = "%02d" % (square,) # convert the clicked position to a 2 digit integer

            if isTurn:
                #! error may occure when already disconnected
                client.send(msg.encode(FORMAT))
                isTurn = False

    if not isRunning:
        break

    screen.fill((0, 0, 0)) #(160, 193, 217)
    draw()

    GameObject.UpdateAll(screen)

    pygame.display.update()

# endregion

save()
sleep(0.2)

pygame.quit()

from sys import exit
exit()