import socket
from threading import Thread
from sys import exit
from time import sleep

isRunning = True

FORMAT = 'utf-8'
HOST = '127.0.0.1'
PORT = 5050
ADDR = (HOST, PORT)
DISCONNECT = "dDd!"
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(ADDR)

#isTurn = bool(client.recv(1).decode(FORMAT))

startMsg = client.recv(2).decode(FORMAT)
isStarted, isTurn = bool(int(startMsg[0])), bool(int(startMsg[1]))

received = ""

def recv():
    global received, isTurn
    while isRunning:
        received = client.recv(5).decode(FORMAT)
        isTurn = bool(int(received[0]))

recvThread = Thread(target=recv)
recvThread.start()

while isRunning and isStarted:
    if isTurn:
        msg = input("Message: ")
        if(msg == "d"):
            client.send(DISCONNECT.encode(FORMAT))
            isRunning = False
        else:
            client.send(msg.encode(FORMAT))
            isTurn = False
    else:
        sleep(0.01)


sleep(0.3)
client.close()
exit()