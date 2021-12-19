import byteStreamType
from byteStreamErrorTypes import *
from customError import *
import re


def constructor_info(message_type, content):
    # enum switch-like attempt (Python lacks a proper enum switch
    if message_type == byteStreamType.ByteStreamType.publickeyrequest:
        out_string = "publickeyrequest - " + content  # content = "clientIP"
    elif message_type == byteStreamType.ByteStreamType.registerrequest:
        out_string = "registerrequest - " + content  # content = "clientIP - username - password"
    elif message_type == byteStreamType.ByteStreamType.loginrequest:
        out_string = "loginrequest - " + content  # content = "clientIP - username - password"
    elif message_type == byteStreamType.ByteStreamType.registeranswer:
        out_string = "registeranswer - " + content # content = "succes/failed"
    else:
        raise CustomError(ByteStreamErrorType.NoMessageTypeMatch)  # todo add if more cases
    out_stream = bytes(out_string, 'utf-8')
    return message_type, content, out_stream


def constructor_bytestream(out_stream):
    out_string = out_stream.decode("utf-8")
    content, message_type = extract_from_byte_string(out_string)
    return message_type, content, out_stream


def extract_from_byte_string(out_string):
    if re.search(r"^publickeyrequest$", out_string) is not None:
        message_type = byteStreamType.ByteStreamType.publickeyrequest
        content = None
    elif re.search(r"^registerrequest - [\S]{1,20} - [\S]{1,20}$", out_string) is not None:
        message_type = byteStreamType.ByteStreamType.registerrequest
        content = re.search(r"[\S]{1,20} - [\S]{1,20}$", out_string).group()
    elif re.search(r"^loginrequest - [\S]{1,20} - [\S]{1,20}$", out_string) is not None:
        message_type = byteStreamType.ByteStreamType.loginrequest
        content = re.search(r"[\S]{1,20} - [\S]{1,20}$", out_string).group()
    elif re.search(r"^registeranswer - [\S]{1,20}$", out_string) is not None:
        message_type = byteStreamType.ByteStreamType.registeranswer
        content = re.search(r"[\S]{1,20}$", out_string).group()
    else:
        raise CustomError(byteStreamErrorTypes.ByteStreamErrorType.NoMessageTypeMatch)
    return content, message_type


class ByteStream:
    #    content = None  # in main server: encrypted by symmetric key related to conversation
    #    messageType = None
    #    outStream = None
    def __init__(self, *args):
        print(len(args))
        print("bloop")
        if len(args) >= 2:
            self.messageType, self.content, self.outStream = constructor_info(args[0], args[1])
        else:
            self.messageType, self.content, self.outStream = constructor_bytestream(args[0])
