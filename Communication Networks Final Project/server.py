import errno
import os
import time

import json

from cryptography.fernet import Fernet

import byte_stream_type
import symmetric_keying
from byte_stream import ByteStream
from byte_stream_type import ByteStreamType
from user import User
from socket import *
from conversation import Conversation
from message import Message
import threading
import asymmetric_keying
from asymmetric_keying import *
from symmetric_keying import *


class ConnectedClient:
    user = None

    def __init__(self, connection_socket, sym_key, pub_key):
        self.connection_socket = connection_socket
        self.pubKey = pub_key
        self.symKey = sym_key
        self.active = True
        self.user = None

    def set_user(self, new_user):
        self.user = new_user


class Server:
    def __init__(self):
        self.conversations = []
        self.connected_clients = []
        self.current_threads = []

        self.stop_all_threads = False

        self.known_users = set()  # empty set (basically list with unique elements)
        self.load_known_users() #load server state from file
        self.load_conversation()

        self.server_port = 15600
        self.stop_port = 12110
        self.server_ip = '127.0.0.1'
        self.server_socket = socket(AF_INET, SOCK_STREAM)
        self.stop_socket = socket(AF_INET, SOCK_STREAM)
        self.server_socket.bind(('127.0.0.1', self.server_port))

        (self.pub_key, self.priv_key) = generate_keys() #generate the asymmetric keys
        f_key = open("serverCommonKey.txt", 'rb')
        self.serverCommonKey = f_key.read()
        f_key.close()

        self.i = 0

        broadcast_thread = threading.Thread(target=self.broadcast_addr) #start the broadcasting thread
        broadcast_thread.start()
        self.current_threads.append(broadcast_thread)

    def load_known_users(self): #load from file
        if os.path.isfile("known_users_main_server.txt"):
            f = open("known_users_main_server.txt", "r")
            json_string = json.loads(f.read())
            if len(json_string) > 0:
                for username in json_string:
                    self.known_users.add(User(username))
            f.close()

    def load_conversation(self): #load from file
        if os.path.isfile("conversations.txt"):
            f = open("conversations.txt", "r")
            json_string = json.loads(f.read())
            if len(json_string) > 0:
                for conv_dict in json_string:
                    id = conv_dict["id"]
                    json_members = conv_dict["members"]
                    members = json.loads(json_members)
                    conversation = Conversation(members, id)
                    messages = json.loads(conv_dict["messages"])
                    for message in messages:
                        sender = message[0]
                        content = message[1]
                        conversation.add_message(Message(sender, content))
                    self.conversations.append(conversation)

            f.close()


    def broadcast_addr(self): #periodically broadcast the address
        interfaces = getaddrinfo(host=gethostname(), port=None, family=AF_INET)
        allips = [ip[-1][0] for ip in interfaces]

        msg = "MS_Addr" + ";;;" + self.server_ip + ";;;" + str(self.server_port)
        msgb = msg.encode("ascii")

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
                    time.sleep(0.43)
                except error as e:
                    sock.close()
                    time.sleep(0.1)

    def listen(self): #listen for first messages and exchange keys
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

            # create new connected client
            new_connected_client = ConnectedClient(connection_socket, new_sym_key, client_pub_key)
            self.connected_clients.append(new_connected_client)

            # launch new thread dedicated to connected_client
            new_thread = threading.Thread(target=self.connected_client_listen, args=(new_connected_client,))
            self.current_threads.append(new_thread)
            new_thread.start()

        # note that it's possible that multiple clients are logged in to the same user

    def connected_client_listen(self, connected_client): #listen to a specific client
        while connected_client.active:

            if self.stop_all_threads:
                break
            else:
                connection_socket = connected_client.connection_socket

                rcvd = connection_socket.recv(1024)
                rcvd = symm_decrypt(rcvd, connected_client.symKey)
                byte_stream_in = ByteStream(rcvd)
                rcvd_content = byte_stream_in.content

                if byte_stream_in.messageType == ByteStreamType.registertomain: #mainserver is notified of new register, and add's username to database
                    (username, sign) = rcvd_content.split(" - ", 1)

                    sign = sign[2:len(sign) - 1]
                    decrypted_username = symm_decrypt(sign.encode('ascii'), self.serverCommonKey)

                    if username.encode('ascii') == decrypted_username: #check signature

                        new_user = User(username)
                        self.known_users.add(new_user)  # doesn't add if already in set

                elif byte_stream_in.messageType == ByteStreamType.requestallids: #client wants all conversation ids
                    username = connected_client.user.username
                    first = True

                    for conv in self.conversations: #collect all conversation sender is part of
                        members = conv.members
                        if username in members:
                            if first:
                                id_array = str(conv.id)
                                first = first and (not first)
                            else:
                                id_array = id_array + " - " + str(conv.id)
                    if first:
                        id_array = ""

                    byte_stream_out = ByteStream(byte_stream_type.ByteStreamType.answerallids, id_array)
                    out = symm_encrypt(byte_stream_out.outStream, connected_client.symKey)
                    connected_client.connection_socket.send(out)

                elif byte_stream_in.messageType == ByteStreamType.loginrequest: #mainserver is notified of new login and sets the username of this client
                    (username, sign) = rcvd_content.split(" - ", 1)
                    sign = sign[2:len(sign) - 1]
                    decrypted_username = symm_decrypt(sign.encode('ascii'), self.serverCommonKey)
                    if username.encode('ascii') == decrypted_username:
                        new_user = User(username)
                        connected_client.set_user(new_user)

                elif byte_stream_in.messageType == ByteStreamType.contactrequest: #return all registered usernames
                    contacts = ""
                    first = True
                    for user in self.known_users:
                        username = user.username
                        if first:
                            contacts = contacts + username
                            first = not first
                        else:
                            contacts = contacts + " - " + username
                    byte_stream_out = ByteStream(ByteStreamType.contactanswer, contacts)
                    out = symm_encrypt(byte_stream_out.outStream, connected_client.symKey)
                    connection_socket.send(out)

                elif byte_stream_in.messageType == ByteStreamType.newconversation: #server is asked to create a new conversation
                    members = rcvd_content.split(" - ")
                    id = hash_string(rcvd_content)
                    conversation = Conversation(members, id)
                    self.conversations.append(conversation)

                elif byte_stream_in.messageType == ByteStreamType.message: #server receives actual chat message
                    # extract conversation id and content from rcvd_content
                    # string has the following form: id-content, so split at first occurence of "-"
                    id = rcvd_content[:40]
                    msg = rcvd_content[43:]

                    sender = connected_client.user
                    message = Message(sender.username, msg)

                    # check if message id is in existing conversations
                    for conversation in self.conversations:
                        if id == conversation.id:
                            # save message in conversation
                            conversation.add_message(message)
                            # find all the receivers
                            members = conversation.members
                            break

                    byte_stream_out = ByteStream(ByteStreamType.message, str(id) + " - " + sender.username + " - " + msg)
                    for receiver in members:
                        # note that the sender is also a receiver, since it's possible that the sender is logged in at multiple clients
                        for tempConnectedClient in self.connected_clients:

                            if tempConnectedClient.user.username is not None and receiver == tempConnectedClient.user.username and tempConnectedClient != connected_client:
                                out = symm_encrypt(byte_stream_out.outStream, tempConnectedClient.symKey)
                                tempConnectedClient.connection_socket.send(out)

                elif byte_stream_in.messageType == ByteStreamType.requestmembers: #client asks to return all conv members
                    id = rcvd_content
                    client_is_member = False
                    client_name = connected_client.user.username
                    for conv in self.conversations:
                        if id == conv.id:
                            members = conv.members
                            first = True
                            for m in members:
                                if m == client_name:
                                    client_is_member = True

                                if first:
                                    first = not first
                                    total_string = m
                                else:
                                    total_string = total_string + " - " + m
                        break
                    if client_is_member:
                        byte_stream_out = ByteStream(byte_stream_type.ByteStreamType.answermembers, total_string)
                        out = symm_encrypt(byte_stream_out.outStream, connected_client.symKey)
                        connected_client.connection_socket.send(out)

                elif byte_stream_in.messageType == ByteStreamType.getconversation: #clients asks for a full conversation
                    id = byte_stream_in.content
                    for conv in self.conversations:
                        if id == conv.id:
                            encoded_conversation = conv.encode_conversation()
                            byte_stream_out = ByteStream(ByteStreamType.conversation, encoded_conversation)
                            out = symm_encrypt(byte_stream_out.outStream, connected_client.symKey)
                            connection_socket.send(out)
                            break

                elif byte_stream_in.messageType == ByteStreamType.logout:
                    connected_client.user = None

    def get_conv_data(self): #return conversation data to GUI
        ans = []
        for conv in self.conversations:
            users = ""
            first = True
            for user in conv.members:
                if first:
                    users = user
                    first = not first
                else:
                    users = users + ", "+ user

            if len(conv.messages) >0:
                lastmsg = conv.messages[len(conv.messages) - 1].content
            else:
                lastmsg = "None"
            ans.append([conv.id,users,lastmsg])
        return ans

    def get_connected_clients(self):
        return self.connected_clients

    def store_conversations(self): #store all conversation in file on shutdown
        if len(self.conversations) > 0:
            conv_json = []
            for conv in self.conversations:
                conv_json.append(conv.to_json())
            json_string = json.dumps(conv_json)

            file = open("conversations.txt", "w")
            file.write(json_string)
            file.close()

    def store_known_users(self): #store all known users in file on shutdown
        #since JSON cannot serialize sets, I believe
        known_users_list = []
        if len(self.known_users) > 0:
            for known_user in self.known_users:
                known_users_list.append(known_user.username)

            json_string = json.dumps(known_users_list)
            f = open("known_users_main_server.txt", "w")
            f.truncate(0)
            f.write(json_string)
            f.close()


    def stop_listening(self):
        self.store_conversations()
        self.store_known_users()
        b = bytes('1', 'utf-8')

        self.stop_all_threads = True

        self.stop_socket.connect((self.server_ip, self.server_port))
        self.stop_socket.send(b)
        self.stop_socket.close()

        for thread in self.current_threads:
            thread.join(2)

