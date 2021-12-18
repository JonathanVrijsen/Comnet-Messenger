from asymmetricKeying import generateKeys
from user import User


class Client:
    user = None
    server_ip = None
    server_socket = None
    key_server_ip = None
    key_server_socket = None

    def __init__(self):
        (pubKey, privKey) = generateKeys()
        (server_ip,server_socket,key_server_ip,key_server_socket) = self.get_server_information(self)
        pass

    def login(self, username, password):
        # send username and password to keyserver
        # if login successful, set current user of client
        self.user = User(username, password)

    def get_server_information(self):

        return '127.0.0.1', 12000, '127.0.0.1', 12001

    def get_conversations(self, server_ip, server_socket):
        # request all the user's conversation from the server
        pass
    def send_message(self):
        pass

    def logout(self):
        # go back to begin screen
        user = None

        # in a way, the keys of the previous user are still saved at the client.
        # so maybe, implement a signal to let the keyServer know that some client has logged out, and hence it should create new keys for the conversations of the client
