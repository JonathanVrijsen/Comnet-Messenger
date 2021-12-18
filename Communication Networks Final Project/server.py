from user import User
from socket import *

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




