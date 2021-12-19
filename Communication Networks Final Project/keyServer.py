import re
import threading
from random import getrandbits
from socket import *
import asymmetricKeying
from byteStreamType import *
from cryptography.fernet import Fernet
from byteStream import *


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
        self.server_ip = '127.0.0.1'

        self.serverSocket = socket(AF_INET, SOCK_STREAM) #AF_INET = Address Family, Internet Protocol (v4) -> ipv4 addresses will connect to this socket.

        #SOCK_STREAM connection oriented -> two-way byte streams
        self.stopSocket = socket(AF_INET, SOCK_STREAM)
        self.serverSocket.bind(('127.0.0.1',self.serverPort)) #'' contains addresses, when empty it means all
        self.stopSocket.bind(('127.0.0.1', self.stopPort))

        (self.pubKey, self.privKey) = asymmetricKeying.generateKeys()

        self.currentThreads = []
        self.connectedClients = []
        self.connectionSockets = [] #some sockets need to remain active for a while
        self.username_password_pairs = [] #already registered users

    def listen(self):
        print("keyserver listening")
        self.serverSocket.listen(64) #Number of allowed unnaccepted connections
        connectionSocket, addr = self.serverSocket.accept() #return values: socket for client, and clientIP
        rcvdContent = connectionSocket.recv(1024)

        newThread = threading.Thread(target=self.handle_message, args=(rcvdContent, connectionSocket,))
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

    def handle_message(self,rcvdContent, connectionSocket):
        msg_bs = ByteStream(rcvdContent)
        msgtype = msg_bs.messageType
        msgcontent = msg_bs.content


        if msgtype == ByteStreamType.registerrequest:
            username_already_used = False
            (username,password) = msgcontent.split(' - ',1)
            for name_pw_pair in self.username_password_pairs:
                if name_pw_pair[0] == username:
                    username_already_used = True
                    print("balls")

                    answer_bs = ByteStream(byteStreamType.ByteStreamType.registeranswer, "failed")

            if (not username_already_used):
                self.username_password_pairs.append((username,password))
                answer_bs = ByteStream(byteStreamType.ByteStreamType.registeranswer, "succes")

            connectionSocket.send(answer_bs.outStream)
            connectionSocket.close()

        #step: if request for public key, send it, otherwise ignore
        #step: decode message using private key and
        #step: if register request, take account-password, check IP if sus?, check if accountname doesn't exist already
        #if allright, create public and private key and send to receiver over temporary secure channel
        #step: if login request, check combo and send to receiver over temporary secure channel

    def getUsers(self):
        return self.username_password_pairs

    def listen_silently(self):

        self.serverSocket.listen(64)
        connection_socket, addr = self.serverSocket.accept()
        rcvd_content = connection_socket.recv(1024)

        return rcvd_content.decode("utf-8"), addr

    def stop_listening(self):
        b = bytes('1', 'utf-8')
        self.stopSocket.connect((self.server_ip, self.serverPort))
        self.stopSocket.send(b)
        self.stopSocket.close()

    def get_password(self, login):
        pass

    def load(self, location):
        pass

    def write(self, location):
        pass