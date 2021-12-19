from asymmetricKeying import generateKeys
from user import User
from socket import *
from RegErrorTypes import *
from byteStream import *
from byteStreamType import *


class Client:
    user = None
    server_ip = None
    server_socket = None
    key_server_ip = None
    key_server_socket = None
    conversations = None

    mainSymKey = None
    keySymKey = None

    def __init__(self):
        self.own_ip = "127.0.0.1"
        (self.pubKey, self.privKey) = generateKeys()
        (self.server_ip, self.server_socket, self.key_server_ip, self.key_server_socket) = self.get_server_information()

        self.clientToMainSocket = socket(AF_INET, SOCK_STREAM)
        self.clientToMainSocket.connect((self.server_ip, self.server_socket))

        self.clientToKeySocket = socket(AF_INET, SOCK_STREAM)
        self.clientToKeySocket.connect((self.key_server_ip, self.key_server_socket))

    def login(self, username, password):
        # send username and password to keyserver
        # if login successful, set current user of client and get conversations from server
        self.user = User(username, password)
        self.get_conversations()

    def register(self, username, password1, password2, password3):

        if password1 != password2 or password1 != password3:
            return RegisterErrorType.NoPasswordMatch
        elif not username:
            return RegisterErrorType.NoUsername
        elif not password1:
            return RegisterErrorType.NoPassword
        else:
            reg_bs = ByteStream(ByteStreamType.registerrequest,username + " - "+password1)
            self.clientToKeySocket.send(reg_bs.outStream)
            return RegisterErrorType.NoError


    def get_server_information(self):
        return '127.0.0.1', 12000, '127.0.0.1', 12002

    def get_conversations(self):
        # request all the user's conversation from the server

        pass

    def first_message_to_server(self):
        byteStreamOut = ByteStream(ByteStreamType.publickey, self.pubKey)
        outstream = byteStreamOut.outStream
        self.clientToMainSocket.send(outstream)

        #wait until server repplies with symmetric key for connection
        self.clientToMainSocket.listen(1)
        rcvd = self.clientToMainSocket.recv(1024)
        byteStreamIn = ByteStream(rcvd)
        if (byteStreamIn.messageType == ByteStreamType.symmetrickey):
            self.mainSymKey = byteStreamIn.content


    def send_message(self, message, conversation = None):
        content = message  # get content from the gui
        b = bytes(content, 'utf-8')
        #conversation.add_message(content, self.user.username)

        # if no mainSymKey exists: first contact with main server, create secure channel
        if (self.mainSymKey == None):
            self.first_message_to_server()

        self.clientToMainSocket.send(b)

    def logout(self):
        # go back to begin screen
        user = None
        conversations = None

        # in a way, the keys of the previous user are still saved at the client.
        # so maybe, implement a signal to let the keyServer know that some client has logged out,
        # and hence it should create new keys for the conversations of the client



