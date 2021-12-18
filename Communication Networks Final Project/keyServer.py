import threading

from user import User
from socket import *
import asymmetricKeying



class keyServer:
    userArray = None
    serverPort = None
    serverSocket = None
    pubKey = None
    privKey = None
    currentThreads = None

    def __init__(self):
        self.userArray = []
        self.serverPort = 12000
        self.serverSocket = socket(AF_INET, SOCK_STREAM) #AF_INET = Address Family, Internet Protocol (v4) -> ipv4 addresses will connect to this socket.
        #SOCK_STREAM connection oriented -> two-way byte streams
        self.serverSocket.bind(('',self.serverPort)) #'' contains addresses, when empty it means all
        (self.pubKey, self.privKey) = asymmetricKeying.generateKeys()
        self.currentThreads = []

    def listen(self):
        self.serverSocket.listen(64) #Number of allowed unnaccepted connections
        connectionSocket, clientIP = self.serverSocket.accept() #return values: socket for client, and clientIP

        newThread = threading.Thread(target=self.handle_message(), args=(connectionSocket, clientIP))
        newThread.start()

        self.currentThreads.append(newThread)

    def handle_message(self,clientIP):
        pass
        #step: if request for public key, send it, otherwise ignore
        #step: decode message using private key and
        #step: if register request, take account-password, check IP if sus?, check if accountname doesn't exist already
        #if allright, create public and private key and send to receiver over temporary secure channel
        #step: if login request, check combo and send to receiver over temporary secure channel