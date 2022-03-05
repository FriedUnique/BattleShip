from cgi import test
import socket
from threading import Thread
from time import sleep
from typing import List

from utils import CONN_TEST, specialMessages

import hashlib
import sys

HOST = '127.0.0.1'  # (localhost)
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
    # TODO: Rename room if roomname already exists
    def __init__(self, name: str):
        self.name = hashlib.shake_256(name.encode(FORMAT)).hexdigest(8) # == 16 in length
        self.count = 0

        self.connections = []
        self.userNames = {}

        self.ready = -2 # if 0 then game starts, when player ready message, ready is incremented
        self.isFinished = False

        rooms.append(self)

    def checkNameOfPlayer(self, name: str):
        if name in list(self.userNames.values()):
            return name + "1"
        return name

    def addPlayer(self, newConn, userName):
        self.connections.append(newConn)
        self.userNames[newConn] = userName
        self.count += 1

    def removePlayer(self, conn):
        #! if player is owner kick other player
        if conn not in self.connections:
            print("errororooooooooo")
            return

        self.connections.remove(conn)
        del self.userNames[conn]
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


def testConnection(conn):
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
    if len(grid) <= 3:
        print(grid)
        room.removePlayer(conn)
        conn.close()
        print("client closed")
        connected = False
        return

    # convert from List[str] to List [int]
    for i in range(0, len(grid)):
        grid[i] = int(grid[i])

    grids.append(grid)  
    

    room.ready += 1

    while room.ready < 0:
        sleep(0.1)
        if not testConnection(conn):
            connected = False
            break
    
    # wait until there are two players
    # send a start message to all players. the player with the bool isTurn variable will start 

    #print(room.connections.index(conn))
    # start message, it determines who starts (second paramter)

    if connected:
        if other == None:
            x = list(room.connections)
            x.remove(conn)
            other = x[0]

        if otherGrid == None:
            g = list(grids)
            g.remove(grid)
            otherGrid = list(map(int, g[0]))
            
        conn.send(f"1{room.connections.index(conn)}{room.userNames[other]}".encode(FORMAT))

    while connected and room.isFinished == False:
        # position of mouse point in grid space
        try:
            if not testConnection(conn):
                print('bad or interrupted connection. closeing game')
                other.send(f"2{room.connections.index(conn)}1...".encode(FORMAT)) # other wins because client to stupid to by connection
                break

            recvMessage = conn.recv(4).decode(FORMAT) # only really needs 2 bytes but all the special messages have a 4 byte config
            
            if(recvMessage == DISCONNECT):
                print("disconnect reseived")
                if testConnection(other):
                    other.send(f"2{room.connections.index(conn)}1Player {room.userNames[conn]} disconnected!".encode(FORMAT))
                break
            """elif recvMessage == SURRENDER:
                conn.send(SURRENDER.encode(FORMAT))
                other.send(f"2{room.connections.index(conn)}1".encode(FORMAT))
                break"""

            
            if len(room.connections) != 2:
                conn.send(f"{DISCONNECT}otherPlayer left the game! You win!".encode(FORMAT))



            square = int(recvMessage[:2])

            # {bool isTurn}{int2 squareHit}{bool isHit} = buffer size 4
            isHit = False
            otherSquares = ["0", "0", "0", "0"] # change the standart values
            square = min(square, mapSize**2-1)

            # check hit
            if otherGrid[square] == 1:
                isHit = True
                otherGrid[square] = 2
                otherSquares = starPattern(otherGrid, square) # returns the value of the other squares


            square = "%02d" % (square,) # convert to a 2 digit format

            #print(f"Player: {list(connections).index(conn)} >>  1{square}{isHit}")
            #{isTurn}{attackedSquare}{isHit}
            other.send(f"1{square}{int(isHit)}".encode(FORMAT)) # 4

            # {isTurn}{attackedSquare}{isHit}{l,r,u,d}
            # after you attacked, attack responce
            conn.send(f"0{square}{int(isHit)}{''.join(otherSquares)}{room.userNames[other]}".encode(FORMAT)) #8+len(userName)

            # win condition
            if 1 not in otherGrid:
                # win
                other.send(f"2{room.connections.index(conn)}0You Loose!".encode(FORMAT))  # other looses
                conn.send(f"2{room.connections.index(conn)}1You Win!".encode(FORMAT))   # you win
                print("[SERVER]: Game finished")
                room.isFinished = True
                break
        except ValueError:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            print(f"Value Error on line {exc_tb.tb_lineno} (Type:{exc_type})")

        except Exception as e:
            # 'surrender' because of internet or connection error
            exc_type, exc_obj, exc_tb = sys.exc_info()
            print(e, exc_tb.tb_lineno)
            break

    room.removePlayer(conn)
    conn.close()
    print("closed client")

def findRoom(name: str):
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

        initMessage = conn.recv(26).decode(FORMAT) # {joinMethod}{roomName},{userName} DONT FORGET TO COUNT THE COMMA
        joinMethod = initMessage[0].lower()

        roomName = initMessage[1:].split(",")[0].lower()
        userName = initMessage[1:].split(",")[1]

        # create room
        if joinMethod == "c":
            room = Room(roomName)
            room.addPlayer(conn, userName)

            sleep(0.1)
            # responce
            conn.send(f"{room.name}{userName}".encode(FORMAT))

        # join existing room
        elif joinMethod == "j":
            room = findRoom(roomName)

            if room == None:
                conn.send(f"{DISCONNECT}No Room Found!".encode(FORMAT))
                conn.close()
                continue

            if room.count == 2:
                conn.send(f"{DISCONNECT}Room Is Full".encode(FORMAT))
                conn.close()
                continue
                
            #userName = room.checkNameOfPlayer(userName)
            room.addPlayer(conn, userName)
            sleep(0.1)

            # responce
            conn.send(f"{room.name}{userName}".encode(FORMAT))

        else:
            conn.close()
            continue

        Thread(target=handle_player, args=(conn, addr, room)).start()

start()