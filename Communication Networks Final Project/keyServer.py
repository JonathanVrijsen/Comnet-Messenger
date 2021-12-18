from user import User
from socket import *
import asymmetricKeying



class keyServer:
    userArray = None
    serverPort = None
    serverSocket = None
    pubKey = None
    privKey = None

    def __init__(self):
        self.userArray = []
        self.serverPort = 12000
        self.serverSocket = socket(AF_INET, SOCK_STREAM) #AF_INET = Address Family, Internet Protocol (v4) -> ipv4 addresses will connect to this socket.
        #SOCK_STREAM connection oriented -> two-way byte streams
        self.serverSocket.bind(('',self.serverPort)) #'' contains addresses, when empty it means all
        (self.pubKey, self.privKey) = asymmetricKeying.generateKeys()

    def listen(self):
        self.serverSocket.listen(64) #Number of allowed unnaccepted connections
        connectionSocket, addr = self.serverSocket.accept() #return values: socket for client, and clientIP

        newThread


