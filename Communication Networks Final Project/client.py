from main import generateKeys
from user import User

class Client:
    user = None

    def __init__(self):
        (pubKey, privKey)=generateKeys()
        pass

    def login(self, username, password):
        #send username and password to keyserver
        #if login successful, set current user of client
        self.user=User(username, password)

    def logout(self):
        #go back to begin screen
        user=None

        #in a way, the keys of the previous user are still saved at the client.
        #so maybe, implement a signal to let the keyServer know that some client has logged out, and hence it should create new keys for the conversations of the client
