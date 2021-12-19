import enum
class ByteStreamType(enum.Enum):
    publickeyrequest = 1
    registerrequest = 2
    loginrequest = 3
    registeranswer = 4
    loginanswer = 5
    passwordrequest = 6
    passwordanswer = 7
    publickey = 8
    # TODO add
