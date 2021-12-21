import enum


class ByteStreamType(enum.Enum):
    publickeyrequest = 1
    registerrequest = 2
    loginrequest = 3
    registeranswer = 4
    loginanswer = 5
    passwordrequest = 6
    passwordanswer = 7
    contactrequest = 8
    contactanswer = 9
    keyrequest = 10
    pubkeyanswer = 11
    symkeyanswer = 12
    passwordwrong = 13
    passwordcorrect = 14
    registertomain = 15
    newconversation = 16
    message = 17
    requestconversationkey = 18
    requestmembers = 19
    answermembers = 20
    requestallids = 21
    answerallids = 22
    getconversation = 23
    conversation = 24
    logout = 25
    stoplistening = 26
    # TODO add (pls stop)
