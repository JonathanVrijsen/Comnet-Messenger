import enum


class ByteStreamErrorType(enum.Enum):
    NoError = 1
    NoMessageTypeMatch = 2
    LoginOrPasswordWrong = 3
