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
from user import User


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
        #self.database = dict()  #{"login": ["password", [("id1", "key1"), ("id2", "key2")]]}

        fkey = open("serverCommonKey.txt",'rb')
        self.serverCommonKey = fkey.read()

        self.database = []
        self.conversationkeys = dict()

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
            print(rcvd)
            byteStreamIn = ByteStream(rcvd)
            type = byteStreamIn.messageType
            content = byteStreamIn.content

            if type == ByteStreamType.registerrequest:
                print(type)
                print(content)
                (username, password) = content.split(' - ', 1)
                if self.check_existense_of_account(username):
                    print("EXISTS")
                    # raise CustomError(ServerErrorTypes.ServerErrorType.AccountAlreadyExists)
                    answer_bs = ByteStream(byteStreamType.ByteStreamType.registeranswer, "failed")
                else:
                    print("DOES NOT EXIST")
                    print(username)
                    print(password)
                    self.database.append((username, password))
                    sign = symmetricKeying.symmEncrypt(username.encode('ascii'), self.serverCommonKey)
                    answer_bs = ByteStream(byteStreamType.ByteStreamType.registeranswer, str(sign))
                    print("Encrypted Username:", str(sign))

                out = symmetricKeying.symmEncrypt(answer_bs.outStream, connectedClient.symKey)
                connectionSocket.send(out)

            elif type == ByteStreamType.loginrequest:
                user_exists = False
                username = content
                for name_pw_pair in self.database:
                    print(self.database)
                    if name_pw_pair[0] == username:
                        # the user exist
                        user_exists = True

                if user_exists:
                    answer_bs = ByteStream(byteStreamType.ByteStreamType.passwordrequest, "sendpassword")
                    newUser = User(username)
                    connectedClient.set_user(newUser) #notice: password not yet given, so client isn't able yet to receive keys

                else:
                    answer_bs = ByteStream(byteStreamType.ByteStreamType.loginanswer, "usernonexistent")
                out = symmetricKeying.symmEncrypt(answer_bs.outStream, connectedClient.symKey)
                connectionSocket.send(out)

            elif type == ByteStreamType.passwordanswer:
                password = content
                password_correct = False
                user = connectedClient.user
                username = user.username

                for temp in self.database:
                    if temp[0] == username and password == temp[1]:
                        password_correct = True
                        break

                if password_correct:
                    sign = symmetricKeying.symmEncrypt(username.encode('ascii'), self.serverCommonKey)
                    answer_bs = ByteStream(byteStreamType.ByteStreamType.passwordcorrect, str(sign))
                    out = symmetricKeying.symmEncrypt(answer_bs.outStream, connectedClient.symKey)
                    connectionSocket.send(out)

                    newUser = User(connectedClient.user.username, password)
                    connectedClient.set_user(newUser)  # user set with password, client can obtain keys
                else:
                    print("password incorrect!!")
                    answer_bs = ByteStream(byteStreamType.ByteStreamType.passwordwrong, "")

                out = symmetricKeying.symmEncrypt(answer_bs.outStream, connectedClient.symKey)
                connectionSocket.send(out)

            elif type == ByteStreamType.newconversation:
                id = content
                conversation_key = Fernet.generate_key()

                self.conversationkeys[id]=conversation_key

                print("KS sends conv symkey: ", str(conversation_key))
                byteStreamOut = ByteStream(ByteStreamType.symkeyanswer, conversation_key)
                out = symmetricKeying.symmEncrypt(byteStreamOut.outStream, connectedClient.symKey)
                connectedClient.connectionSocket.send(out)

            elif type == ByteStreamType.requestconversationkey:
                ##TODO verify user
                id = content
                conversation_key = self.conversationkeys[id]

                byteStreamOut = ByteStream(ByteStreamType.symkeyanswer, conversation_key)
                out = symmetricKeying.symmEncrypt(byteStreamOut.outStream, connectedClient.symKey)
                connectedClient.connectionSocket.send(out)


        # step: decode message using private key and
        # step: if register request, take account-password, check IP if sus?, check if accountname doesn't exist already
        # if allright, create public and private key and send to receiver over temporary secure channel
        # step: if login request, check combo and send to receiver over temporary secure channel

    def getUsers(self):
        return self.database

    def getConnectedClients(self):
        return self.connectedClients

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

    def check_existense_of_account(self, username):
        for temp in self.database:
            tempname = temp[0]
            if tempname == username:
                return True

        return False

    def find_in_sorted_list(self, login):
        return self.database[login]
#        bottom_index = 0
#        top_index = len(self.database) - 1
#        while True:
#            middle_index = floor( (bottom_index+top_index) / 2)
#            if middle_index
#        pass
