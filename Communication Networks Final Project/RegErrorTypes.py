import enum

class RegisterErrorType(enum.Enum):
    NoError = 1
    NoStreamMatch = 2
    WrongInputLength = 3
    NoUsername = 4
    NoPassword = 5
    NoPasswordMatch = 6