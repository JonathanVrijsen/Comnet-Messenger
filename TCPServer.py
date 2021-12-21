from socket import *

#from click._compat import raw_input


serverPort = 12000
serverSocket = socket(AF_INET,SOCK_STREAM)
serverSocket.bind(('',serverPort))
print(serverSocket.getsockname())
#print(server_socket.gethostbyname(server_socket.getsockname()))
serverSocket.listen(1)
print("The server is ready to receive")
connectionSocket, addr = serverSocket.accept()
print(addr)
while 1:
    sentence = connectionSocket.recv(1024)
    capitalizedSentence = sentence.upper()
    connectionSocket.send(capitalizedSentence)
    if capitalizedSentence== "b'END'":
        connectionSocket.close()