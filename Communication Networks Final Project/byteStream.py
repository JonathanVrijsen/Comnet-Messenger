import byteStreamType

class ByteStream:
    sender = None
    content = None  # in main server: encrypted by symmetric key related to conversation
    messageType = None
    outString = None

    def __init__(self, sender, messageType, content):
        self.sender=sender
        self.content=content
        self.messageType = messageType

        #enum switch-like attempt (Python lacks a proper enum switch
        if byteStreamType.ByteStreamType['messageType'] == 1:
            self.outString = "publickeyrequest - " + content #content = "clientIP"
        elif byteStreamType.ByteStreamType['messageType'] == 2:
            self.outString = "registerrequest - " + content #content = "clientIP - username - password"
            #todo encrypt
        elif byteStreamType.ByteStreamType['messageType'] == 3:
            self.outString = "loginrequest - " + content #content = "clientIP - username - password"
            #todo encrypt
        #todo add if more cases
        #todo reject when else

    def __init__(self, outString):
        self.outString = outString
