from turtle import left
import pygame
from utils import Vector2
from sys import exit
from random import randint
from typing import List

import socket
from time import sleep
from threading import Thread

"""
TODO: Ship placement update
TODO: Better name for grid and otherGrid
TODO: Make the ship dragging mechanic drag in steps

TODO: Game testing

"""

pygame.init()
width, height = (1210, 600)
screen = pygame.display.set_mode((width, height))
clock = pygame.time.Clock()

# colors
EMPTY = (160, 193, 217) # 0
BOAT = (79, 78, 77) # 1
HIT = (217, 84, 54) # 2
MISS = (114, 129, 140) # 3

# networking
FORMAT = 'utf-8'
HOST = '127.0.0.1'
PORT = 5050
ADDR = (HOST, PORT)
DISCONNECT = "!dDd"

# map stuff
mapSize = 10 #int(width/GRIDSIZE) # always a square grid!
GRIDSIZE = 60 # 8x8
screenOffset = Vector2(mapSize * GRIDSIZE + 10, 0)

grid = [] # the side where you edit the ships
otherGrid = [] # the side where you attack (see your attacks)

isRunning = True
canEdit = True # will change if game starts
isTurn = False
isFinished = None

selectedIndex: int = None # index can be 0, has to do with the boat-dragging mechanic

def blancMap():
    _g = []
    for y in range(mapSize):
        for x in range(mapSize):
            _g.append(0)
    return _g
grid = blancMap()
otherGrid = blancMap()

class Boat():
    def __init__(self, position: Vector2, dimensions: Vector2):
        self.pos = position
        self.oldPos = Vector2(position.x, position.y)

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
        t1 = startCheck if not str(startCheck+1)[0] > str(startCheck)[0] and len(str(startCheck)) >= len(str(startCheck+1)) else -1

        yLow = startCheck + (mapSize* (1+self.normDim.y))
        l1 = yLow if str(yLow+1)[0] == str(yLow)[0] and yLow < mapSize**2 else -1

        checkCoords.append(t1)
        checkCoords.append(l1)

        for y in range(0, self.normDim.y+1):
            for x in range(0, self.normDim.x+1):
                checkCoords.append(startCheck+1+x if str(startCheck+1)[0] == str(startCheck+1+x)[0] and len(str(startCheck+1+x)) >= len(str(startCheck+1)) else -1)# right most upper check
                checkCoords.append(yLow+1+x if str(yLow+1)[0] == str(yLow+1+x)[0] and yLow+1+x < mapSize**2 else -1) # right most lower check

            leftCheck = startCheck + (mapSize*y)
            checkCoords.append(leftCheck if str(leftCheck+1)[0] == str(leftCheck)[0] else -1) # left side check

            rightCheck = startCheck + (mapSize*y)+self.normDim.x+1
            checkCoords.append(rightCheck if str(rightCheck-1)[0] == str(rightCheck)[0] else -1) # right side check


        for i in range(len(checkCoords)):
            if checkCoords[i] == -1 or checkCoords[i] == mapSize**2:
                continue

            #print(grid[checkCoords[i]])
            
            if grid[checkCoords[i]] == 1:
                self.pos = Vector2(self.oldPos.x, self.oldPos.y)
                grid = blancMap()

                for boat in boats:
                    boat.addToGrid()
                return True

        self.oldPos = Vector2(self.pos.x, self.pos.y)
        return False

    def draw(self):
        self.rect = pygame.Rect(self.pos.x-1, self.pos.y-1, self.dim.x, self.dim.y)
        pygame.draw.rect(screen, BOAT, self.rect)

    def addToGrid(self):
        # all boats must be placed
        for y in range(self.normDim.y):
            for x in range(self.normDim.x):
                pX = (self.pos.x + (75*x))
                pY = (self.pos.y + (75*y))

                square = min(int(pY/GRIDSIZE) * mapSize + int(pX/GRIDSIZE), mapSize**2-1)
                grid[square] = 1

# instantiation of the boats
boats: List[Boat] = []
"""for i in range(5):
    x, y = randint(0, mapSize-1) * GRIDSIZE, randint(0, mapSize-2) * GRIDSIZE
    Boat(Vector2(x, y), Vector2(1, randint(1,4)))"""

Boat(Vector2(60, 60), Vector2(2, 1))
Boat(Vector2(180, 60), Vector2(2, 1))


for boat in boats:
    boat.addToGrid()


