import byte_stream_type
from byte_stream_error_types import *
from custom_error import *
import re

#The class ByteStream is a protocol used to transmit data. It's type can be seen as a header of the data, specifying the goal of the data
#It is used to convert a certain content to an outstream, which is a string that can be sent, and vice versa

#It was created at the beginning of the project, before the developers had any experience with Python.
#Due to a lack of time, it has not been updated with a more efficient and elegant solution (for example: JSON) yet.

def constructor_info(message_type, content):
    #construct outstream (string) based on type and content of the ByteStream

    # enum switch-like attempt (Python lacks a proper enum switch
    if message_type == byte_stream_type.ByteStreamType.publickeyrequest:
        out_string = "publickeyrequest - " + content
    elif message_type == byte_stream_type.ByteStreamType.registerrequest:
        out_string = "registerrequest - " + content
    elif message_type == byte_stream_type.ByteStreamType.loginrequest:
        out_string = "loginrequest - " + content
    elif message_type == byte_stream_type.ByteStreamType.registeranswer:
        out_string = "registeranswer - " + content
    elif message_type == byte_stream_type.ByteStreamType.passwordrequest:
        out_string = "passwordrequest - " + content
    elif message_type == byte_stream_type.ByteStreamType.passwordanswer:
        out_string = "passwordanswer - " + content
    elif message_type == byte_stream_type.ByteStreamType.loginanswer:
        out_string = "loginanswer - " + content
    elif message_type == byte_stream_type.ByteStreamType.contactrequest:
        out_string = "contactrequest"
    elif message_type == byte_stream_type.ByteStreamType.contactanswer:
        out_string = "contactanswer - " + content
    elif message_type == byte_stream_type.ByteStreamType.keyrequest:
        out_string = "keyrequest - " + str(content)
    elif message_type == byte_stream_type.ByteStreamType.pubkeyanswer:
        out_string = "pubkeyanswer - " + str(content)
    elif message_type == byte_stream_type.ByteStreamType.symkeyanswer:
        out_string = "symkeyanswer - " + str(content)
    elif message_type == byte_stream_type.ByteStreamType.passwordcorrect:
        out_string = "passwordcorrect - " + str(content)
    elif message_type == byte_stream_type.ByteStreamType.passwordwrong:
        out_string = "passwordwrong"
    elif message_type == byte_stream_type.ByteStreamType.registertomain:
        out_string = "registertomain - " + content
    elif message_type == byte_stream_type.ByteStreamType.newconversation:
        out_string = "newconversation - " + content
    elif message_type == byte_stream_type.ByteStreamType.message:
        out_string = "message - " + content #content id (len(id) is 40) - message
    elif message_type == byte_stream_type.ByteStreamType.requestconversationkey:
        out_string = "requestconversationkey - " + content
    elif message_type == byte_stream_type.ByteStreamType.requestmembers:
        out_string = "requestmembers - " + content
    elif message_type == byte_stream_type.ByteStreamType.answermembers:
        out_string = "answermembers - " + content
    elif message_type == byte_stream_type.ByteStreamType.requestallids:
        out_string = "requestallids"
    elif message_type == byte_stream_type.ByteStreamType.answerallids:
        out_string = "answerallids - " + content
    elif message_type == byte_stream_type.ByteStreamType.getconversation:
        out_string = "getconversation - " + content
    elif message_type == byte_stream_type.ByteStreamType.conversation:
        out_string = "conversation - " + content
    elif message_type == byte_stream_type.ByteStreamType.logout:
        out_string = "logout"
    else:
        raise CustomError(ByteStreamErrorType.NoMessageTypeMatch)
    out_stream = out_string.encode("utf-8")
    return message_type, content, out_stream


def constructor_bytestream(out_stream):
    if not isinstance(out_stream, str): #if it is not a string
        out_string = out_stream.decode("utf-8")
    else:
        out_string = out_stream
    content, message_type = extract_from_byte_string(out_string)
    return message_type, content, out_stream


#Based on regex, commonly used in f.e. C++

