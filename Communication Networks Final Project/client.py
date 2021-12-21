import hashlib
import threading
from conversation import *
from asymmetric_keying import *
from symmetric_keying import *
from message import Message
from user import User
from socket import *
from reg_error_types import *
from byte_stream import *
from byte_stream_type import *
import time
import errno


def hash_string(input_string):
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
        (self.pub_key, self.priv_key) = generate_keys()

        self.currentThreads = []
        self.all_conversation_members = []
        self.all_conversations_received = False

        self.contacts = []
        self.known_conversation_keys = dict()

        self.conversations = []

        self.stop_all_threads = False

        self.KS_found = False
        self.MS_found = False

        self.key_server_ip = None
        self.key_server_socket = None

        broadcast_thread = threading.Thread(target=self.listen_for_broadcast)
        broadcast_thread.start()
        self.currentThreads.append(broadcast_thread)

        while not(self.KS_found and self.MS_found):
            time.sleep(1)




        self.clientToMainSocket = socket(AF_INET, SOCK_STREAM)

        self.clientToMainSocket.connect((self.server_ip, self.server_socket))
        self.mainserver_pubkey = None
        self.mainserver_symkey = None

        self.clientToKeySocket = socket(AF_INET, SOCK_STREAM)
        self.clientToKeySocket.connect((self.key_server_ip, self.key_server_socket))
        self.keyserver_pubkey = ""
        self.keyserver_symkey = ""



        self.first_message_to_keyserver()
        self.first_message_to_server()

        # self.clientToKeySocket.send(reg_bs.outStream)


    def listen_for_broadcast(self):
        while not(self.KS_found and self.MS_found):
            sock = socket(AF_INET, SOCK_DGRAM)
            sock.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)
            try:
                sock.bind(("0.0.0.0", 5005))
                data, addr = sock.recvfrom(1024)
                sock.close()
                data = data.decode("utf-8")
                data = data.split(";;;")
                if data[0] == "KS_Addr":
                    self.KS_found = True
                    self.key_server_ip = data[1]
                    self.key_server_socket = int(data[2])
                elif data[0] == "MS_Addr":
                    self.MS_found = True
                    self.server_ip = data[1]
                    self.server_socket = int(data[2])
                time.sleep(0.27)
            except error as e:
                if e.errno == errno.EADDRINUSE:
                sock.close()
                time.sleep(0.1)



    def login(self, username, password):
        password = hash_string(password)  # since only hashed version of password is transmitted
        # send username and password to keyserver
        # if login successful, set current user of client and get conversations from server

        login_bs = ByteStream(ByteStreamType.loginrequest, username)
        out = symm_encrypt(login_bs.outStream, self.keyserver_symkey)
        self.clientToKeySocket.send(out)

        msg = self.clientToKeySocket.recv(1024)
        msg = symm_decrypt(msg, self.keyserver_symkey)
        login_ans_bs = ByteStream(msg)
        ans_type = login_ans_bs.messageType

        if ans_type == ByteStreamType.passwordrequest:
            # send password
            password_bs = ByteStream(ByteStreamType.passwordanswer, password)
            out = symm_encrypt(password_bs.outStream, self.keyserver_symkey)
            self.clientToKeySocket.send(out)

            msg = self.clientToKeySocket.recv(1024)
            msg = symm_decrypt(msg, self.keyserver_symkey)
            password_ans_bs = ByteStream(msg)
            ans_type = password_ans_bs.messageType
            if ans_type == ByteStreamType.passwordcorrect:
                self.encrypted_username = password_ans_bs.content
                self.user = User(username, password)

                byte_stream_out = ByteStream(ByteStreamType.loginrequest, username + " - " + self.encrypted_username)
                out = symm_encrypt(byte_stream_out.outStream, self.mainserver_symkey)
                self.clientToMainSocket.send(out)

                listen_thread = threading.Thread(target=self.listen_to_mainserver)
                listen_thread.start()
                self.currentThreads.append(listen_thread)
                return True
            elif ans_type == ByteStreamType.passwordwrong:
                pass

        elif ans_type == ByteStreamType.loginanswer:
            self.user = None

        return False

    def listen_to_mainserver(self):
        while True:

            if self.stop_all_threads:
                break

            rcvd = self.clientToMainSocket.recv(1024)
            rcvd = symm_decrypt(rcvd, self.mainserver_symkey)
            byte_stream_in = ByteStream(rcvd)
            rcvd_content = byte_stream_in.content
            type = byte_stream_in.messageType

            if type == byte_stream_type.ByteStreamType.message:
                id = rcvd_content[:40]
                other_content = rcvd_content[43:]
                (sender_name, msg) = other_content.split(" - ", 1)

                if not (id in self.known_conversation_keys):
                    self.new_conversation(id)

                msg = msg[2:len(msg)-1]
                msg = symm_decrypt(msg.encode('ascii'), self.known_conversation_keys[id])
                msg = msg.decode('ascii')

                for conv in self.conversations:
                    if id == conv.id:
                        members = conv.members
                        sender_name_is_member = False
                        for m in members:
                            member_name = m
                            if sender_name == member_name:
                                sender_name_is_member = True
                                sender = m
                        if sender_name_is_member:
                            message = Message(sender, msg)
                            conv.add_message(message)
                        break
            elif byte_stream_in.messageType == ByteStreamType.contactanswer:
                self.contacts = byte_stream_in.content.split(" - ")
                self.contacts.remove(self.user.username)
                # TODO add message to conversation

            elif byte_stream_in.messageType == byte_stream_type.ByteStreamType.answerallids:
                id_array = byte_stream_in.content
                ids = id_array.split(" - ")
                self.conversations.clear()
                self.all_conversation_members.clear()
                for id in ids:

                    conversation = self.get_one_conversation(id)
                    members = conversation.members

                    first = True
                    for member in members:
                        if member != self.user.username:
                            if first:
                                conversation_members = member
                                first = first and (not first) or not first
                            else:
                                conversation_members = conversation_members + ", " + member
                    self.all_conversation_members.append(conversation_members)
                    self.conversations.append(conversation)

                self.all_conversations_received = True

    def get_messages(self, contact):
        contact.append(self.user.username)
        asked_members = contact
        asked_members = sorted(asked_members)
        for conv in self.conversations:
            if sorted(conv.members) == asked_members:
                ans = []
                for mes in conv.messages:
                    ans.append(mes.sender + ": " + mes.content)
                return ans

    def new_conversation(self, id):
        # ask for key at key server
        byte_stream_out = ByteStream(byte_stream_type.ByteStreamType.requestconversationkey, id)
        out = symm_encrypt(byte_stream_out.outStream, self.keyserver_symkey)
        self.clientToKeySocket.send(out)

        rcvd = self.clientToKeySocket.recv(1024)
        rcvd = symm_decrypt(rcvd, self.keyserver_symkey)
        byte_stream_in = ByteStream(rcvd)
        if byte_stream_in.messageType == byte_stream_type.ByteStreamType.symkeyanswer:
            content = byte_stream_in.content
            conversation_key = str_to_symmkey(content)
            self.known_conversation_keys[id] = conversation_key

            # ask main server for members in conversation
            byte_stream_out = ByteStream(byte_stream_type.ByteStreamType.requestmembers, id)
            out = symm_encrypt(byte_stream_out.outStream, self.mainserver_symkey)
            self.clientToMainSocket.send(out)

            rcvd = self.clientToMainSocket.recv(1024)
            rcvd = symm_decrypt(rcvd, self.mainserver_symkey)
            byte_stream_in = ByteStream(rcvd)

            if byte_stream_in.messageType == byte_stream_type.ByteStreamType.answermembers:
                members = byte_stream_in.content
                members = members.split(" - ")
                new_conversation = Conversation(members, id)
                self.conversations.append(new_conversation)

    def register(self, username, password1, password2, password3):

        if password1 != password2 or password1 != password3:
            return RegisterErrorType.NoPasswordMatch
        elif not username:
            return RegisterErrorType.NoUsername
        elif not password1:
            return RegisterErrorType.NoPassword
        else:
            password_hash = hash_string(password1)
            reg_bs = ByteStream(ByteStreamType.registerrequest, username + " - " + password_hash)

            if self.keyserver_symkey != None:
                out = symm_encrypt(reg_bs.outStream, self.keyserver_symkey)
                self.clientToKeySocket.send(out)
                ans_bytes = self.clientToKeySocket.recv(1024)
                ans_bytes = symm_decrypt(ans_bytes, self.keyserver_symkey)
                ans_bs = ByteStream(ans_bytes)
                ans = ans_bs.content
                if ans != "failed":
                    self.encrypted_username = ans

                    out = username + " - " + str(ans)
                    byte_stream_out = ByteStream(ByteStreamType.registertomain, out)
                    out = byte_stream_out.outStream
                    out = symm_encrypt(out, self.mainserver_symkey)
                    self.clientToMainSocket.send(out)

                    return RegisterErrorType.NoError
                else:
                    return RegisterErrorType.UsernameAlreadyInUse

    def get_server_information(self):
        return '127.0.0.1', 12100, '127.0.0.1', 12002

    def get_conversations(self):
        # request all the user's conversation from the server

        # first: get all message id's of which the user is a member
        byte_stream_out = ByteStream(byte_stream_type.ByteStreamType.requestallids, "")
        out = symm_encrypt(byte_stream_out.outStream, self.mainserver_symkey)
        self.clientToMainSocket.send(out)

        while not self.all_conversations_received:
            time.sleep(0.1)

        self.all_conversations_received = False
        return self.all_conversation_members

    def get_one_conversation(self, id):
        byte_stream_out = ByteStream(byte_stream_type.ByteStreamType.getconversation, id)
        out = symm_encrypt(byte_stream_out.outStream, self.mainserver_symkey)
        self.clientToMainSocket.send(out)

        rcvd = self.clientToMainSocket.recv(1024)
        rcvd = symm_decrypt(rcvd, self.mainserver_symkey)
        byte_stream_in = ByteStream(rcvd)
        if byte_stream_in.messageType == ByteStreamType.conversation:
            encoded_conversation = byte_stream_in.content
            conv = Conversation(None, None)
            conv.decode_conversation(encoded_conversation)

            for message in conv.messages:
                if not (conv.id in self.known_conversation_keys):
                    self.new_conversation(conv.id)
                message.content = message.content[2:len(message.content)-1]
                message.content = symm_decrypt(message.content.encode('ascii'), self.known_conversation_keys[conv.id])
                message.content = message.content.decode('ascii')
            return conv

    def first_message_to_server(self):
        byte_stream_out = ByteStream(ByteStreamType.keyrequest, self.pub_key)
        out_stream = byte_stream_out.outStream
        self.clientToMainSocket.send(out_stream)

        # wait until server replies with own public key
        rcvd = self.clientToMainSocket.recv(1024)

        byte_stream_in = ByteStream(rcvd)
        if byte_stream_in.messageType == ByteStreamType.pubkeyanswer:
            self.mainserver_pubkey = string_to_pubkey(byte_stream_in.content)

        rcvd = self.clientToMainSocket.recv(1024)
        rcvd = rsa_receive(rcvd, self.mainserver_pubkey, self.priv_key)
        byte_stream_in = ByteStream(rcvd)
        if byte_stream_in.messageType == ByteStreamType.symkeyanswer:
            self.mainserver_symkey = str_to_symmkey(byte_stream_in.content)

    def first_message_to_keyserver(self):
        byte_stream_out = ByteStream(ByteStreamType.keyrequest, self.pub_key)
        out_stream = byte_stream_out.outStream
        self.clientToKeySocket.send(out_stream)

        # wait until server replies with own public key
        rcvd = self.clientToKeySocket.recv(1024)

        byte_stream_in = ByteStream(rcvd)
        if byte_stream_in.messageType == ByteStreamType.pubkeyanswer:
            self.keyserver_pubkey = string_to_pubkey(byte_stream_in.content)

        rcvd = self.clientToKeySocket.recv(1024)
        rcvd = rsa_receive(rcvd, self.keyserver_pubkey, self.priv_key)
        byte_stream_in = ByteStream(rcvd)
        if byte_stream_in.messageType == ByteStreamType.symkeyanswer:
            self.keyserver_symkey = str_to_symmkey(byte_stream_in.content)

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

        id = hash_string(total_string)

        for conversation in self.conversations:
            if id == conversation.id:
                # save message in conversation
                conversation.add_message(Message(self.user.username, msg))

        conversation_key = self.known_conversation_keys[id]
        msg = symm_encrypt(msg.encode('ascii'), conversation_key)
        byte_stream_out = ByteStream(ByteStreamType.message, id + " - " + str(msg))
        out = symm_encrypt(byte_stream_out.outStream, self.mainserver_symkey)
        self.clientToMainSocket.send(out)

    def request_contacts(self):
        req_bs = ByteStream(byte_stream_type.ByteStreamType.contactrequest, "")
        out = symm_encrypt(req_bs.outStream, self.mainserver_symkey)
        self.clientToMainSocket.send(out)

    def get_contacts(self):

        return self.contacts

    def start_conversation(self, contact_usernames):
        # contacts = self.get_contacts()

        contact_usernames.append(self.user.username)
        contact_usernames = sorted(contact_usernames)
        first = True
        for username in contact_usernames:
            if first:
                first = not first
                total_string = username
            else:
                total_string = total_string + " - " + username

        id = hash_string(total_string)
        # start conversation by letting the key server now a key should be created
        byte_stream_out = ByteStream(ByteStreamType.newconversation, id)
        out = symm_encrypt(byte_stream_out.outStream, self.keyserver_symkey)
        self.clientToKeySocket.send(out)

        rcvd = self.clientToKeySocket.recv(1024)
        rcvd = symm_decrypt(rcvd, self.keyserver_symkey)
        byte_stream_in = ByteStream(rcvd)
        if byte_stream_in.messageType == ByteStreamType.symkeyanswer:
            conversation_key = str_to_symmkey(byte_stream_in.content)
            self.known_conversation_keys[id] = conversation_key

            byte_stream_out = ByteStream(ByteStreamType.newconversation, total_string)
            out = symm_encrypt(byte_stream_out.outStream, self.mainserver_symkey)
            self.clientToMainSocket.send(out)

    def log_out(self):
        #logout at keyserver and server
        byteStreamOut = ByteStream(ByteStreamType.logout, "logout")
        out1 = symm_encrypt(byteStreamOut.outStream, self.mainserver_symkey)
        self.clientToMainSocket.send(out1)
        # go back to begin screen
        user = None
        conversations = None


    def stop_client(self):
        self.stop_all_threads = True
        for thread in self.currentThreads:
            thread.join(2)


