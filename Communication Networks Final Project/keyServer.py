import re
import threading
from math import floor
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
    conversationKeys = None  # tuple of (id, symmetric key)
    def __init__(self):
        self.userArray = []

        self.serverPort = 12002
        self.stopPort = 12003
        self.server_ip = '127.0.0.1'

        self.serverSocket = socket(AF_INET, SOCK_STREAM)  # AF_INET = Address Family, Internet Protocol (v4) -> ipv4 addresses will connect to this socket.

        # SOCK_STREAM connection oriented -> two-way byte streams
        self.stopSocket = socket(AF_INET, SOCK_STREAM)
        self.serverSocket.bind(('127.0.0.1',self.serverPort))  # '' contains addresses, when empty it means all
        self.stopSocket.bind(('127.0.0.1', self.stopPort))

        (self.pubKey, self.privKey) = asymmetricKeying.generateKeys()

        self.currentThreads = []
        self.connectedClients = []
        self.connectionSockets = []  # some sockets need to remain active for a while
        self.username_password_pairs = []  # already registered users
        self.database = {"login": ["password", [("id1", "key1"), ("id2", "key2")]]}

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
        msg_type = msg_bs.messageType
        msg_content = msg_bs.content


        if msg_type == ByteStreamType.registerrequest:
            username_already_used = False
            (username, password) = msg_content.split(' - ', 1)
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

        if msg_type == ByteStreamType.loginrequest:
            user_exists = False
            username = msg_content
            for name_pw_pair in self.username_password_pairs:
                if name_pw_pair[0] == username:
                    # the user exist
                    user_exists = True

            if user_exists:
                answer_bs = ByteStream(byteStreamType.ByteStreamType.passwordrequest, "send password")
                connectionSocket.send(answer_bs.outStream)
                # connectionSocket not closed to receive password
                self.connectionSockets.append((connectionSocket, username))
            else:
                answer_bs = ByteStream(byteStreamType.ByteStreamType.loginanswer, "user non existent")
                connectionSocket.send(answer_bs.outStream)
                connectionSocket.close()  # user non existent => login abort

        if msg_type == ByteStreamType.passwordanswer:
            password = msg_content
            password_correct = False
            i = self.connectionSockets.index(connectionSocket)
            username = self.connectionSockets[i][1]
            for name_pw_pair in self.username_password_pairs:
                if name_pw_pair == (username, password):
                    password_correct = True
            if password_correct:
                answer_bs = ByteStream(byteStreamType.ByteStreamType.passwordanswer, "password correct")
                connectionSocket.send(answer_bs.outStream)
                # Close and remove connectionSocket
                self.connectionSockets.remove(connectionSocket)
                connectionSocket.close()
            else:
                answer_bs = ByteStream(byteStreamType.ByteStreamType.passwordanswer, "password wrong")
                connectionSocket.send(answer_bs.outStream)
                # Close and remove connectionSocket
                self.connectionSockets.remove(connectionSocket)
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
        return self.find_in_sorted_list(login)[0]
        pass

    def load(self, location):
        pass

    def write(self, location):
        pass

    def find_in_sorted_list(self, login):
        bottom_index = 0
        top_index = len(self.database) - 1
        while True:
            middle_index = floor( (bottom_index+top_index) / 2)
            if middle<
        pass