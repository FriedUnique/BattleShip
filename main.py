import pygame
from pygame.locals import *
from utils import Vector2
from sys import exit
from random import randint

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
GRIDSIZE = 75 # 8x8
mapSize = 8 #int(width/GRIDSIZE) # always a square grid!
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
        self.oldPos = Vector2(75, 75)
        self.dim = dimensions*GRIDSIZE
        self.normDim = dimensions
        
        self.rect = pygame.Rect(self.pos.x-1, self.pos.y-1, self.dim.x, self.dim.y)
        boats.append(self)

    def rotate(self):
        self.dim.switch()
        self.normDim.switch()

    def checkInBounds(self, _x, _y):
        for y in range(self.normDim.y):
            for x in range(self.normDim.x):
                pX = (self.pos.x + (75*x))
                pY = (self.pos.y + (75*y))

                if((_x+(75*x)+1) >= width):
                    return False
                elif((_y+(75*y)+1) >= height):
                    return False

        return True

    def draw(self):
        self.rect = pygame.Rect(self.pos.x-1, self.pos.y-1, self.dim.x, self.dim.y)
        pygame.draw.rect(screen, BOAT, self.rect)

    def addToGrid(self):
        # all boats must be placed
        pX, pY = 0, 0
        for y in range(self.normDim.y):
            for x in range(self.normDim.x):
                pX = (self.pos.x + (75*x))
                pY = (self.pos.y + (75*y))

                square = int(pY/GRIDSIZE) * mapSize + int(pX/GRIDSIZE)
                print(square)
                grid[square] = 1

# instantiation of the boats
boats = []
for i in range(2): 
    x, y = randint(0, mapSize-1) * GRIDSIZE, randint(0, mapSize-1) * GRIDSIZE
    Boat(Vector2(x, y), Vector2(1, 2))


def draw():
    for y in range(mapSize):
        for x in range(mapSize):
            square = y * mapSize + x

            # empty slot
            if(grid[square] == 0):
                pygame.draw.rect(screen, EMPTY, (x * GRIDSIZE, y * GRIDSIZE + screenOffset.y, GRIDSIZE - 2, GRIDSIZE - 2))
            elif(grid[square] == 1):
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
                        selectedIndex = i
                        x = boat.pos.x - event.pos[0]
                        y = boat.pos.y - event.pos[1]
                        offset: Vector2 = Vector2(x, y)

            if selectedIndex == None: continue
            
            if event.button == 4 or event.button == 5: boats[selectedIndex].rotate() 

        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                if selectedIndex == None: continue
                selectedIndex = None

            ''' x = min(int(event.pos[0]/GRIDSIZE), mapSize-1) * GRIDSIZE
                y = min(int(event.pos[1]/GRIDSIZE), mapSize-1) * GRIDSIZE

                if boats[selectedIndex].rect.colliderect(pygame.Rect(width, 0, width+100, height + 100)):
                    print("Overlap right")
                    boats[selectedIndex].pos = Vector2(150, 150)
                elif boats[selectedIndex].rect.colliderect(pygame.Rect(0, height, width+100, height + 100)):
                    print("Overlap bottom")
                    boats[selectedIndex].pos = Vector2(150, 150)
                else:
                    boats[selectedIndex].pos = Vector2(x, y)
                    boats[selectedIndex].oldPos = Vector2(x, y)'''

        elif event.type == pygame.MOUSEMOTION:
            if selectedIndex is not None: # selected can be '0'
                dimensions: Vector2 = boats[selectedIndex].normDim
                boats[selectedIndex].pos.y = min(int(event.pos[1]/GRIDSIZE), mapSize-dimensions.y) * GRIDSIZE # y

                #print(boats[selectedIndex].checkBounds())

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
    msg = msg[:-2]
    client.send(msg.encode(FORMAT))

received = ""

def starPattern(lel: list, s: int):
    l = max(s-1, 0)
    r = min(s+1, mapSize**2-1) 
    u = max(s-mapSize, 0)
    d = min(s+mapSize, mapSize**2-1)

    if s % mapSize != 0:
        lel[l] = 3 if lel[l] != 1 else 2
    if s % mapSize != mapSize-1:
        lel[r] = 3 if lel[r] != 1 else 2
    
    lel[u] = 3 if lel[u] != 1 else 2
    lel[d] = 3 if lel[d] != 1 else 2

def recv():
    global received, isTurn, isFinished, isRunning
    startMsg = client.recv(2).decode(FORMAT)
    isTurn = bool(int(startMsg[1]))
    print(f"start message recved! my turn: {isTurn}!")

    while isRunning:
        received = client.recv(4).decode(FORMAT)
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
            #? check around the hit point and mark the other spots, like in the browser game
            otherGrid[square] = 2 if isHit == True else 3
            if isHit:
                starPattern(otherGrid, square)
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