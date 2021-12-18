from user import User
from socket import *
import threading


class connectedUser:
    def __int__(self, connectionSocket, user):
        self.connectionSocket = connectionSocket
        self.user= user

class Server:
    def __init__(self):
        self.conversations=[]
        self.connectedUsers=[]

        self.serverPort = 12000
        self.serverSocket = socket(AF_INET, SOCK_STREAM)
        self.serverSocket.bind(('', self.serverPort))

    def listen(self):
        self.serverSocket.listen(64)
        connectionSocket, addr = self.serverSocket.accept()
        rcvdContent = connectionSocket.recv(1024)
        #extract username from sender
        username = "name"
        #create user
        newUser = User(username)
        newConnectedUser = connectedUser(connectionSocket, newUser)
        self.connectedUsers.append(newConnectedUser)

    def listenToConnectedUser(self, connectedUser):
        connectedUser.connectionSocket.listen(16)




