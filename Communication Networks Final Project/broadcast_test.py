import socket
import threading
from socket import *
from time import sleep

## SERVER

# serverport = 12002
# msg = b'hello world'
#
# def send(serverport, msg):
#     while True:
#         sock = socket(AF_INET, SOCK_DGRAM, IPPROTO_UDP)  # UDP
#         sock.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)
#         sock.bind(("127.0.0.1",serverport))
#         sock.sendto(msg, ("255.255.255.255", 5005))
#         print("send")
#         sock.close()
#
#         sleep(2)
#
# thread = threading.Thread(target = send, args= (serverport, msg,))
# thread.start()
#
#
# ## CLIENT
# client_port = 11999
# while True:
#     client_socket = socket(AF_INET, SOCK_DGRAM)
#     client_socket.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)
#     print("receiving")
#     data, addr = client_socket.recvfrom(1024)
#     print(data)

import json

from cryptography.fernet import Fernet

import message
import symmetric_keying
from message import Message

print(dir(json))

a = ["1","a","7","5","4"]
conversation_keys = dict()
for string in a:
    id = string
    print(id)
    key = Fernet.generate_key()
    conversation_keys[id] = key.decode("ascii")

string1 = json.dumps(conversation_keys)


a = ["1s","as","7s","54","44"]
conversation_keys = dict()
for string in a:
    id = string
    print(id)
    key = Fernet.generate_key()
    conversation_keys[id] = key.decode("ascii")

string2 = json.dumps(conversation_keys)

file = open("conversation_keys.txt", "w")
file.write(string1 + "\n" + string2)
file.close()

file = open("conversation_keys.txt", "r")
content = file.read().splitlines()
file.close

print(content)
