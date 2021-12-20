from cryptography.fernet import Fernet

import symmetricKeying
from byteStream import ByteStream
from byteStreamType import ByteStreamType
from user import User
from socket import *
from conversation import Conversation
from message import Message
import threading
import asymmetricKeying

class ConnectedClient:
    user = None

    def __init__(self, connectionSocket, symKey, pubKey):
        self.connectionSocket = connectionSocket
        self.pubKey = pubKey
        self.symKey = symKey
        self.active = True

    def set_user(self, newUser):
        self.user = newUser


class Server:
    def __init__(self):
        self.conversations = []
        self.connectedClients = []
        self.currentThreads = []

        self.knownUsers = set() #empty set (basically list with unique elements)

        self.serverPort = 12100
        self.stopPort = 12101
        self.server_ip = '127.0.0.1'
        self.serverSocket = socket(AF_INET, SOCK_STREAM)
        self.stopSocket = socket(AF_INET, SOCK_STREAM)
        self.serverSocket.bind(('127.0.0.1', self.serverPort))
        self.stopSocket.bind(('127.0.0.1', self.stopPort))

        (self.pubKey, self.privKey) = asymmetricKeying.generateKeys()
        fkey = open("serverCommonKey.txt",'rb')
        self.serverCommonKey = fkey.read()

        self.i = 0

    def listen(self):
        self.serverSocket.listen(64)
        connectionSocket, addr = self.serverSocket.accept()
        rcvdContent = connectionSocket.recv(1024)

        #check if incoming client wants to make a new connection. If this is the case, it hands the server its public key first
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

        # create new connected client
        newConnectedClient = ConnectedClient(connectionSocket, newSymKey, clientPubKey)
        self.connectedClients.append(newConnectedClient)

        # launch new thread dedicated to connectedClient
        newThread = threading.Thread(target=self.connected_user_listen, args=(newConnectedClient,))
        self.currentThreads.append(newThread)
        newThread.start()

        #note that it's possible that multiple clients are logged in to the same user

    def connected_user_listen(self, connectedClient):
        while(connectedClient.active):
            connectionSocket = connectedClient.connectionSocket

            rcvd = connectionSocket.recv(1024)
            rcvd = symmetricKeying.symmDecrypt(rcvd, connectedClient.symKey)
            byteStreamIn = ByteStream(rcvd)
            rcvdContent = byteStreamIn.content

            if byteStreamIn.messageType == ByteStreamType.registertomain:
                (username, sign) = rcvdContent.split(" - ", 1)
                print("MAIN SERVER: REGISTER TO MAIN")
                print(username)
                print(sign)
                sign = sign[2:len(sign)-1]
                print(sign)


                decrypted_username = symmetricKeying.symmDecrypt(sign.encode('ascii'), self.serverCommonKey)

                if username.encode('ascii') == decrypted_username:
                    print("USER RGISTERED AT MAIN SERVER:", username)
                    newUser = User(username)
                    connectedClient.set_user(newUser)
                    self.knownUsers.add(newUser) #doesn't add if already in set

            #TODO add message to bytestreamtypes
            elif byteStreamIn.messageType == ByteStreamType.message:
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
        self.stopSocket.connect((self.server_ip, self.serverPort))
        self.stopSocket.send(b)
        self.stopSocket.close()