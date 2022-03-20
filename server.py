import socket
from threading import Thread
from time import sleep
from typing import List

from utils import specialMessages, starPattern

import hashlib
import sys
import time

HOST = '127.0.0.1'
PORT = 5050
FORMAT = 'utf-8'

DISCONNECT = specialMessages["disconnect"]
SURRENDER = specialMessages["surrender"]
CONN_TEST = specialMessages["connection test"]

ADDR = (HOST, PORT)

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(ADDR)

class Room:
    # TODO: Rename room if roomname already exists
    def __init__(self, name: str):
        self.name = hashlib.shake_256(name.encode(FORMAT)).hexdigest(8) # == 16 in length
        self.count = 0

        self.connections = []
        self.userNames = {}
        self.grids = []

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

def findRoom(name: str):
    for room in rooms:
        if room.name == name:
            return room

        # if not hashed name
        if room.name == hashlib.shake_256(name.encode()).hexdigest(8):
            return room

    return None

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
    try:
        grid = conn.recv(2048).decode(FORMAT)
        grid = grid.split(",")
        if len(grid) <= 3:
            room.removePlayer(conn)
            conn.close()
            print("Client closed. Bad message!")
            connected = False
            return

        # convert from List[str] to List [int]
        for i in range(0, len(grid)):
            grid[i] = int(grid[i])

        room.grids.append(grid)

    except ConnectionResetError:
        conn.close()
        room.removePlayer(conn)
        print("[SERVER] Client forcibly closed the connection")
        
        return
    

    room.ready += 1

    # wait until room is full
    while room.ready < 0:
        sleep(0.1)
        if not testConnection(conn):
            connected = False
            break

    if connected:
        if other == None:
            x = list(room.connections)
            x.remove(conn)
            other = x[0]

        if otherGrid == None:
            g = list(room.grids)
            g.remove(grid)
            otherGrid = list(map(int, g[0]))
            
        conn.send(f"1{room.connections.index(conn)}{room.userNames[other]}".encode(FORMAT)) # start message

    while connected and room.isFinished == False:
        # position of mouse point in grid space
        try:
            if not testConnection(conn):
                print('bad or interrupted connection. closeing game')
                other.send(f"2{room.connections.index(conn)}1...".encode(FORMAT)) # other wins because client to stupid to by connection
                break

            recvMessage = conn.recv(4).decode(FORMAT) # only really needs 2 bytes but all the special messages have a 4 byte config

            if recvMessage == CONN_TEST:
                continue
            
            if(recvMessage == DISCONNECT):
                print("disconnect reseived")
                if testConnection(other):
                    other.send(f"2{room.connections.index(conn)}1Player {room.userNames[conn]} disconnected!".encode(FORMAT))
                try:
                    conn.send(DISCONNECT.encode(FORMAT))
                except Exception:
                    pass

                break
            
            if len(room.connections) != 2:
                conn.send(f"{DISCONNECT}otherPlayer left the game! You win!".encode(FORMAT))


            square = int(recvMessage[:2])
            squareSend = "%02d" % (square,) # convert to 2 digit number

            # {bool isTurn}{int2 squareHit}{bool isHit} = buffer size 4
            isHit = False
            otherSquares = ["0", "0", "0", "0"] # change the standart values
            otherSquares = starPattern(otherGrid, square)
            

            #* check hit
            if otherGrid[square] == 1:
                isHit = True
                otherGrid[square] = 2

                #* if client hits a boat, he can shoot again.
                conn.send(f"1{squareSend}{int(isHit)}{''.join(otherSquares)}".encode(FORMAT))
                other.send(f"0{squareSend}{int(isHit)}".encode(FORMAT))

            else:
                otherGrid[square] = 3

                conn.send(f"1{squareSend}{int(isHit)}{''.join(otherSquares)}".encode(FORMAT)) #8+len(userName)
                other.send(f"0{squareSend}{int(isHit)}{''.join(otherSquares)}".encode(FORMAT)) # 4

                conn.send("0".encode(FORMAT))
                other.send("1".encode(FORMAT))


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

    time_string = time.strftime("%H:%M:%S", time.localtime())
    print(f"[{time_string}] closed client")


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
            if findRoom(roomName) != None:
                conn.send(f"{DISCONNECT}Room already exists".encode(FORMAT))
                conn.close()
                continue

            room = Room(roomName)
            room.addPlayer(conn, userName)

            sleep(0.1)
            # responce
            conn.send(f"{room.name}{userName}".encode(FORMAT))

        # join existing room
        elif joinMethod == "j":
            room = findRoom(roomName) # roomName can be either a link or string name

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