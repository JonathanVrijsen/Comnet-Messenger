from user import User
import enum
#class message as saved in the server
class MessageType(enum.Enum):
    publickeyrequest = 1
    registerrequest = 2
    loginrequest = 3
    #add

class Message:
    sender = None
    content = None #in main server: encrypted by symmetric key related to conversation
    messageType = None
    def __init__(self, sender, messageType, content):
        self.sender=sender
        #self.content=content

        #enum switch-like attempt (Python lacks a proper enum switch
        if MessageType['messageType'] == 1:
            self.content = "publickeyrequest - " + content #content = "clientIP"
        elif MessageType['messageType'] == 2:
            self.content = "registerrequest - " + content #content = "clientIP - username - password"
            #todo encrypt
        elif MessageType['messageType'] == 3:
            self.content = "loginrequest - " + content #content = "clientIP - username - password"
            #todo encrypt
        #todo add if more cases
        #todo reject when else