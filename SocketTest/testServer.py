import socket
from threading import Thread
from time import sleep

HOST = '127.0.0.1'  # Standard loopback interface address (localhost)
PORT = 5050        # Port to listen on (non-privileged ports are > 1023)
FORMAT = 'utf-8'
ADDR = (HOST, PORT)
DISCONNECT = "dDd!"

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(ADDR)

connections = {}

def handle_player(conn, addr, start: bool):
    connected = True
    isTurn = start
    other = None
    grid = None

    #! upload the grid, so server can check

    if len(connections) > 0:
        other = list(connections.keys())[0]

    connections[conn] = addr
    while len(connections) <= 1:
        sleep(0.01)
    
    # wait until there are two players
    # send a start message to all players. the player with the bool isTurn variable will start 

    for index, connection in enumerate(connections):
        connection.send(f"1{index}".encode(FORMAT))

    while connected:
        # position of mouse point in grid space
        recvMessage = conn.recv(4).decode(FORMAT)
        x, y = int(recvMessage[:2]), int(recvMessage[2:4])

        if(recvMessage == DISCONNECT):
            connections.pop(conn)
            connected = False
            break
        
        #! send to other
        # {bool isTurn}{int2 gridSpaceHitX}{int2 gridSpaceHitY}
        if other == None:
            other = list(connections.keys())[1]
        
        other.send(f"1{x}{y}".encode(FORMAT))
        # recv confirmation
        

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