import enum

class ServerErrorType(enum.Enum):
    NoError = 1
    IncorrectPassword = 2
    AccountAlreadyExists = 3
    AccountDoesntExist = 4