def extract_from_byte_string(out_string):
    #extract type and content based on a string

    if re.search(r"^publickeyrequest$", out_string) is not None:
        message_type = byte_stream_type.ByteStreamType.publickeyrequest
        content = None
    elif re.search(r"^registerrequest - [\S]{1,99} - ", out_string) is not None:
        message_type = byte_stream_type.ByteStreamType.registerrequest
        (start, end) = re.search(r"registerrequest - ", out_string).span()
        content = out_string[end:]
    elif re.search(r"^loginrequest - ", out_string) is not None:
        message_type = byte_stream_type.ByteStreamType.loginrequest
        (start, end) = re.search(r"^loginrequest - ", out_string).span()
        content = out_string[end:]
    elif re.search(r"^registeranswer - ", out_string) is not None:
        (start, end) = re.search(r"^registeranswer - ", out_string).span()
        message_type = byte_stream_type.ByteStreamType.registeranswer
        content = out_string[end:]
    elif re.search(r"^loginanswer - ", out_string) is not None:
        (start, end) = re.search(r"^loginanswer - ", out_string).span()
        message_type = byte_stream_type.ByteStreamType.loginanswer
        content = out_string[end:]
    elif re.search(r"^passwordrequest - ", out_string) is not None:
        (start, end) = re.search(r"^passwordrequest - ", out_string).span()
        message_type = byte_stream_type.ByteStreamType.passwordrequest
        content = out_string[end:]
    elif re.search(r"^passwordanswer - ", out_string) is not None:
        (start, end) = re.search(r"^passwordanswer - ", out_string).span()
        message_type = byte_stream_type.ByteStreamType.passwordanswer
        content = out_string[end:]
    elif re.search(r"^contactrequest$", out_string) is not None:
        message_type = byte_stream_type.ByteStreamType.contactrequest
        content = ""
    elif re.search(r"^contactanswer - ", out_string) is not None:
        message_type = byte_stream_type.ByteStreamType.contactanswer
        (start, end) = re.search(r"^contactanswer - ", out_string).span()
        content = out_string[end:]
    elif re.search(r"^keyrequest - ", out_string) is not None:
        (start, end) = re.search(r"^keyrequest - ", out_string).span()
        message_type = byte_stream_type.ByteStreamType.keyrequest
        content = out_string[end:]
    elif re.search(r"^pubkeyanswer - ", out_string) is not None:
        (start, end) = re.search(r"^pubkeyanswer - ", out_string).span()
        message_type = byte_stream_type.ByteStreamType.pubkeyanswer
        content = out_string[end:]
    elif re.search(r"^symkeyanswer - ", out_string) is not None:
        (start, end) = re.search(r"^symkeyanswer - ", out_string).span()
        message_type = byte_stream_type.ByteStreamType.symkeyanswer
        content = out_string[end:]
    elif re.search(r"^passwordcorrect - ", out_string) is not None:
        (start, end) = re.search(r"^passwordcorrect - ", out_string).span()
        message_type = byte_stream_type.ByteStreamType.passwordcorrect
        content = out_string[end:]
    elif re.search(r"^passwordwrong$", out_string) is not None:
        message_type = byte_stream_type.ByteStreamType.passwordwrong
        content = ""
    elif re.search(r"^registertomain - ", out_string) is not None:
        (start, end) = re.search(r"^registertomain - ", out_string).span()
        message_type = byte_stream_type.ByteStreamType.registertomain
        content = out_string[end:]
    elif re.search(r"^newconversation - ", out_string) is not None:
        (start, end) = re.search(r"^newconversation - ", out_string).span()
        message_type = byte_stream_type.ByteStreamType.newconversation
        content = out_string[end:]
    elif re.search(r"^message - ", out_string) is not None:
        (start, end) = re.search(r"^message - ", out_string).span()
        message_type = byte_stream_type.ByteStreamType.message
        content = out_string[end:]
    elif re.search(r"^requestconversationkey - ", out_string) is not None:
        (start, end) = re.search(r"^requestconversationkey - ", out_string).span()
        message_type = byte_stream_type.ByteStreamType.requestconversationkey
        content = out_string[end:]
    elif re.search(r"^requestmembers - ", out_string) is not None:
        (start, end) = re.search(r"^requestmembers - ", out_string).span()
        message_type = byte_stream_type.ByteStreamType.requestmembers
        content = out_string[end:]
    elif re.search(r"^answermembers - ", out_string) is not None:
        (start, end) = re.search(r"^answermembers - ", out_string).span()
        message_type = byte_stream_type.ByteStreamType.answermembers
        content = out_string[end:]
    elif re.search(r"^requestallids$", out_string) is not None:
        (start, end) = re.search(r"^requestallids$", out_string).span()
        message_type = byte_stream_type.ByteStreamType.requestallids
        content = out_string[end:]
    elif re.search(r"^answerallids - ", out_string) is not None:
        (start, end) = re.search(r"^answerallids - ", out_string).span()
        message_type = byte_stream_type.ByteStreamType.answerallids
        content = out_string[end:]
    elif re.search(r"^getconversation - ", out_string) is not None:
        (start, end) = re.search(r"^getconversation - ", out_string).span()
        message_type = byte_stream_type.ByteStreamType.getconversation
        content = out_string[end:]
    elif re.search(r"^conversation - ", out_string) is not None:
        (start, end) = re.search(r"^conversation - ", out_string).span()
        message_type = byte_stream_type.ByteStreamType.conversation
        content = out_string[end:]
    elif re.search(r"^logout$", out_string) is not None:
        content = None
        message_type = byte_stream_type.ByteStreamType.logout

    elif out_string == '1': #exit signal
        message_type = byte_stream_type.ByteStreamType.stoplistening
        content = ""

    else:
        raise CustomError(byte_stream_error_types.ByteStreamErrorType.NoMessageTypeMatch)
    return content, message_type


class ByteStream:
    #Two constructors required: if string is given, find type and content. If content and type are given, construct string
    def __init__(self, *args):
        if len(args) >= 2:
            self.messageType, self.content, self.outStream = constructor_info(args[0], args[1])
        else:
            self.messageType, self.content, self.outStream = constructor_bytestream(args[0])
