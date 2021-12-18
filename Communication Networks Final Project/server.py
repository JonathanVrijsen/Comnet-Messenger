from user import User
from socket import *
from conversation import Conversation
from message import Message
import threading
import asymmetricKeying


# class connectedUser:
#     def __int__(self, connectionSocket, user):
#         self.connectionSocket = connectionSocket
#         self.user = user
#         self.listenThread = threading.Thread(target=self.listen())
#         self.listenThread.start()
#
#     def listen(self):
#         while(True):
#             self.connectionSocket.listen(16)
#             rcvdContent = self.connectionSocket.recv(1024)


class Server:
    def __init__(self):
        self.conversations = []
        self.connectedUsers = []

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
        newThreat = threading.Thread(target=self.connected_user_listen(), args=(connectionSocket, newUser , None))
        newConnectedUser = (connectionSocket, newUser, newThreat)
        self.connectedUsers.append(newConnectedUser)

        #note that it's possible that multiple clients are logged in to the same user

        newConnectedUser(2).start()

    def connected_user_listen(self, connectionSocket, user):
        while(True):
            self.connectionSocket.listen(16)
            totalRcvdContent = self.connectionSocket.recv(1024)

            #split totalRcvdContent into signature (always 128 bytes long) and the rcvdContent

            rcvdContent = asymmetricKeying.decrypt(rcvdContent, self.privKey)

            if asymmetricKeying.verifySHA1(rcvdContent, signature, pubKeySender):
                print('Signature verified')
            else:
                print('Signature not verified')


            sender = user

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
                    receivers = members.remove(sender)

                    newConversation = False
                    break

            if newConversation:
                #conversation does not yet exist
                members=[sender]
                for receiverName in receiverNames:
                    members.append(User(receiverName))

                newConversation=Conversation(members, id)
                newConversation.add_message(message)

                receivers = members.pop(0)

            #send message to all receivers

            for receiver in receivers:
                for connectedUser in self.connectedUsers:
                    if receiver == connectedUser(1): #connectedUser(1) contains the user itself.
                        #send message via socket connectedUser(0)
                        pass