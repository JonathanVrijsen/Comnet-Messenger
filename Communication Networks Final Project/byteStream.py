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
        out_string = "loginanswer - " + content # content = "succes/failed"
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
    elif message_type == byteStreamType.ByteStreamType.passwordcorrect:
        out_string = "passwordcorrect - " + str(content)
    elif message_type == byteStreamType.ByteStreamType.passwordwrong:
        out_string = "passwordwrong" # content = \
    elif message_type == byteStreamType.ByteStreamType.registertomain:
        out_string = "registertomain - " + content # content = list of usernames
    elif message_type == byteStreamType.ByteStreamType.newconversation:
        out_string = "newconversation - " +content #content is list of members
    elif message_type == byteStreamType.ByteStreamType.message:
        out_string = "message - " + content #content id (len(id) is 40) - message
    elif message_type == byteStreamType.ByteStreamType.requestconversationkey:
        out_string = "requestconversationkey - " + content
    elif message_type == byteStreamType.ByteStreamType.requestmembers:
        out_string = "requestmembers - " + content
    elif message_type == byteStreamType.ByteStreamType.answermembers:
        out_string = "answermembers - " + content
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
    elif re.search(r"^registerrequest - [\S]{1,99} - ", out_string) is not None:
        message_type = byteStreamType.ByteStreamType.registerrequest
        (start, end) = re.search(r"registerrequest - ", out_string).span()
        content = out_string[end:]
    elif re.search(r"^loginrequest - ", out_string) is not None:
        message_type = byteStreamType.ByteStreamType.loginrequest
        (start, end) = re.search(r"^loginrequest - ", out_string).span()
        print(start, end)
        content = out_string[end:]
    elif re.search(r"^registeranswer - ", out_string) is not None:
        (start, end) = re.search(r"^registeranswer - ", out_string).span()
        message_type = byteStreamType.ByteStreamType.registeranswer
        content = out_string[end:]
    elif re.search(r"^loginanswer - ", out_string) is not None:
        (start, end) = re.search(r"^loginanswer - ", out_string).span()
        message_type = byteStreamType.ByteStreamType.loginanswer
        content = out_string[end:]
    elif re.search(r"^passwordrequest - ", out_string) is not None:
        (start, end) = re.search(r"^passwordrequest - ", out_string).span()
        message_type = byteStreamType.ByteStreamType.passwordrequest
        content = out_string[end:]
    elif re.search(r"^passwordanswer - ", out_string) is not None:
        (start, end) = re.search(r"^passwordanswer - ", out_string).span()
        message_type = byteStreamType.ByteStreamType.passwordanswer
        content = out_string[end:]
    elif re.search(r"^contactrequest$", out_string) is not None:
        message_type = byteStreamType.ByteStreamType.contactrequest
        content = ""
    elif re.search(r"^contactanswer - ", out_string) is not None:
        message_type = byteStreamType.ByteStreamType.contactanswer
        (start, end) = re.search(r"^contactanswer - ", out_string).span()
        content = out_string[end:]
    elif re.search(r"^keyrequest - ", out_string) is not None:
        (start, end) = re.search(r"^keyrequest - ", out_string).span()
        message_type = byteStreamType.ByteStreamType.keyrequest
        content = out_string[end:]
    elif re.search(r"^pubkeyanswer - ", out_string) is not None:
        (start, end) = re.search(r"^pubkeyanswer - ", out_string).span()
        message_type = byteStreamType.ByteStreamType.pubkeyanswer
        content = out_string[end:]
    elif re.search(r"^symkeyanswer - ", out_string) is not None:
        (start, end) = re.search(r"^symkeyanswer - ", out_string).span()
        message_type = byteStreamType.ByteStreamType.symkeyanswer
        content = out_string[end:]
    elif re.search(r"^passwordcorrect - ", out_string) is not None:
        (start, end) = re.search(r"^passwordcorrect - ", out_string).span()
        message_type = byteStreamType.ByteStreamType.passwordcorrect
        content = out_string[end:]
    elif re.search(r"^passwordwrong$", out_string) is not None:
        message_type = byteStreamType.ByteStreamType.passwordwrong
        content = ""
    elif re.search(r"^registertomain - ", out_string) is not None:
        (start, end) = re.search(r"^registertomain - ", out_string).span()
        message_type = byteStreamType.ByteStreamType.registertomain
        content = out_string[end:]
    elif re.search(r"^newconversation - ", out_string) is not None:
        (start, end) = re.search(r"^newconversation - ", out_string).span()
        message_type = byteStreamType.ByteStreamType.newconversation
        content = out_string[end:]
    elif re.search(r"^message - ", out_string) is not None:
        (start, end) = re.search(r"^message - ", out_string).span()
        message_type = byteStreamType.ByteStreamType.message
        content = out_string[end:]
    elif re.search(r"^requestconversationkey - ", out_string) is not None:
        (start, end) = re.search(r"^requestconversationkey - ", out_string).span()
        message_type = byteStreamType.ByteStreamType.requestconversationkey
        content = out_string[end:]
    elif re.search(r"^requestmembers - ", out_string) is not None:
        (start, end) = re.search(r"^requestmembers - ", out_string).span()
        message_type = byteStreamType.ByteStreamType.requestmembers
        content = out_string[end:]
    elif re.search(r"^answermembers - ", out_string) is not None:
        (start, end) = re.search(r"^answermembers - ", out_string).span()
        message_type = byteStreamType.ByteStreamType.answermembers
        content = out_string[end:]

    else:
        raise CustomError(byteStreamErrorTypes.ByteStreamErrorType.NoMessageTypeMatch)
    return content, message_type


class ByteStream:
    #    content = None  # in main server: encrypted by symmetric key related to conversation
    #    messageType = None
    #    outStream = None
    def __init__(self, *args):
        if len(args) >= 2:
            self.messageType, self.content, self.outStream = constructor_info(args[0], args[1])
        else:
            self.messageType, self.content, self.outStream = constructor_bytestream(args[0])
