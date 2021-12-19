from asymmetricKeying import generateKeys
from user import User
from socket import *


class Client:
    user = None
    server_ip = None
    server_socket = None
    key_server_ip = None
    key_server_socket = None
    conversations = None

    def __init__(self):
        (self.pubKey, self.privKey) = generateKeys()
        (self.server_ip, self.server_socket, self.key_server_ip, self.key_server_socket) = self.get_server_information()

    def login(self, username, password):
        # send username and password to keyserver
        # if login successful, set current user of client and get conversations from server
        self.user = User(username, password)
        self.get_conversations()

    def get_server_information(self):
        return '127.0.0.1', 12002, '127.0.0.1', 12001

    def get_conversations(self):
        # request all the user's conversation from the server

        pass

    def send_message(self, message, conversation = None):
        content = message  # get content from the gui
        b = bytes(content, 'utf-8')
        #conversation.add_message(content, self.user.username)
        clientSocket = socket(AF_INET, SOCK_STREAM)
        clientSocket.connect((self.server_ip, self.server_socket))
        clientSocket.send(b)
        clientSocket.close()

    def logout(self):
        # go back to begin screen
        user = None
        conversations = None

        # in a way, the keys of the previous user are still saved at the client.
        # so maybe, implement a signal to let the keyServer know that some client has logged out,
        # and hence it should create new keys for the conversations of the client
