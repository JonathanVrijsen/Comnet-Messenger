import byteStreamType
import asymmetricKeying
import re


def extract_from_byte_string(out_string):
    if re.search(r"^publickeyrequest$", out_string) is not None:
        message_type = byteStreamType.ByteStreamType.publickeyrequest
        content = None
    elif re.search(r"^registerrequest - [\S]{5,20} - [\S]{8,20}$", out_string) is not None:
        message_type = byteStreamType.ByteStreamType.registerrequest
        content = re.search(r"[\S]{5,20} - [\S]{8,20}$").group()
    elif re.search(r"^loginrequest - [\S]{5,20} - [\S]{8,20}$", out_string) is not None:
        message_type = byteStreamType.ByteStreamType.loginrequest
        content = re.search(r"[\S]{5,20} - [\S]{8,20}$").group()
    else:
        pass #todo error handling
    return content, message_type

class ByteStream:
#    content = None  # in main server: encrypted by symmetric key related to conversation
#    messageType = None
#    outStream = None


    def __init__(self, message_type, content):
        self.content = content
        self.messageType = message_type

        #enum switch-like attempt (Python lacks a proper enum switch
        if message_type == byteStreamType.ByteStreamType.publickeyrequest:
            out_string = "publickeyrequest - " + content #content = "clientIP"
        elif message_type == byteStreamType.ByteStreamType.registerrequest:
            out_string = "registerrequest - " + content #content = "clientIP - username - password"
        elif message_type == byteStreamType.ByteStreamType.loginrequest:
            out_string = "loginrequest - " + content #content = "clientIP - username - password"
        else:
            pass#todo add if more cases
            #todo reject ERROR when else
        self.outStream = bytes(out_string, 'utf-8')
        #todo ERROR HANDLING when failed?

    #def __init__(self, out_stream, private_key_receiver):
        #self.outStream = out_stream
        #out_string = out_stream.decode("utf-8")
        #self.senderIP, self.content, self.messageType = extract_from_byte_string(out_string)