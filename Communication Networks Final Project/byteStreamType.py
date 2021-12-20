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
    # TODO add
