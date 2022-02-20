import socket
from threading import Thread
from time import sleep
from typing import List

from utils import CONN_TEST, specialMessages

import hashlib

HOST = '127.0.0.1'  # Standard loopback interface address (localhost)
PORT = 5050        # Port to listen on (non-privileged ports are > 1023)
FORMAT = 'utf-8'

DISCONNECT = specialMessages["disconnect"]
SURRENDER = specialMessages["surrender"]

ADDR = (HOST, PORT)
mapSize = 10

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(ADDR)

grids = []

class Room:
    def __init__(self, name: str):
        self.name = hashlib.shake_256(name.encode(FORMAT)).hexdigest(8) # == 16 in length
        self.count = 0

        self.connections = []

        self.ready = -2 # if 0 then game starts
        self.isFinished = False

        rooms.append(self)

    def addPlayer(self, newConn):
        self.connections.append(newConn)
        self.count += 1

    def removePlayer(self, conn):
        #! if player is owner kick other player
        if conn not in self.connections: return

        self.connections.remove(conn)
        self.count -= 1

        if self.count <= 0:
            rooms.remove(self)
            del self

rooms: List[Room] = []


def starPattern(lel: list, s: int):
    l = max(s-1, 0)
    r = min(s+1, mapSize**2-1)
    u = max(s-mapSize, 0)
    d = min(s+mapSize, mapSize**2-1)

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
    
    return [str(lel[l]), str(lel[r]), str(lel[u]), str(lel[d])] # 4


def testConnection(conn) -> bool:
    try:
        conn.send(CONN_TEST.encode(FORMAT))
    except:
        return False

    return True

def handle_player(conn, addr, room: Room):
    connected = True
    other = None
    otherGrid = None

    # when the start (ready) button is pressed, then it sends the grid.
    grid = conn.recv(2048).decode(FORMAT)
    grid = grid.split(",")
    # convert from List[str] to List [int]
    if len(grid) <= 3:
        room.removePlayer(conn)
        conn.close()
        print("client closed")
        connected = False
        return

    for i in range(0, len(grid)):
        grid[i] = int(grid[i])

    grids.append(grid)  
    

    room.ready += 1

    while room.ready < 0:
        print(testConnection(conn))
        sleep(0.1)
        # if not testConnection(conn):
        #     connected = False
        #     break

    print("both here")
    
    # wait until there are two players
    # send a start message to all players. the player with the bool isTurn variable will start 

    print(room.connections.index(conn))
    conn.send(f"1{room.connections.index(conn)}".encode(FORMAT))

    while connected:
        # position of mouse point in grid space
        recvMessage = conn.recv(2).decode(FORMAT)
        
        if(recvMessage == DISCONNECT):
            room.connections.pop(conn)
            connected = False
            # send to the other a force quit message
            break
        elif recvMessage == SURRENDER:
            conn.send(SURRENDER.encode(FORMAT))
            other.send(f"2{list(room.connections.keys()).index(conn)}1".encode(FORMAT))
            continue
        elif not testConnection(conn):
            print('bad or interrupted connection. closeing game')
            other.send(f"2{list(room.connections.keys()).index(conn)}1".encode(FORMAT)) # other wins because client to stupid to by connection
            break


        square = int(recvMessage[:2])
        
        if other == None:
            other = list(room.connections.keys())[1]
        if otherGrid == None:
            otherGrid = grids[1]

        # {bool isTurn}{int2 squareHit}{bool isHit} = buffer size 4

        isHit = False
        otherSquares = ["0", "0", "0", "0"] # change the standart values
        square = min(square, mapSize**2-1)
        print(square, len(otherGrid), len(grid))

        if otherGrid[square] == 1:
            isHit = True
            otherGrid[square] = 2

            otherSquares = starPattern(otherGrid, square) # returns the value of the other squares


        square = "%02d" % (square,) # convert to a 2 digit format

        #print(f"Player: {list(connections.keys()).index(conn)} >>  1{square}{isHit}")
        #{isTurn}{attackedSquare}{isHit}
        other.send(f"1{square}{int(isHit)}".encode(FORMAT)) # 4

        # {isTurn}{attackedSquare}{isHit}{l,r,u,d}
        conn.send(f"0{square}{int(isHit)}{''.join(otherSquares)}".encode(FORMAT)) #8

        # win condition
        if 1 not in otherGrid:
            # win
            other.send(f"2{list(room.connections.keys()).index(conn)}0".encode(FORMAT))  # other looses
            conn.send(f"2{list(room.connections.keys()).index(conn)}1".encode(FORMAT))   # you win
            room.isFinished = True
            break

    room.removePlayer(conn)
    conn.close()
    print("removed")

def findRoom(name: str) -> Room:
    for room in rooms:
        if room.name == name:
            return room

        # if not hashed name
        if room.name == hashlib.shake_256(name.encode()).hexdigest(8):
            return room

    return None

def start():
    server.listen()
    print("[SERVER] Server launch successful!")
    while True:
        conn, addr = server.accept()
        print(conn.getpeername())

        initMessage = conn.recv(20).decode(FORMAT) # buffer 9 when creating room and 17 when joining with hash
        joinMethod = initMessage[0].lower()
        roomName = initMessage[1:].lower()

        # create room
        if joinMethod == "c":
            room = Room(roomName)
            room.addPlayer(conn)

            sleep(0.1)
            conn.send(f"{room.name}".encode(FORMAT))

        # join existing room
        elif joinMethod == "j":
            room = findRoom(roomName)

            if room == None:
                conn.send(f"{DISCONNECT}no room found!".encode(FORMAT))
                conn.close()
                continue

            room.addPlayer(conn)
            print(room.connections)
            sleep(0.1)
            conn.send(f"{room.name}".encode(FORMAT))

        else:
            conn.close()
            continue

        Thread(target=handle_player, args=(conn, addr, room)).start()

start()