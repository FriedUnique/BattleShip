import socket
from threading import Thread
from time import sleep
from typing import List

HOST = '127.0.0.1'  # Standard loopback interface address (localhost)
PORT = 5050        # Port to listen on (non-privileged ports are > 1023)
FORMAT = 'utf-8'
ADDR = (HOST, PORT)
DISCONNECT = "!dDd"
mapSize = 8

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(ADDR)

connections = {}
grids = []

def handle_player(conn, addr, start: bool):
    connected = True
    isTurn = start
    other = None
    otherGrid = None

    grid = conn.recv(2048).decode(FORMAT)
    grid = grid.split(",")
    # convert from List[str] to List [int]
    for i in range(0, len(grid)):
        grid[i] = int(grid[i])

    grids.append(grid)  

    if len(connections) > 0:
        other = list(connections.keys())[0]
        otherGrid = grids[0]

    connections[conn] = addr
    while len(connections) <= 1:
        sleep(0.01)
    
    # wait until there are two players
    # send a start message to all players. the player with the bool isTurn variable will start 

    for index, connection in enumerate(connections):
        connection.send(f"1{index}".encode(FORMAT))

    while connected:
        # position of mouse point in grid space
        recvMessage = conn.recv(2).decode(FORMAT)
        square = int(recvMessage[:2])
        square = "%02d" % (square,)

        if(recvMessage == DISCONNECT):
            connections.pop(conn)
            connected = False
            # send to the other a force quit message
            break
        
        if other == None:
            other = list(connections.keys())[1]
        if otherGrid == None:
            otherGrid = grids[1]

        # {bool isTurn}{int2 squareHit}{bool isHit} = buffer size 4

        isHit = False
        if otherGrid[int(square)] == 1:
            isHit = True
            otherGrid[int(square)] = 2

        print(f"Player: {list(connections.keys()).index(conn)} >>  1{square}{isHit}")
        other.send(f"1{square}{int(isHit)}".encode(FORMAT))
        conn.send(f"0{square}{int(isHit)}".encode(FORMAT))

        # win condition
        if 1 not in otherGrid:
            # win
            other.send(f"2{list(connections.keys()).index(conn)}0".encode(FORMAT))
            conn.send(f"2{list(connections.keys()).index(conn)}1".encode(FORMAT))
        

    conn.close()
    print("removed")

def start():
    server.listen()
    print("[SERVER] Server launch successful!")
    playerCount = 0
    while True:
        if playerCount == 2:
            break

        conn, addr = server.accept()
        playerCount += 1
        Thread(target=handle_player, args=(conn, addr, True if playerCount == 1 else False)).start()

start()