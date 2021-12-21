import json
import errno
import re
import threading
import time
from math import floor
from random import getrandbits
from socket import *
import asymmetric_keying
import symmetric_keying
from byte_stream_type import *
from cryptography.fernet import Fernet
from byte_stream import *
from server import ConnectedClient
from user import User
from asymmetric_keying import *
from symmetric_keying import *


class KeyServer:
    server_port = None
    server_socket = None
    stop_socket = None
    pub_key = None
    priv_key = None
    current_threads = None
    conversationKeys = None  # tuple of (id, symmetric key)

    def __init__(self):

        self.server_port = 12002
        self.stop_port = 12013
        self.server_ip = '127.0.0.1'

        self.server_socket = socket(AF_INET,
                                    SOCK_STREAM)  # AF_INET = Address Family, Internet Protocol (v4) -> ipv4 addresses will connect to this socket.

        # SOCK_STREAM connection oriented -> two-way byte streams
        self.stop_socket = socket(AF_INET, SOCK_STREAM)
        self.server_socket.bind(('127.0.0.1', self.server_port))  # '' contains addresses, when empty it means all
        #self.stop_socket.bind(('127.0.0.1', self.stop_port))

        (self.pub_key, self.priv_key) = generate_keys()

        self.current_threads = []
        self.connected_clients = []
        self.stop_all_threads = False

        self.username_password_pairs = []  # already registered users
        #self.database = dict()  #{"login": ["password", [("id1", "key1"), ("id2", "key2")]]}

        f_key = open("serverCommonKey.txt",'rb')
        self.server_common_key = f_key.read()
        f_key.close()

        self.database = []
        self.conversation_keys = dict()

        broadcast_thread = threading.Thread(target = self.broadcast_addr)
        broadcast_thread.start()
        self.current_threads.append(broadcast_thread)

    def broadcast_addr(self):
        interfaces = getaddrinfo(host=gethostname(), port=None, family=AF_INET)
        allips = [ip[-1][0] for ip in interfaces]

        msg = "KS_Addr" + ";;;" + self.server_ip + ";;;" + str(self.server_port)
        msgb = msg.encode("ascii")

        time.sleep(0.2)

        while True:
            if self.stop_all_threads:
                break

            for ip in allips:
                sock = socket(AF_INET, SOCK_DGRAM, IPPROTO_UDP)  # UDP
                sock.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)
                try:
                    sock.bind((ip, 0))
                    sock.sendto(msgb, ("255.255.255.255", 5005))
                    sock.close()
                    time.sleep(0.37)
                except error as e:
                    if e.errno == errno.EADDRINUSE:
                        print("KS can't listen on broadcast: already in use")
                    sock.close()
                    time.sleep(0.1)


    def listen(self):
        self.server_socket.listen(64)
        connection_socket, addr = self.server_socket.accept()
        rcvd_content = connection_socket.recv(1024)

        # check if incoming client wants to make a new connection. If this is the case, it hands the server its public key first
        byte_stream_in = ByteStream(rcvd_content)

        if byte_stream_in.messageType == ByteStreamType.stoplistening:
            pass

        elif byte_stream_in.messageType == ByteStreamType.keyrequest:
            client_pub_key = string_to_pubkey(byte_stream_in.content)
            print("KS receivers client pubkey:")
            print(client_pub_key)

            print("KS sends own pubkey:")
            print(self.pub_key)
            # send own public key to client
            byte_stream_out = ByteStream(ByteStreamType.pubkeyanswer, self.pub_key)
            connection_socket.send(byte_stream_out.outStream)  # send own public key

            # encrypt symmetric key and send to client
            new_sym_key = Fernet.generate_key()
            print("KS sends symkey:")
            print(new_sym_key)
            msg_bs = ByteStream(ByteStreamType.symkeyanswer, new_sym_key)
            msg = rsa_sendable(msg_bs.outStream, self.priv_key, client_pub_key)
            print("KS sends symkey, encrypted")
            print(msg)
            connection_socket.send(msg)

            #create new connected client
            new_connected_client = ConnectedClient(connection_socket, new_sym_key, client_pub_key)
            self.connected_clients.append(new_connected_client)


            # launch new thread dedicated to connected_client
            new_thread = threading.Thread(target=self.connected_client_listen, args=(new_connected_client,))
            self.current_threads.append(new_thread)
            new_thread.start()




        #new_thread = threading.Thread(target=self.handle_message, args=(rcvd_content, connection_socket,))
        #new_thread.start()
        #self.current_threads.append(new_thread)

    def listen_for_password(self, connection_socket):
        rcvd_content = connection_socket.recv(1024)
        print("content rec listen for password")
        if rcvd_content != b"":
            print("content not empty listen for password")
            print(rcvd_content)
            self.handle_message(rcvd_content, connection_socket)

    def connected_client_listen(self, connected_client):
        while connected_client.active:

            if self.stop_all_threads:
                break

            connection_socket = connected_client.connection_socket
            rcvd = connection_socket.recv(1024)
            print("RECEIVED")
            rcvd = symm_decrypt(rcvd, connected_client.symKey)
            print(rcvd)
            byte_stream_in = ByteStream(rcvd)
            type = byte_stream_in.messageType
            content = byte_stream_in.content

            if type == ByteStreamType.registerrequest:
                print(type)
                print(content)
                (username, password) = content.split(' - ', 1)
                if self.check_existence_of_account(username):
                    print("EXISTS")
                    # raise CustomError(ServerErrorTypes.ServerErrorType.AccountAlreadyExists)
                    answer_bs = ByteStream(byte_stream_type.ByteStreamType.registeranswer, "failed")
                else:
                    print("DOES NOT EXIST")
                    print(username)
                    print(password)
                    self.database.append((username, password))
                    sign = symm_encrypt(username.encode('ascii'), self.server_common_key)
                    answer_bs = ByteStream(byte_stream_type.ByteStreamType.registeranswer, str(sign))
                    print("Encrypted Username:", str(sign))

                out = symm_encrypt(answer_bs.outStream, connected_client.symKey)
                connection_socket.send(out)

            elif type == ByteStreamType.loginrequest:
                user_exists = False
                username = content
                for name_pw_pair in self.database:
                    print(self.database)
                    if name_pw_pair[0] == username:
                        # the user exist
                        user_exists = True

                if user_exists:
                    answer_bs = ByteStream(byte_stream_type.ByteStreamType.passwordrequest, "sendpassword")
                    new_user = User(username)
                    connected_client.set_user(new_user) #notice: password not yet given, so client isn't able yet to receive keys

                else:
                    answer_bs = ByteStream(byte_stream_type.ByteStreamType.loginanswer, "usernonexistent")
                out = symm_encrypt(answer_bs.outStream, connected_client.symKey)
                connection_socket.send(out)

            elif type == ByteStreamType.passwordanswer:
                password = content
                password_correct = False
                user = connected_client.user
                username = user.username

                for temp in self.database:
                    if temp[0] == username and password == temp[1]:
                        password_correct = True
                        break

                if password_correct:
                    sign = symm_encrypt(username.encode('ascii'), self.server_common_key)
                    answer_bs = ByteStream(byte_stream_type.ByteStreamType.passwordcorrect, str(sign))

                    new_user = User(connected_client.user.username, password)
                    connected_client.set_user(new_user)  # user set with password, client can obtain keys
                else:
                    print("password incorrect!!")
                    answer_bs = ByteStream(byte_stream_type.ByteStreamType.passwordwrong, "")

                out = symm_encrypt(answer_bs.outStream, connected_client.symKey)
                connection_socket.send(out)

            elif type == ByteStreamType.newconversation:
                id = content
                conversation_key = Fernet.generate_key()

                self.conversation_keys[id] = conversation_key

                print("KS sends conv symkey: ", str(conversation_key))
                byte_stream_out = ByteStream(ByteStreamType.symkeyanswer, conversation_key)
                out = symm_encrypt(byte_stream_out.outStream, connected_client.symKey)
                connected_client.connection_socket.send(out)

            elif type == ByteStreamType.requestconversationkey:
                ##TODO verify user
                id = content
                conversation_key = self.conversation_keys[id]

                byte_stream_out = ByteStream(ByteStreamType.symkeyanswer, conversation_key)
                out = symm_encrypt(byte_stream_out.outStream, connected_client.symKey)
                connected_client.connection_socket.send(out)

            elif type == ByteStreamType.logout:
                connected_client.user = None


    def get_users(self):
        return self.database

    def get_connected_clients(self):
        return self.connected_clients

    def listen_silently(self):

        self.server_socket.listen(64)
        connection_socket, addr = self.server_socket.accept()
        rcvd_content = connection_socket.recv(1024)

        return rcvd_content.decode("utf-8"), addr
    def store_keys(self):
        ids = self.conversation_keys.keys()
        file = open("conversation_keys.txt", "w")
        file.truncate(0)
        for id in ids:
            #make json string
            json_dict = dict()
            json_dict["id"] = id
            json_dict["key"] = self.conversation_keys[id].decode('ascii')

            json_string = json.dumps(json_dict)
            file.write(json_string + "\n")

        file.close()

    def stop_listening(self):
        self.store_keys()
        b = bytes('1', 'utf-8')
        self.stop_all_threads = True
        self.stop_socket.connect((self.server_ip, self.server_port))
        self.stop_socket.send(b)
        self.stop_socket.close()

        print("KS needs to close ", len(self.current_threads), "threads")
        for thread in self.current_threads:
            thread.join(2)
        print("KS threads closed")

    def get_password(self, login):
        return self.find_in_list(login)[0]
        pass

    def add_user(self, login, password):
        self.database[login] = [password, []]

    def add_key(self, login, id, key):
        self.database[login][1].append((id, key))

    def load(self, location):
        pass

    def write(self, location):
        pass

    def check_existence_of_account(self, username):
        for temp in self.database:
            temp_name = temp[0]
            if temp_name == username:
                return True

        return False

    def find_in_list(self, login):
        return self.database[login]
