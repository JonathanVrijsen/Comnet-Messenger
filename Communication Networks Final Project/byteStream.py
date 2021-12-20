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
        out_string = "registeranswer - " + content  # content = "succes/failed"
    elif message_type == byteStreamType.ByteStreamType.passwordrequest:
        out_string = "passwordrequest - " + content  # content = "user exists"
    elif message_type == byteStreamType.ByteStreamType.passwordanswer:
        out_string = "passwordanswer - " + content  # content = "password"
    elif message_type == byteStreamType.ByteStreamType.loginanswer:
        out_string = "registeranswer - " + content # content = "succes/failed"
    elif message_type == byteStreamType.ByteStreamType.contactrequest:
        out_string = "contactrequest" # content = \
    elif message_type == byteStreamType.ByteStreamType.contactanswer:
        out_string = "contactanswer - " + content # content = list of usernames
    elif message_type == byteStreamType.ByteStreamType.keyrequest:
        out_string = "keyrequest - " + str(content)  # content = public key of sender
    elif message_type == byteStreamType.ByteStreamType.pubkeyanswer:
        out_string = "pubkeyanswer - " + str(content)  # content = public key of sender
    elif message_type == byteStreamType.ByteStreamType.symkeyanswer:
        out_string = "symkeyanswer - " + str(content)  # content = sym key of sender

    else:
        raise CustomError(ByteStreamErrorType.NoMessageTypeMatch)  # todo add if more cases
    out_stream = out_string.encode("utf-8")
    return message_type, content, out_stream


def constructor_bytestream(out_stream):
    if not isinstance(out_stream, str): #if it is not a string
        out_string = out_stream.decode("utf-8")
    else:
        out_string = out_stream
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
        (start, end) = re.search(r"^registeranswer - ", out_string).span()
        message_type = byteStreamType.ByteStreamType.registeranswer
        content = out_string[end:-1]
    elif re.search(r"^loginanswer - [\S]{1,20}$", out_string) is not None:
        (start, end) = re.search(r"^loginanswer - ", out_string).span()
        message_type = byteStreamType.ByteStreamType.loginanswer
        content = out_string[end:-1]
    elif re.search(r"^passwordrequest - [\S]{1,20}$", out_string) is not None:
        (start, end) = re.search(r"^passwordrequest - ", out_string).span()
        message_type = byteStreamType.ByteStreamType.passwordrequest
        content = out_string[end:-1]
    elif re.search(r"^passwordanswer - [\S]{1,20}$", out_string) is not None:
        (start, end) = re.search(r"^passwordanswer - ", out_string).span()
        message_type = byteStreamType.ByteStreamType.passwordanswer
        content = out_string[end:-1]
    elif re.search(r"^contactrequest$", out_string) is not None:
        message_type = byteStreamType.ByteStreamType.contactrequest
        content = ""
    elif re.search(r"^contactanswer - $", out_string) is not None:
        message_type = byteStreamType.ByteStreamType.contactanswer
        content = ""
    elif re.search(r"^keyrequest - ", out_string) is not None:
        (start, end) = re.search(r"^keyrequest - ", out_string).span()
        message_type = byteStreamType.ByteStreamType.keyrequest
        content = out_string[end:-1]
    elif re.search(r"^pubkeyanswer - ", out_string) is not None:
        (start, end) = re.search(r"^pubkeyanswer - ", out_string).span()
        message_type = byteStreamType.ByteStreamType.pubkeyanswer
        content = out_string[end:-1]
    elif re.search(r"^symkeyanswer - ", out_string) is not None:
        (start, end) = re.search(r"^symkeyanswer - ", out_string).span()
        message_type = byteStreamType.ByteStreamType.symkeyanswer
        content = out_string[end:]
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
