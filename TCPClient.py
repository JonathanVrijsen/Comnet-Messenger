from socket import *
from requests import get

from User import User


#from click._compat import raw_input

public_ip = get('https://api.ipify.org').text
print(public_ip)
serverName = public_ip
print("vlop")
serverPort = 12000
clientSocket = socket(AF_INET, SOCK_STREAM)
clientSocket.connect((serverName, serverPort))
while(1):
    sentence = input("Input lowercase sentence:")
    b = bytes(sentence, 'utf-8')
    clientSocket.send(b)
    modifiedSentence = clientSocket.recv(1024)
    print('From Server:', modifiedSentence)
    if(modifiedSentence=="b'END'"):
        clientSocket.close()