import json
import errno
import os
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
        self.load_keys()
        self.load_registered_users()

        broadcast_thread = threading.Thread(target = self.broadcast_addr)
        broadcast_thread.start()
        self.current_threads.append(broadcast_thread)



    def broadcast_addr(self):
        interfaces = getaddrinfo(host=getghostname(), port=None, family=AF_INET)
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
                    sock.close()
                    time.sleep(0.1)

    def load_keys(self):
        if os.path.isfile("conversation_keys.txt"):
            f = open("conversation_keys.txt", "r")
            json_keys = f.read().splitlines()
            f.close()
            if len(json_keys) > 0:
                for json_key in json_keys:
                    pair = json.loads(json_key)
                    id = pair["id"]
                    key = pair["key"]
                    self.conversation_keys[id] = str(key)

    def load_registered_users(self):
        if os.path.isfile("registered_users.txt"):
            f = open("registered_users.txt", "r")
            json_string = json.loads(f.read())
            f.close()
            for pair in json_string:
                self.database.append((pair[0], pair[1]))

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

            # send own public key to client
            byte_stream_out = ByteStream(ByteStreamType.pubkeyanswer, self.pub_key)
            connection_socket.send(byte_stream_out.outStream)  # send own public key

            # encrypt symmetric key and send to client
            new_sym_key = Fernet.generate_key()

            msg_bs = ByteStream(ByteStreamType.symkeyanswer, new_sym_key)
            msg = rsa_sendable(msg_bs.outStream, self.priv_key, client_pub_key)

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
        if rcvd_content != b"":
            self.handle_message(rcvd_content, connection_socket)

    def connected_client_listen(self, connected_client):
        connected_client_logged_in = False
        while connected_client.active:
            if self.stop_all_threads:
                break

            connection_socket = connected_client.connection_socket
            rcvd = connection_socket.recv(1024)
            rcvd = symm_decrypt(rcvd, connected_client.symKey)
            byte_stream_in = ByteStream(rcvd)
            type = byte_stream_in.messageType
            content = byte_stream_in.content

            if type == ByteStreamType.registerrequest:
                (username, password) = content.split(' - ', 1)
                if self.check_existence_of_account(username):
                    # raise CustomError(ServerErrorTypes.ServerErrorType.AccountAlreadyExists)
                    answer_bs = ByteStream(byte_stream_type.ByteStreamType.registeranswer, "failed")
                else:
                    self.database.append((username, password))
                    sign = symm_encrypt(username.encode('ascii'), self.server_common_key)
                    answer_bs = ByteStream(byte_stream_type.ByteStreamType.registeranswer, str(sign))

                out = symm_encrypt(answer_bs.outStream, connected_client.symKey)
                connection_socket.send(out)

            elif type == ByteStreamType.loginrequest:
                user_exists = False
                username = content
                for name_pw_pair in self.database:
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
                    connected_client_logged_in = True
                    new_user = User(connected_client.user.username, password)
                    connected_client.set_user(new_user)  # user set with password, client can obtain keys
                else:
                    answer_bs = ByteStream(byte_stream_type.ByteStreamType.passwordwrong, "")

                out = symm_encrypt(answer_bs.outStream, connected_client.symKey)
                connection_socket.send(out)

            elif type == ByteStreamType.newconversation:
                if connected_client_logged_in:
                    id = content
                    conversation_key = Fernet.generate_key()

                    self.conversation_keys[id] = conversation_key

                    byte_stream_out = ByteStream(ByteStreamType.symkeyanswer, conversation_key)
                    out = symm_encrypt(byte_stream_out.outStream, connected_client.symKey)
                    connected_client.connection_socket.send(out)

            elif type == ByteStreamType.requestconversationkey:
                if connected_client_logged_in:
                    id = content
                    conversation_key = self.conversation_keys[id]

                    byte_stream_out = ByteStream(ByteStreamType.symkeyanswer, conversation_key)
                    out = symm_encrypt(byte_stream_out.outStream, connected_client.symKey)
                    connected_client.connection_socket.send(out)

            elif type == ByteStreamType.logout:
                connected_client_logged_in = False
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
        if len(ids) > 0:
            file = open("conversation_keys.txt", "w")
            file.truncate(0)
            for id in ids:
                #make json string
                json_dict = dict()
                json_dict["id"] = id
                if not isinstance(self.conversation_keys[id], str):
                    json_dict["key"] = self.conversation_keys[id].decode('ascii')
                else:
                    json_dict["key"]=self.conversation_keys[id]

                json_string = json.dumps(json_dict)
                file.write(json_string + "\n")

            file.close()

    def store_users(self):
        if len(self.database) > 0:
            json_string = json.dumps(self.database)
            f = open("registered_users.txt", "w")
            f.truncate(0)
            f.write(json_string)
            f.close()

    def stop_listening(self):
        self.store_keys()
        self.store_users()
        b = bytes('1', 'utf-8')
        self.stop_all_threads = True
        self.stop_socket.connect((self.server_ip, self.server_port))
        self.stop_socket.send(b)
        self.stop_socket.close()

        for thread in self.current_threads:
            thread.join(2)

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
