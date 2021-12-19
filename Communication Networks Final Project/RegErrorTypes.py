import enum

class RegisterErrorType(enum.Enum):
    NoError = 1
    NoPasswordMatch = 2
    NoUsername = 3
    NoPassword = 4