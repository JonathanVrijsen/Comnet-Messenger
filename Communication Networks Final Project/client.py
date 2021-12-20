import asymmetricKeying
import symmetricKeying
from asymmetricKeying import *
from user import User
from socket import *
from RegErrorTypes import *
from byteStream import *
from byteStreamType import *
from cryptography.fernet import Fernet


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
        self.Mainserver_pubkey = None
        self.Mainserver_symkey = None

        self.clientToKeySocket = socket(AF_INET, SOCK_STREAM)
        self.clientToKeySocket.connect((self.key_server_ip, self.key_server_socket))
        self.Keyserver_pubkey = ""
        self.Keyserver_symkey = ""

        self.first_message_to_keyserver()


        #self.clientToKeySocket.send(reg_bs.outStream)


        self.contacts = []

    def login(self, username, password):
        # send username and password to keyserver
        # if login successful, set current user of client and get conversations from server
        self.clientToKeySocket = socket(AF_INET, SOCK_STREAM)
        self.clientToKeySocket.connect((self.key_server_ip, self.key_server_socket))

        login_bs = ByteStream(ByteStreamType.loginrequest, username)
        self.clientToKeySocket.send(login_bs.outStream)
        login_ans_bytes = self.clientToKeySocket.recv(1024)
        login_ans_bs = ByteStream(login_ans_bytes)
        login_ans = login_ans_bs.content
        if login_ans == "sendpassword":
            # send password

            password_bs = ByteStream(ByteStreamType.passwordanswer, password)
            self.clientToKeySocket.send(password_bs.outStream)
            password_ans_bytes = self.clientToKeySocket.recv(1024)
            password_ans_bs = ByteStream(password_ans_bytes)
            password_ans = password_ans_bs.content
            print(password_ans)
            if password_ans == "passwordcorrec":  # something wrong with regex
                print("password correct")
                self.user = User(username, password)
                self.get_conversations()
                self.clientToKeySocket.close()
                return True
            else:
                self.user = None
                self.clientToKeySocket.close()
                return False
        else:
            self.user = None
            self.clientToKeySocket.close()
            return False

    def register(self, username, password1, password2, password3):

        if password1 != password2 or password1 != password3:
            return RegisterErrorType.NoPasswordMatch
        elif not username:
            return RegisterErrorType.NoUsername
        elif not password1:
            return RegisterErrorType.NoPassword
        else:
            reg_bs = ByteStream(ByteStreamType.registerrequest, username + " - " + password1)

            if (self.Keyserver_symkey != None):
                print(self.Keyserver_symkey)
                print(reg_bs)
                reg_bs = symmetricKeying.symmEncrypt(reg_bs.outStream, self.Keyserver_symkey)
                self.clientToKeySocket.send(reg_bs.outStream)
                ans_bytes = self.clientToKeySocket.recv(1024)
                ans_bytes = symmetricKeying.symmDecrypt(ans_bytes, self.Keyserver_symkey)
                ans_bs = ByteStream(ans_bytes)
                ans = ans_bs.content
                if ans == "succes":
                    return RegisterErrorType.NoError
                else:
                    return RegisterErrorType.UsernameAlreadyInUse


    def get_server_information(self):
        return '127.0.0.1', 12100, '127.0.0.1', 12002

    def get_conversations(self):
        # request all the user's conversation from the server

        pass

    def first_message_to_server(self):
        byteStreamOut = ByteStream(ByteStreamType.keyrequest, self.pubKey)
        outstream = byteStreamOut.outStream
        print("Cl sends own pubkey:")
        print(self.pubKey)
        self.clientToMainSocket.send(outstream)

        #wait until server repplies with symmetric key for connection
        rcvd = self.clientToMainSocket.recv(1024)

        byteStreamIn = ByteStream(rcvd)
        if (byteStreamIn.messageType == ByteStreamType.pubkeyanswer):
            self.Mainserver_pubkey = asymmetricKeying.string_to_pubkey(byteStreamIn.content)
            print("Cl receives KS pubkey:")
            print(self.Mainserver_pubkey)

        rcvd = self.clientToKeySocket.recv(1024)
        print("Cl receives symm key, encrypted")
        print(rcvd)
        rcvd = rsa_receive(rcvd, self.Mainserver_pubkey, self.privKey)
        print(rcvd)
        byteStreamIn = ByteStream(rcvd)
        print(byteStreamIn.messageType)
        if (byteStreamIn.messageType == ByteStreamType.symkeyanswer):
            self.Keyserver_symkey = symmetricKeying.strToSymkey(byteStreamIn.content)
            print("Cl decrypts symm key")
            print(self.Keyserver_symkey)

    def first_message_to_keyserver(self):
        byteStreamOut = ByteStream(ByteStreamType.keyrequest, self.pubKey)
        outstream = byteStreamOut.outStream
        print("Cl sends own pubkey:")
        print(self.pubKey)
        self.clientToKeySocket.send(outstream)

        #wait until server repplies with symmetric key for connection
        rcvd = self.clientToKeySocket.recv(1024)

        byteStreamIn = ByteStream(rcvd)
        if (byteStreamIn.messageType == ByteStreamType.pubkeyanswer):
            self.Keyserver_pubkey = asymmetricKeying.string_to_pubkey(byteStreamIn.content)
            print("Cl receives KS pubkey:")
            print(self.Keyserver_pubkey)

        rcvd = self.clientToKeySocket.recv(1024)
        print("Cl receives symm key, encrypted")
        print(rcvd)
        rcvd = rsa_receive(rcvd, self.Keyserver_pubkey, self.privKey)
        print(rcvd)
        byteStreamIn = ByteStream(rcvd)
        print(byteStreamIn.messageType)
        if (byteStreamIn.messageType == ByteStreamType.symkeyanswer):
            print(byteStreamIn.content)
            self.Keyserver_symkey = symmetricKeying.strToSymkey(byteStreamIn.content)
            print("Cl decrypts symm key")
            print(self.Keyserver_symkey)


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



