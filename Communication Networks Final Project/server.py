from cryptography.fernet import Fernet

import byteStreamType
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
        self.user = None

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
                    self.knownUsers.add(newUser) #doesn't add if already in set

            elif byteStreamIn.messageType == ByteStreamType.loginrequest:
                (username, sign) = rcvdContent.split(" - ", 1)
                print("MAIN SERVER: LOGIN OF:", username)
                sign = sign[2:len(sign)-1]
                decrypted_username = symmetricKeying.symmDecrypt(sign.encode('ascii'), self.serverCommonKey)
                if username.encode('ascii') == decrypted_username:
                    newUser = User(username)
                    connectedClient.set_user(newUser)

            elif byteStreamIn.messageType == ByteStreamType.contactrequest:
                print("CONTACT REQUEST AT MAIN SERVER")
                contacts = ""
                first = True
                for user in self.knownUsers:
                    username = user.username
                    print(connectedClient.user.username)
                    #if username != connectedClient.user.username:
                    #TODO filter in different way
                    if first:
                        contacts = contacts + username
                        first = not first
                    else:
                        contacts = contacts + " - " + username
                print("send: ",contacts)
                byteStreamOut = ByteStream(ByteStreamType.contactanswer, contacts)
                out = symmetricKeying.symmEncrypt(byteStreamOut.outStream, connectedClient.symKey)
                connectionSocket.send(out)

            elif byteStreamIn.messageType == ByteStreamType.newconversation:
                members = rcvdContent.split(" - ")
                print("MS receives members: ", members)
                id = symmetricKeying.hashString(rcvdContent)
                conversation = Conversation(members, id)
                self.conversations.append(conversation)

            elif byteStreamIn.messageType == ByteStreamType.message:
                #extract conversation id and content from rcvdContent
                #string has following form: id-content, so split at first occurence of "-"
                id = rcvdContent[:40]
                msg = rcvdContent[43:]

                print("MS receives msg: ", msg)

                sender = connectedClient.user
                #TODO user is last registered, not last logged in
                message = Message(sender, msg)

                #check if message id is in existing conversations
                for conversation in self.conversations:
                    if id == conversation.id:
                        #save message in conversation
                        conversation.add_message(message)
                        print("conversation changed: ")
                        conversation.printmessages()
                        #find all the receivers
                        members = conversation.members
                        print("conversation members: ", members)
                        break



                byteStreamOut = ByteStream(ByteStreamType.message, str(id) + " - " + sender.username + " - " + msg)
                for receiver in members:
                    #note that the sender is also a receiver, since it's possible that the sender is logged in at multiple clients
                    for tempConnectedClient in self.connectedClients:
                        print(tempConnectedClient.user.username)

                        if tempConnectedClient.user.username != None and receiver == tempConnectedClient.user.username and tempConnectedClient != connectedClient:
                            out = symmetricKeying.symmEncrypt(byteStreamOut.outStream, tempConnectedClient.symKey)
                            print('MS sends message')
                            tempConnectedClient.connectionSocket.send(out)

            elif byteStreamIn.messageType == ByteStreamType.requestmembers:
                id = rcvdContent
                for conv in self.conversations:
                    if id == conv.id:
                        members = conv.members
                        first = True
                        for m in members:
                            if first:
                                first = not first
                                total_string = m
                            else:
                                total_string = total_string + " - " + m

                byteStreamOut = ByteStream(byteStreamType.ByteStreamType.answermembers, total_string)
                out = symmetricKeying.symmEncrypt(byteStreamOut.outStream, connectedClient.symKey)
                connectedClient.connectionSocket.send(out)

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