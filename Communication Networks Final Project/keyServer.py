import threading
from random import getrandbits
from socket import *
import asymmetricKeying
from cryptography.fernet import Fernet


class keyServer:
    userArray = None
    serverPort = None
    serverSocket = None
    stopSocket = None
    pubKey = None
    privKey = None
    currentThreads = None
    conversationKeys = None #tuple of (id, symmetric key)
    def __init__(self):
        self.userArray = []
        self.serverPort = 12002
        self.stopPort = 12003
        self.serverSocket = socket(AF_INET, SOCK_STREAM) #AF_INET = Address Family, Internet Protocol (v4) -> ipv4 addresses will connect to this socket.
        #SOCK_STREAM connection oriented -> two-way byte streams
        self.stopSocket = socket(AF_INET, SOCK_STREAM)
        self.serverSocket.bind(('127.0.0.1',self.serverPort)) #'' contains addresses, when empty it means all
        self.stopSocket.bind(('127.0.0.1', self.stopPort))
        (self.pubKey, self.privKey) = asymmetricKeying.generateKeys()
        self.currentThreads = []
        self.conversationKeys = []
        self.username_password_pairs = []

    def listen(self):
        self.serverSocket.listen(64) #Number of allowed unnaccepted connections
        connectionSocket, clientIP = self.serverSocket.accept() #return values: socket for client, and clientIP
        rcvdContent = connectionSocket.recv(1024)
        newThread = threading.Thread(target=self.handle_message(), args=(connectionSocket, clientIP))
        newThread.start()
        self.currentThreads.append(newThread)

    def create_conversation(self):
        id = getrandbits(32)

        # check if id doesn't exist already
        passed = False
        while not passed:
            passed = True
            for i in range(len(self.conversationKeys)):
                if id == self.conversationKeys(i):
                    passed = False
                    id = getrandbits(32)
                    break
        newSymKey = Fernet.generate_key()
        self.conversationKeys.append(id, newSymKey)

    def handle_message(self,clientIP):
        pass
        #step: if request for public key, send it, otherwise ignore
        #step: decode message using private key and
        #step: if register request, take account-password, check IP if sus?, check if accountname doesn't exist already
        #if allright, create public and private key and send to receiver over temporary secure channel
        #step: if login request, check combo and send to receiver over temporary secure channel
    def listen_silently(self):

        self.serverSocket.listen(64)
        connectionSocket, addr = self.serverSocket.accept()
        rcvdContent = connectionSocket.recv(1024)

        return rcvdContent.decode("utf-8"), addr

    def stop_listening(self):
        b = bytes('1', 'utf-8')
        self.stopSocket.connect((self.server_ip, self.server_socket))
        self.stopSocket.send(b)
        self.stopSocket.close()