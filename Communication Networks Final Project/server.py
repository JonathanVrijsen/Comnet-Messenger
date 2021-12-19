from user import User
from socket import *
from conversation import Conversation
from message import Message
import threading
import asymmetricKeying

class ConnectedClient:
    def __init__(self, connectionSocket, pubKey, user):
        self.connectionSocket = connectionSocket
        self.user = user
        self.pubKey = pubKey
        self.loggedIn = True


class Server:
    def __init__(self):
        self.conversations = []
        self.connectedClients = []
        self.currentThreads = []

        self.serverPort = 12000
        self.serverSocket = socket(AF_INET, SOCK_STREAM)
        self.serverSocket.bind(('', self.serverPort))
        (self.pubKey, self.privKey) = asymmetricKeying.generateKeys()

    def listen(self):
        self.serverSocket.listen(64)
        connectionSocket, addr = self.serverSocket.accept()
        rcvdContent = connectionSocket.recv(1024)

        #extract username of sender
        username = "name"

        #create new connected user
        newUser = User(username)

        #somehow get public key of sender
        newPubKey = 0

        newConnectedClient=ConnectedClient(connectionSocket, newPubKey, newUser)

        newThread = threading.Thread(target=self.connected_user_listen(), args=(newConnectedClient, None))
        self.currentThreads.append(newThread)
        newThread.start()

        self.connectedClients.append(newConnectedClient)

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

        self.serverSocket.listen(64)
        connectionSocket, addr = self.serverSocket.accept()
        rcvdContent = connectionSocket.recv(1024)

        return rcvdContent.decode("utf-8"), addr

    def close(self):
        #perhaps send close message to all connectedClients

        for thread in self.currentThreads:
            thread.join()
