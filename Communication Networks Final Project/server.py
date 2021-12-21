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

        self.server_port = 12100
        self.stop_port = 12110
        self.server_ip = '127.0.0.1'
        self.server_socket = socket(AF_INET, SOCK_STREAM)
        self.stop_socket = socket(AF_INET, SOCK_STREAM)
        self.server_socket.bind(('127.0.0.1', self.server_port))
        #self.stop_socket.bind(('127.0.0.1', self.stop_port))

        (self.pub_key, self.priv_key) = generate_keys()
        f_key = open("serverCommonKey.txt", 'rb')
        self.serverCommonKey = f_key.read()

        self.i = 0

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

            # create new connected client
            new_connected_client = ConnectedClient(connection_socket, new_sym_key, client_pub_key)
            self.connected_clients.append(new_connected_client)

            # launch new thread dedicated to connected_client
            new_thread = threading.Thread(target=self.connected_client_listen, args=(new_connected_client,))
            self.current_threads.append(new_thread)
            new_thread.start()

        # note that it's possible that multiple clients are logged in to the same user

    def connected_client_listen(self, connected_client):
        while connected_client.active:

            if self.stop_all_threads:
                break

            connection_socket = connected_client.connection_socket

            rcvd = connection_socket.recv(1024)
            rcvd = symm_decrypt(rcvd, connected_client.symKey)
            byte_stream_in = ByteStream(rcvd)
            rcvd_content = byte_stream_in.content

            if byte_stream_in.messageType == ByteStreamType.registertomain:
                (username, sign) = rcvd_content.split(" - ", 1)
                print("MAIN SERVER: REGISTER TO MAIN")
                print(username)
                print(sign)
                sign = sign[2:len(sign) - 1]
                print(sign)

                decrypted_username = symm_decrypt(sign.encode('ascii'), self.serverCommonKey)

                if username.encode('ascii') == decrypted_username:
                    print("USER RGISTERED AT MAIN SERVER:", username)
                    new_user = User(username)
                    self.known_users.add(new_user)  # doesn't add if already in set

            elif byte_stream_in.messageType == ByteStreamType.requestallids:
                username = connected_client.user.username
                first = True
                print(len(self.conversations))
                for conv in self.conversations:
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

            elif byte_stream_in.messageType == ByteStreamType.loginrequest:
                (username, sign) = rcvd_content.split(" - ", 1)
                print("MAIN SERVER: LOGIN OF:", username)
                sign = sign[2:len(sign) - 1]
                decrypted_username = symm_decrypt(sign.encode('ascii'), self.serverCommonKey)
                if username.encode('ascii') == decrypted_username:
                    print("NOUS SOMMES ENTRES")
                    new_user = User(username)
                    connected_client.set_user(new_user)

            elif byte_stream_in.messageType == ByteStreamType.contactrequest:
                print("CONTACT REQUEST AT MAIN SERVER")
                contacts = ""
                first = True
                for user in self.known_users:
                    username = user.username
                    print(connected_client.user.username)
                    # if username != connected_client.user.username:
                    # TODO filter in different way
                    if first:
                        contacts = contacts + username
                        first = not first
                    else:
                        contacts = contacts + " - " + username
                print("send: ", contacts)
                byte_stream_out = ByteStream(ByteStreamType.contactanswer, contacts)
                out = symm_encrypt(byte_stream_out.outStream, connected_client.symKey)
                connection_socket.send(out)

            elif byte_stream_in.messageType == ByteStreamType.newconversation:
                members = rcvd_content.split(" - ")
                print("MS receives members: ", members)
                id = hash_string(rcvd_content)
                conversation = Conversation(members, id)
                self.conversations.append(conversation)

            elif byte_stream_in.messageType == ByteStreamType.message:
                # extract conversation id and content from rcvd_content
                # string has the following form: id-content, so split at first occurence of "-"
                id = rcvd_content[:40]
                msg = rcvd_content[43:]

                print("MS receives msg: ", msg)

                sender = connected_client.user
                # TODO user is last registered, not last logged in
                message = Message(sender.username, msg)

                # check if message id is in existing conversations
                for conversation in self.conversations:
                    if id == conversation.id:
                        # save message in conversation
                        conversation.add_message(message)
                        print("conversation changed: ")
                        conversation.print_messages()
                        # find all the receivers
                        members = conversation.members
                        print("conversation members: ", members)
                        break

                byte_stream_out = ByteStream(ByteStreamType.message, str(id) + " - " + sender.username + " - " + msg)
                for receiver in members:
                    # note that the sender is also a receiver, since it's possible that the sender is logged in at multiple clients
                    for tempConnectedClient in self.connected_clients:
                        print(tempConnectedClient.user.username)

                        if tempConnectedClient.user.username is not None and receiver == tempConnectedClient.user.username and tempConnectedClient != connected_client:
                            out = symm_encrypt(byte_stream_out.outStream, tempConnectedClient.symKey)
                            print('MS sends message')
                            tempConnectedClient.connection_socket.send(out)

            elif byte_stream_in.messageType == ByteStreamType.requestmembers:
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

            elif byte_stream_in.messageType == ByteStreamType.getconversation:
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

    def listen_silently(self):

        if self.i == 0:
            print("listening...")
            self.server_socket.listen(64)
            self.connection_socket, addr = self.server_socket.accept()
            rcvd_content = self.connection_socket.recv(1024)
            print("recieved!")
            print(rcvd_content.decode("utf-8"))
            self.i = self.i + 1
            return rcvd_content.decode("utf-8"), addr

        else:
            print("waf")
            self.server_socket.listen(64)
            rcvd_content = self.connection_socket.recv(1024)
            print(rcvd_content.decode("utf-8"))
            return rcvd_content.decode("utf-8"), (0, 0)

    def close(self):
        # perhaps send close message to all connected_clients

        for thread in self.current_threads:
            thread.join()

    def stop_listening(self):
        b = bytes('1', 'utf-8')

        self.stop_all_threads = True

        self.stop_socket.connect((self.server_ip, self.server_port))
        self.stop_socket.send(b)
        self.stop_socket.close()

        print("MS needs to close ", len(self.current_threads), "threads")
        for thread in self.current_threads:
            thread.join(2)
        print("MS threads closed")
