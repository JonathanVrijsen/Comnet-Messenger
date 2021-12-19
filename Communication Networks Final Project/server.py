from cryptography.fernet import Fernet

from user import User
from socket import *
from conversation import Conversation
from message import Message
import threading
import asymmetricKeying

class ConnectedClient:
    def __init__(self, connectionSocket, symKey, user):
        self.connectionSocket = connectionSocket
        self.user = user
        self.symKey = symKey
        self.loggedIn = True


class Server:
    def __init__(self):
        self.conversations = []
        self.connectedClients = []
        self.currentThreads = []

        self.serverPort = 12000
        self.stopPort = 12001
        self.serverSocket = socket(AF_INET, SOCK_STREAM)
        self.stopSocket = socket(AF_INET, SOCK_STREAM)
        self.serverSocket.bind(('127.0.0.1', self.serverPort))
        self.stopSocket.bind(('127.0.0.1', self.stopPort))
        (self.pubKey, self.privKey) = asymmetricKeying.generateKeys()

        self.i = 0

    def listen(self):
        self.serverSocket.listen(64)
        connectionSocket, addr = self.serverSocket.accept()
        rcvdContent = connectionSocket.recv(1024)

        #check if incoming client wants to make a new connection.If this is the case,it hands the server its name and public key

        #extract public key of sender
        clientPubKey = 0
        #encrypt symmetric key and send to client
        newSymKey = Fernet.generate_key()
        msg = asymmetricKeying.rsa_sendable(newSymKey, self.privKey, clientPubKey)
        connectionSocket.send(msg)

        #extract username of sender
        username = "name"
        # create new connected user
        newUser = User(username)
        newConnectedClient = ConnectedClient(connectionSocket, newSymKey, newUser)
        self.connectedClients.append(newConnectedClient)

        #launch new thread dedicated to connectedClient
        newThread = threading.Thread(target=self.connected_user_listen(), args=(newConnectedClient, None))
        self.currentThreads.append(newThread)
        newThread.start()

        #note that it's possible that multiple clients are logged in to the same user

    def connected_user_listen(self, connectedClient):
        while(connectedClient.loggedIn):

            connectionSocket = connectedClient.connectionSocket

            self.connectionSocket.listen(16)
            rcvdContent = self.connectionSocket.recv(1024)
            rcvdContent = asymmetricKeying.rsa_receive(rcvdContent, connectedClient.pubKey, self.privKey)

            #extract conversation id and content from rcvdContent
            #string has following form: id-content, so split at first occurence of "-"
            (id, content)=rcvdContent.split("-", 1)

            id=int(id)

            sender = connectedClient.user
            message = Message(sender, content)

            newConversation = True

            #check if message id is in existing conversations
            for conversation in self.conversations:
                if id == conversation.id:
                    #conversation already exists

                    #save message in conversation
                    conversation.add_message(message)

                    #find all the receivers
                    members = conversation.members

                    newConversation = False
                    break

            if newConversation:
                #conversation does not yet exist
                members = [sender]

                receiverNames = []
                #fetch names of receivers from key server based on conversation id


                for receiverName in receiverNames:
                    members.append(User(receiverName))

                newConversation = Conversation(members, id)
                newConversation.add_message(message)

            #send message to all receivers

            for receiver in members:
                #note that the sender is also a receiver, since it's possible that the sender is logged in at multiple clients
                for tempConnectedClient in self.connectedClients:
                    if receiver == tempConnectedClient.user and tempConnectedClient != connectedClient:
                        message = asymmetricKeying.rsa_sendable(message, self.privKey, tempConnectedClient.pubKey)
                        tempConnectedClient.connectionSocket.send(message)

    def listen_silently(self):

        if self.i == 0:
            print("listening...")
            self.serverSocket.listen(64)
            self.connectionSocket, addr = self.serverSocket.accept()
            rcvdContent = self.connectionSocket.recv(1024)
            print("recieved!")
            print(rcvdContent.decode("utf-8"))
            self.i = self.i+1
            return rcvdContent.decode("utf-8"), addr

        else:
            print("waf")
            self.serverSocket.listen(64)
            rcvdContent = self.connectionSocket.recv(1024)
            print(rcvdContent.decode("utf-8"))
            return rcvdContent.decode("utf-8"), (0,0)


    def close(self):
        #perhaps send close message to all connectedClients

        for thread in self.currentThreads:
            thread.join()

    def stop_listening(self):
        b = bytes('1', 'utf-8')
        self.stopSocket.connect((self.server_ip, self.server_socket))
        self.stopSocket.send(b)
        self.stopSocket.close()