def draw():
    for y in range(mapSize):
        for x in range(mapSize):
            square = y * mapSize + x

            # empty slot
            if(grid[square] == 0):
                pygame.draw.rect(screen, EMPTY, (x * GRIDSIZE, y * GRIDSIZE + screenOffset.y, GRIDSIZE - 2, GRIDSIZE - 2))
            elif(grid[square] == 1):
                #? boat is drawn two times, here and in down in the dedicated for loop
                pygame.draw.rect(screen, BOAT, (x * GRIDSIZE, y * GRIDSIZE + screenOffset.y, GRIDSIZE, GRIDSIZE))
            elif(grid[square] == 2):
                pygame.draw.rect(screen, HIT, (x * GRIDSIZE, y * GRIDSIZE + screenOffset.y, GRIDSIZE - 2, GRIDSIZE - 2))
            elif(grid[square] == 3):
                pygame.draw.rect(screen, MISS, (x * GRIDSIZE, y * GRIDSIZE + screenOffset.y, GRIDSIZE - 2, GRIDSIZE - 2))

    for y in range(mapSize):
        for x in range(mapSize):
            square = y * mapSize + x

            # empty slot
            if(otherGrid[square] == 0):
                pygame.draw.rect(screen, EMPTY, (x * GRIDSIZE + screenOffset.x, y * GRIDSIZE + screenOffset.y, GRIDSIZE - 2, GRIDSIZE - 2))
            elif(otherGrid[square] == 2):
                pygame.draw.rect(screen, HIT, (x * GRIDSIZE + screenOffset.x, y * GRIDSIZE + screenOffset.y, GRIDSIZE - 2, GRIDSIZE - 2))
            elif(otherGrid[square] == 3):
                pygame.draw.rect(screen, MISS, (x * GRIDSIZE + screenOffset.x, y * GRIDSIZE + screenOffset.y, GRIDSIZE - 2, GRIDSIZE - 2))


    if canEdit:
        for boat in boats:
            boat.draw()

# placing boats
while canEdit:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            isRunning = False
            canEdit = False

        elif event.type == pygame.KEYDOWN:
            # confirm you loadout
            if event.key == pygame.K_SPACE:
                grid = blancMap()
                for i, boat in enumerate(boats):
                    boat.addToGrid()
                canEdit = False

        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                for i, boat in enumerate(boats):
                    if boat.rect.collidepoint(event.pos):
                        grid = blancMap()
                        selectedIndex = i
                        x = boat.pos.x - event.pos[0]
                        y = boat.pos.y - event.pos[1]
                        offset: Vector2 = Vector2(x, y)

            if selectedIndex == None: continue
            
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

    pygame.display.update()

# client init and server connection setup
if isRunning:
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(ADDR)

    x = [str(int) for int in grid]
    msg = ",".join(x)
    client.send(msg.encode(FORMAT))

received = ""

def starPattern(lel: list, s: int, kenek: list = None):
    l = max(s-1, 0)
    r = min(s+1, mapSize**2-1)
    u = max(s-mapSize, 0)
    d = min(s+mapSize, mapSize**2-1)

    if kenek != None:
        lel[l] = int(kenek[0]) if int(kenek[0]) != 1 else 0
        lel[r] = int(kenek[1]) if int(kenek[1]) != 1 else 0
        lel[u] = int(kenek[2]) if int(kenek[2]) != 1 else 0
        lel[d] = int(kenek[3]) if int(kenek[3]) != 1 else 0
        return

    if s % mapSize != 0:
        if lel[l] != 1 and lel[l] != 2:
            lel[l] = 3
    if s % mapSize != mapSize-1:
        if lel[r] != 1 and lel[r] != 2:
            lel[r] = 3
    
    if lel[u] != 1 and lel[u] != 2:
        lel[u] = 3

    if lel[d] != 1 and lel[d] != 2:
        lel[d] = 3


def recv():
    global received, isTurn, isFinished, isRunning
    startMsg = client.recv(2).decode(FORMAT)
    isTurn = bool(int(startMsg[1]))
    print(f"start message recved! my turn: {isTurn}!")

    while isRunning:
        received = client.recv(8).decode(FORMAT)
        if len(received) < 3:
            continue

        if received.startswith("!"):
            if received == DISCONNECT:
                isRunning = False
                isTurn = False
                isFinished = False
                print("Force close!")
                break
        
        # end of game, win/loose
        # 2{playerIndex}{bool: didWin}
        if int(received[0]) > 1:
            isTurn = False
            isFinished = True
            t = int(received[2])
            print(f"Game finished! You {'won' if t==1 else 'lost'}!")
            break

        isTurn = bool(int(received[0]))
        square = int(received[1:3])
        isHit = bool(int(received[3]))

        # if hit a boat (handled on the server) grid slot is a 2
        if isTurn == 0:
            # this is called right after your turn
            #? check around the hit point and mark the other spots, like in the browser game
            otherStarSquares = received[4:]
            otherGrid[square] = 2 if isHit == True else 3
            if isHit:
                starPattern(otherGrid, square, list(otherStarSquares))
        else:
            grid[square] = 2 if isHit == True else 3
            if isHit:
                starPattern(grid, square)

# init the receive thread
if isRunning:
    recvThread = Thread(target=recv)
    recvThread.start()
    #grid = blancMap()

# actual attacking draw your attacks
while isRunning:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            isTurn = False
            isRunning = False
            canEdit = False
            client.send(DISCONNECT.encode(FORMAT))

        elif event.type == pygame.MOUSEBUTTONDOWN:
            if(event.pos[0] < screenOffset.x): continue

            # on the right side
            square = int(event.pos[1]/GRIDSIZE) * mapSize + int(max(event.pos[0]-600, 0)/GRIDSIZE)
            #square = min(square, mapSize**2-1)

            if otherGrid[square] == 2 or otherGrid[square] == 3: continue # not click on hit positions

            msg = "%02d" % (square,) # convert the clicked position to a 2 digit integer

            if isTurn:
                client.send(msg.encode(FORMAT))
                isTurn = False

    screen.fill((0, 0, 0)) #(160, 193, 217)
    draw()

    pygame.display.update()


sleep(0.2)
pygame.quit()
exit()



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