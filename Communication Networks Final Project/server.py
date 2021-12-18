from user import User
from socket import *
from conversation import Conversation
from message import Message
import threading
import asymmetricKeying


class ConnectedUser:
    def __int__(self, connectionSocket, pubKey, user):
        self.connectionSocket = connectionSocket
        self.user = user
        self.pubKey=pubKey


class Server:
    def __init__(self):
        self.conversations = []
        self.connectedUsers_and_threat = []

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

        newConnectedUser=ConnectedUser(connectionSocket, newPubKey, newUser)

        newThreat = threading.Thread(target=self.connected_user_listen(), args=(newConnectedUser, None))
        newThreat.start()

        self.connectedUsers_and_threat.append((newConnectedUser, newThreat))

        #note that it's possible that multiple clients are logged in to the same user

    def connected_user_listen(self, connectedUser):
        while(True):

            connectionSocket = connectedUser.connectionSocket

            self.connectionSocket.listen(16)
            rcvdContent = self.connectionSocket.recv(1024)

            rcvdContent = asymmetricKeying.rsa_receive(rcvdContent, connectedUser.pubKey, self.privKey)


            sender = connectedUser.user

            #extract conversation id and content

            content = ""
            message = Message(sender, content)

            receiverNames = []
            id = 0
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
                members=[sender]
                for receiverName in receiverNames:
                    members.append(User(receiverName))

                newConversation=Conversation(members, id)
                newConversation.add_message(message)

            #send message to all receivers

            for receiver in members:
                #note that the sender is also a receiver, since it's possible that the sender is logged in at multiple clients
                for tempConnectedUser in self.connectedUsers:
                    if receiver == tempConnectedUser.user and tempConnectedUser.connectionSocket != connectedUser.connectionSocket:
                        message=asymmetricKeying.rsa_sendable(message, self.privKey, tempConnectedUser.pubKey)
                        tempConnectedUser.connectionSocket.send(message)