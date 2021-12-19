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

    def __init__(self, *args):
        if len(args) > 1:
            self.constructor_info(self, args[2], args[3])
        else:
            self.constructor_bytestream(self, args)

    def constructor_info(self, message_type, content):
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
        self.outStream = bytes(out_string, 'utf-8')
        #todo ERROR HANDLING when failed?

    def constructor_bytestream(self, out_stream):
        self.outStream = out_stream
        out_string = out_stream.decode("utf-8")
        self.senderIP, self.content, self.messageType = extract_from_byte_string(out_string)