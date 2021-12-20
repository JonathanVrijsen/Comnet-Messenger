import re
import threading
from math import floor
from random import getrandbits
from socket import *
import asymmetricKeying
import symmetricKeying
from byteStreamType import *
from cryptography.fernet import Fernet
from byteStream import *
from server import ConnectedClient


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

        self.serverSocket = socket(AF_INET,
                                   SOCK_STREAM)  # AF_INET = Address Family, Internet Protocol (v4) -> ipv4 addresses will connect to this socket.

        # SOCK_STREAM connection oriented -> two-way byte streams
        self.stopSocket = socket(AF_INET, SOCK_STREAM)
        self.serverSocket.bind(('127.0.0.1', self.serverPort))  # '' contains addresses, when empty it means all
        self.stopSocket.bind(('127.0.0.1', self.stopPort))

        (self.pubKey, self.privKey) = asymmetricKeying.generateKeys()

        self.currentThreads = []
        self.connectedClients = []

        self.username_password_pairs = []  # already registered users
        self.database = dict()  #{"login": ["password", [("id1", "key1"), ("id2", "key2")]]}

    def listen(self):
        self.serverSocket.listen(64)
        connectionSocket, addr = self.serverSocket.accept()
        rcvdContent = connectionSocket.recv(1024)

        # check if incoming client wants to make a new connection. If this is the case, it hands the server its public key first
        byteStreamIn = ByteStream(rcvdContent)
        if (byteStreamIn.messageType == ByteStreamType.keyrequest):
            clientPubKey = asymmetricKeying.string_to_pubkey(byteStreamIn.content)
            print("KS receivers client pubkey:")
            print(clientPubKey)

        print("KS sends own pubkey:")
        print(self.pubKey)
        # send own public key to client
        byteStreamOut = ByteStream(ByteStreamType.pubkeyanswer, self.pubKey)
        connectionSocket.send(byteStreamOut.outStream)  # send own public key

        # encrypt symmetric key and send to client
        newSymKey = Fernet.generate_key()
        print("KS sends symkey:")
        print(newSymKey)
        msg_bs = ByteStream(ByteStreamType.symkeyanswer, newSymKey)
        msg = asymmetricKeying.rsa_sendable(msg_bs.outStream, self.privKey, clientPubKey)
        print("KS sends symkey, encrypted")
        print(msg)
        connectionSocket.send(msg)

        #create new connected client
        newConnectedClient = ConnectedClient(connectionSocket, newSymKey, clientPubKey)
        self.connectedClients.append(newConnectedClient)


        # launch new thread dedicated to connectedClient
        newThread = threading.Thread(target=self.connected_user_listen, args=(newConnectedClient,))
        self.currentThreads.append(newThread)
        newThread.start()




        #newThread = threading.Thread(target=self.handle_message, args=(rcvdContent, connectionSocket,))
        #newThread.start()
        #self.currentThreads.append(newThread)

    def listen_for_password(self, connectionSocket):
        rcvdContent = connectionSocket.recv(1024)
        print("content rec listen for password")
        if rcvdContent != b"":
            print("content not empty listen for password")
            print(rcvdContent)
            self.handle_message(rcvdContent, connectionSocket)

    def connected_user_listen(self, connectedClient):
        while connectedClient.active:
            connectionSocket = connectedClient.connectionSocket
            rcvd = connectionSocket.recv(1024)
            print("RECEIVED")
            rcvd = symmetricKeying.symmDecrypt(rcvd, connectedClient.symKey)
            byteStreamIn = ByteStream(rcvd)
            type = byteStreamIn.messageType
            content = byteStreamIn.content

            if type == ByteStreamType.registerrequest:
                (username, password) = content.split(' - ', 1)
                if self.check_existense_of_account(username):
                    raise CustomError(ServerErrorTypes.ServerErrorType.AccountAlreadyExists)
                else:
                    self.add_user(username, password)
                    answer_bs = ByteStream(byteStreamType.ByteStreamType.registeranswer, "succes")

                #            username_already_used = False
                #            (username, password) = msg_content.split(' - ', 1)
                # for name_pw_pair in self.username_password_pairs:
                #    if name_pw_pair[0] == username:
                #        username_already_used = True
                #        print("balls")

                # answer_bs = ByteStream(byteStreamType.ByteStreamType.registeranswer, "failed")

                #            if (not username_already_used):
                #                self.username_password_pairs.append((username, password))
                #                answer_bs = ByteStream(byteStreamType.ByteStreamType.registeranswer, "succes")
                answer_bs = symmetricKeying.symmEncrypt(answer_bs, connectedClient.symKey)
                connectionSocket.send(answer_bs.outStream)

            elif type == ByteStreamType.loginrequest:
                user_exists = False
                username = content
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

            elif type == ByteStreamType.passwordanswer:
                password = content
                password_correct = False
                username = self.connectionSockets[connectionSocket]
                if self.check_existence_of_account(username):
                    if self.get_password(username) == password:
                        print("password correct!!")
                    password_correct = True

                if password_correct:
                    answer_bs = ByteStream(byteStreamType.ByteStreamType.loginanswer, "passwordcorrect")
                    connectionSocket.send(answer_bs.outStream)
                    # Close and remove connectionSocket
                    del self.connectionSockets[connectionSocket]
                    connectionSocket.close()
                else:
                    print("password incorrect!!")
                    answer_bs = ByteStream(byteStreamType.ByteStreamType.loginanswer, "passwordwrong")
                    connectionSocket.send(answer_bs.outStream)
                    # Close and remove connectionSocket
                    del self.connectionSockets[connectionSocket]

        # step: decode message using private key and
        # step: if register request, take account-password, check IP if sus?, check if accountname doesn't exist already
        # if allright, create public and private key and send to receiver over temporary secure channel
        # step: if login request, check combo and send to receiver over temporary secure channel
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

    def getUsers(self):
        return self.database

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

    def add_user(self, login, password):
        self.database[login] = [password, []]

    def add_key(self, login, id, key):
        self.database[login][1].append((id, key))

    def load(self, location):
        pass

    def write(self, location):
        pass

    def check_existence_of_account(self, login):
        return login in self.database

    def find_in_sorted_list(self, login):
        return self.database[login]
#        bottom_index = 0
#        top_index = len(self.database) - 1
#        while True:
#            middle_index = floor( (bottom_index+top_index) / 2)
#            if middle_index
#        pass
