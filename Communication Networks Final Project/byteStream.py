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
    elif re.search(r"^loginrequest - [\S]{5,20} - [\S]{8,20}$",out_string) is not None:
        message_type = byteStreamType.ByteStreamType.loginrequest
        content = re.search(r"[\S]{5,20} - [\S]{8,20}$").group()
    else:
        pass #todo error handling
    return content, message_type

class ByteStream:
#    sender = None
#    content = None  # in main server: encrypted by symmetric key related to conversation
#    messageType = None
#    outStream = None


    def __init__(self, sender_ip, message_type, content, public_key_sender):
        self.senderIP = sender_ip
        self.content = content
        self.messageType = message_type

        #enum switch-like attempt (Python lacks a proper enum switch
        if byteStreamType.ByteStreamType['messageType'] == 1:
            out_string = "publickeyrequest - " + content #content = "clientIP"
        elif byteStreamType.ByteStreamType['messageType'] == 2:
            out_string = "registerrequest - " + content #content = "clientIP - username - password"
        elif byteStreamType.ByteStreamType['messageType'] == 3:
            out_string = "loginrequest - " + content #content = "clientIP - username - password"
        else:
            pass#todo add if more cases
            #todo reject ERROR when else
        self.outStream = asymmetricKeying.encrypt(content.encode('ascii'), out_string)
        #todo ERROR HANDLING when failed?

    def __init__(self, out_stream, private_key_receiver):
        self.outStream = out_stream
        outstring = asymmetricKeying.decrypt(out_stream, private_key_receiver)
        if outstring:
            self.senderIP, self.content, self.messageType = extract_from_byte_string(outstring)
        else:
            pass #todo ERROR HANDLING
