from user import User
import enum
#class message as saved in the server
class MessageType(enum.Enum):
    publickeyrequest = 1
    registerrequest = 2
    loginrequest = 3
    #TODO add

class Message:
    sender = None
    content = None #in main server: encrypted by symmetric key related to conversation
    messageType = None
    outString = None
    def __init__(self, sender, messageType, content):
        self.sender=sender
        self.content=content
        self.messageType = messageType;

        #enum switch-like attempt (Python lacks a proper enum switch
        if MessageType['messageType'] == 1:
            self.outString = "publickeyrequest - " + content #content = "clientIP"
        elif MessageType['messageType'] == 2:
            self.outString = "registerrequest - " + content #content = "clientIP - username - password"
            #todo encrypt
        elif MessageType['messageType'] == 3:
            self.outString = "loginrequest - " + content #content = "clientIP - username - password"
            #todo encrypt
        #todo add if more cases
        #todo reject when else