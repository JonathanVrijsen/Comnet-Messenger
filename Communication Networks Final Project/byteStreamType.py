import enum
class ByteStreamType(enum.Enum):
    publickeyrequest = 1
    registerrequest = 2
    loginrequest = 3
    publickey = 4
    #TODO add