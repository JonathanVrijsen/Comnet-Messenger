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
            self.messageType, self.content, self.outStream = self.constructor_info(args[0], args[1])
        else:
            self.messageType, self.content, self.outStream = self.constructor_bytestream(args)

    def constructor_info(self, message_type, content):

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
        out_stream = bytes(out_string, 'utf-8')
        #todo ERROR HANDLING when failed?
        return message_type, content, out_stream

    def constructor_bytestream(out_stream):
        out_string = out_stream.decode("utf-8")
        content, message_type = extract_from_byte_string(out_string)
        return message_type, content, out_stream
