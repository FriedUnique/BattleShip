from typing import List
import pygame, sys
from utils import Vector2

pygame.init()
width, height = (600, 600)
screen = pygame.display.set_mode((width, height))
clock = pygame.time.Clock()

# colors
EMPTY = (160, 193, 217) # 0
BOAT = (79, 78, 77) # 1
HIT = (217, 84, 54) # 2

GRIDSIZE = 75 # 8x8
mapSize = 8 #int(width/GRIDSIZE) # always a square grid!
grid = []

isRunning = True
canEdit = True # will change if game starts

def blancMap():
    global grid
    grid = []
    for y in range(mapSize):
        for x in range(mapSize):
            grid.append(0)
blancMap()

class Boat():
    def __init__(self, position: Vector2, dimensions: Vector2):
        self.pos = position
        self.oldPos = Vector2(75, 75)
        self.dim = dimensions*GRIDSIZE
        self.normDim = dimensions
        
        self.rect = pygame.Rect(self.pos.x-1, self.pos.y-1, self.dim.x, self.dim.y)
        boats.append(self)

    def checkInBounds(self, _x, _y):
        for y in range(self.normDim.y):
            for x in range(self.normDim.x):
                pX = (self.pos.x + (75*x))
                pY = (self.pos.y + (75*y))

                if((_x+(75*x)+1) >= width):
                    return self.oldPos
                elif((_y+(75*y)+1) >= height):
                    return self.oldPos

        return Vector2(_x, _y)

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

boats: List[Boat] = []
Boat(Vector2(75, 75), Vector2(2, 1))
Boat(Vector2(75, 75), Vector2(3, 1))
#Boat(Vector2(75, 75), Vector2(1, 2))


def draw():
    for y in range(mapSize):
        for x in range(mapSize):
            square = y * mapSize + x

            # empty slot
            if(grid[square] == 0):
                pygame.draw.rect(screen, EMPTY, (x * GRIDSIZE, y * GRIDSIZE, GRIDSIZE - 2, GRIDSIZE - 2))
            elif(grid[square] == 1):
                pygame.draw.rect(screen, BOAT, (x * GRIDSIZE, y * GRIDSIZE, GRIDSIZE, GRIDSIZE))
            elif(grid[square] == 2):
                pygame.draw.rect(screen, HIT, (x * GRIDSIZE, y * GRIDSIZE, GRIDSIZE - 2, GRIDSIZE - 2))

    for boat in boats:
        boat.draw()

selectedIndex: int = None # index can be 0
while canEdit:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            isRunning = False
            canEdit = False
            pygame.quit()

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                blancMap()
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

        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                if(selectedIndex == None):
                    continue
                
                x = min(int(event.pos[0]/GRIDSIZE), mapSize-1) * GRIDSIZE
                y = min(int(event.pos[1]/GRIDSIZE), mapSize-1) * GRIDSIZE

                if(boats[selectedIndex].rect.colliderect(pygame.Rect(width, 0, width+100, height + 100))):
                    print("Overlap right")
                    boats[selectedIndex].pos = Vector2(150, 150)
                elif(boats[selectedIndex].rect.colliderect(pygame.Rect(0, height, width+100, height + 100))):
                    print("Overlap bottom")
                    boats[selectedIndex].pos = Vector2(150, 150)
                else:
                    boats[selectedIndex].pos = Vector2(x, y)
                    boats[selectedIndex].oldPos = Vector2(x, y)
                selectedIndex = None

        elif event.type == pygame.MOUSEMOTION:
            if selectedIndex is not None: # selected can be `0` so `is not None` is required
                # move object
                boats[selectedIndex].pos.x = event.pos[0] + offset.x
                boats[selectedIndex].pos.y = event.pos[1] + offset.y


    screen.fill((0, 0, 0)) #(160, 193, 217)
    draw()

    pygame.display.update()


# actual attacking

while isRunning:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            isRunning = False
            canEdit = False
            pygame.quit()

        elif event.type == pygame.MOUSEBUTTONDOWN:
            square = Vector2(int(event.pos[0]/GRIDSIZE), int(event.pos[1]/GRIDSIZE))
            print(square)

    screen.fill((0, 0, 0)) #(160, 193, 217)
    draw()

    pygame.display.update()


sys.exit()