import hashlib
import threading

import asymmetricKeying
import conversation
import symmetricKeying
from asymmetricKeying import *
from message import Message
from user import User
from socket import *
from RegErrorTypes import *
from byteStream import *
from byteStreamType import *
from cryptography.fernet import Fernet

def hashString(input_string):
    pb = bytes(input_string, 'utf-8')
    hash = hashlib.sha1(pb)
    return hash.hexdigest()

class Client:
    user = None
    server_ip = None
    server_socket = None
    key_server_ip = None
    key_server_socket = None
    conversations = None
    encrypted_username = None

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

        self.currentThreads = []

        self.first_message_to_keyserver()
        self.first_message_to_server()



        #self.clientToKeySocket.send(reg_bs.outStream)
        self.contacts = []
        self.knownconversationkeys = dict()

        self.conversations = []

    def login(self, username, password):
        password = hashString(password) #since only hashed version of password is transmitted
        # send username and password to keyserver
        # if login successful, set current user of client and get conversations from server

        login_bs = ByteStream(ByteStreamType.loginrequest, username)
        out = symmetricKeying.symmEncrypt(login_bs.outStream, self.Keyserver_symkey)
        self.clientToKeySocket.send(out)

        msg = self.clientToKeySocket.recv(1024)
        msg = symmetricKeying.symmDecrypt(msg, self.Keyserver_symkey)
        print(msg)
        login_ans_bs = ByteStream(msg)
        ans_type = login_ans_bs.messageType

        if ans_type == ByteStreamType.passwordrequest:
            # send password
            password_bs = ByteStream(ByteStreamType.passwordanswer, password)
            out = symmetricKeying.symmEncrypt(password_bs.outStream, self.Keyserver_symkey)
            self.clientToKeySocket.send(out)

            msg = self.clientToKeySocket.recv(1024)
            msg = symmetricKeying.symmDecrypt(msg, self.Keyserver_symkey)
            print(msg)
            password_ans_bs = ByteStream(msg)
            ans_type = password_ans_bs.messageType
            if ans_type == ByteStreamType.passwordcorrect:
                self.encrypted_username = password_ans_bs.content
                print("password correct")
                print("encrypted name:", self.encrypted_username)
                self.user = User(username, password)

                byteStreamOut = ByteStream(ByteStreamType.loginrequest, username + " - " + self.encrypted_username)
                out = symmetricKeying.symmEncrypt(byteStreamOut.outStream, self.Mainserver_symkey)
                self.clientToMainSocket.send(out)



                listen_thread = threading.Thread(target = self.listen_to_mainserver)
                listen_thread.start()
                self.currentThreads.append(listen_thread)
                return True
            elif ans_type == ByteStreamType.passwordwrong:
                print("password wrong")

        elif ans_type == ByteStreamType.loginanswer:
            print("user non existent")
            self.user = None

        return False

    def listen_to_mainserver(self):
        rcvd = self.clientToMainSocket.recv(1024)
        rcvd = symmetricKeying.symmDecrypt(rcvd, self.Mainserver_symkey)
        byteStreamIn = ByteStream(rcvd)
        rcvdContent = byteStreamIn.content
        print("received at start ",rcvdContent)
        type = byteStreamIn.messageType

        if type == byteStreamType.ByteStreamType.message:
            id = rcvdContent[:40]
            othercontent = rcvdContent[43:]
            (sendername, msg) = othercontent.split(" - ", 1)

            print("CL gets message:" , msg)

            if not(id in self.knownconversationkeys):
                # ask for key at key server
                byteStreamOut = ByteStream(byteStreamType.ByteStreamType.requestconversationkey, id)
                out = symmetricKeying.symmEncrypt(byteStreamOut.outStream, self.Keyserver_symkey)
                self.clientToKeySocket.send(out)

                rcvd = self.clientToKeySocket.recv(1024)
                rcvd = symmetricKeying.symmDecrypt(rcvd, self.Keyserver_symkey)
                byteStreamIn = ByteStream(rcvd)
                if byteStreamIn.messageType == byteStreamType.ByteStreamType.symkeyanswer:
                    content = byteStreamIn.content
                    conversation_key = symmetricKeying.strToSymkey(content)
                    self.knownconversationkeys[id] = conversation_key

                    byteStreamOut = ByteStream(byteStreamType.ByteStreamType.requestmembers, id)
                    out = symmetricKeying.symmEncrypt(byteStreamOut.outStream, self.Mainserver_symkey)
                    self.clientToMainSocket.send(out)

                    rcvd = self.clientToMainSocket.recv(1024)
                    rcvd = symmetricKeying.symmDecrypt(rcvd, self.Mainserver_symkey)
                    byteStreamIn = ByteStream(rcvd)

                    if byteStreamIn.messageType == byteStreamType.ByteStreamType.answermembers:
                        members = byteStreamIn.content
                        members = members.split(" - ")
                        newconversation = conversation.Conversation(members, id)
                        self.conversations.append(newconversation)


            for conv in self.conversations:
                if id == conv.id:
                    members = conv.members
                    sendernameismmember = False
                    for m in members:
                        membername = m
                        if sendername == membername:
                            sendernameismmember = True
                            sender = m

                    if sendernameismmember:
                        message = Message(User(sender), msg)
                        conv.add_message(message)
                    break

        if byteStreamIn.messageType == ByteStreamType.contactanswer:
            self.contacts = byteStreamIn.content.split(" - ")
            print("recieved: ", self.contacts)
            #TODO add message to conversation



    def register(self, username, password1, password2, password3):

        if password1 != password2 or password1 != password3:
            return RegisterErrorType.NoPasswordMatch
        elif not username:
            return RegisterErrorType.NoUsername
        elif not password1:
            return RegisterErrorType.NoPassword
        else:
            password_hash = hashString(password1)
            reg_bs = ByteStream(ByteStreamType.registerrequest, username + " - " + password_hash)

            if (self.Keyserver_symkey != None):
                print(self.Keyserver_symkey)
                print(reg_bs)
                out = symmetricKeying.symmEncrypt(reg_bs.outStream, self.Keyserver_symkey)
                print("SENT")
                self.clientToKeySocket.send(out)
                ans_bytes = self.clientToKeySocket.recv(1024)
                ans_bytes = symmetricKeying.symmDecrypt(ans_bytes, self.Keyserver_symkey)
                ans_bs = ByteStream(ans_bytes)
                ans = ans_bs.content
                print(ans)
                if ans != "failed":
                    self.encrypted_username = ans
                    print("Received encrypted username:", str(ans))

                    out = username + " - "+str(ans)
                    byteStreamOut = ByteStream(ByteStreamType.registertomain, out)
                    out = byteStreamOut.outStream
                    out = symmetricKeying.symmEncrypt(out, self.Mainserver_symkey)
                    self.clientToMainSocket.send(out)

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

        #wait until server repplies with own public key
        rcvd = self.clientToMainSocket.recv(1024)

        byteStreamIn = ByteStream(rcvd)
        if (byteStreamIn.messageType == ByteStreamType.pubkeyanswer):
            self.Mainserver_pubkey = asymmetricKeying.string_to_pubkey(byteStreamIn.content)
            print("Cl receives KS pubkey:")
            print(self.Mainserver_pubkey)

        rcvd = self.clientToMainSocket.recv(1024)
        print("Cl receives symm key, encrypted")
        print(rcvd)
        rcvd = rsa_receive(rcvd, self.Mainserver_pubkey, self.privKey)
        print(rcvd)
        byteStreamIn = ByteStream(rcvd)
        print(byteStreamIn.messageType)
        if (byteStreamIn.messageType == ByteStreamType.symkeyanswer):
            print(byteStreamIn.content)
            self.Mainserver_symkey = symmetricKeying.strToSymkey(byteStreamIn.content)
            print("Cl decrypts symm key")
            print(self.Mainserver_symkey)

    def first_message_to_keyserver(self):
        byteStreamOut = ByteStream(ByteStreamType.keyrequest, self.pubKey)
        outstream = byteStreamOut.outStream
        print("Cl sends own pubkey:")
        print(self.pubKey)
        self.clientToKeySocket.send(outstream)

        # wait until server repplies with own public key
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

    def send_message(self, members, msg):
        members.append(self.user.username)
        members = sorted(members)
        first = True
        for m in members:
            if first:
                total_string = m
                first = first and (not first)
            else:
                total_string = total_string + " - " + m

        id = hashString(total_string)

        print("CL sends msg: ", msg)
        byteStreamOut = ByteStream(ByteStreamType.message, (id) + " - " + msg)
        out = symmetricKeying.symmEncrypt(byteStreamOut.outStream, self.Mainserver_symkey)
        self.clientToMainSocket.send(out)

    def request_contacts(self):
        req_bs = ByteStream(byteStreamType.ByteStreamType.contactrequest, "")
        out = symmetricKeying.symmEncrypt(req_bs.outStream, self.Mainserver_symkey)
        print("contactrequest sent")
        self.clientToMainSocket.send(out)

    def get_contacts(self):
        return self.contacts

    def start_conversation(self, contact_usernames):
        #contacts = self.get_contacts()

        print(self.user.username)
        contact_usernames.append(self.user.username)
        contact_usernames = sorted(contact_usernames)
        first = True
        for username in contact_usernames:
            if first:
                first = not first
                total_string = username
            else:
                total_string = total_string + " - " + username

        id = hashString(total_string)
        print("Generated conv ID= ",id)
        #start conversation by letting the key server now a key should be created
        byteStreamOut = ByteStream(ByteStreamType.newconversation, id)
        out = symmetricKeying.symmEncrypt(byteStreamOut.outStream, self.Keyserver_symkey)
        self.clientToKeySocket.send(out)

        rcvd = self.clientToKeySocket.recv(1024)
        rcvd = symmetricKeying.symmDecrypt(rcvd, self.Keyserver_symkey)
        byteStreamIn = ByteStream(rcvd)
        if byteStreamIn.messageType == ByteStreamType.symkeyanswer:
            conversationkey = symmetricKeying.strToSymkey(byteStreamIn.content)
            print("Received conv symkey: ", str(conversationkey))
            self.knownconversationkeys[id]=conversationkey

            byteStreamOut = ByteStream(ByteStreamType.newconversation, total_string)
            out = symmetricKeying.symmEncrypt(byteStreamOut.outStream, self.Mainserver_symkey)
            self.clientToMainSocket.send(out)

    def logout(self):
        # go back to begin screen
        user = None
        conversations = None

        # in a way, the keys of the previous user are still saved at the client.
        # so maybe, implement a signal to let the keyServer know that some client has logged out,
        # and hence it should create new keys for the conversations of the client



