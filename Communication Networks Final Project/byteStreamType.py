import enum
class ByteStreamType(enum.Enum):
    publickeyrequest = 1
    registerrequest = 2
    loginrequest = 3
    registeranswer = 4
    #TODO add