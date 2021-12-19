import byteStreamErrorTypes

class CustomError(Exception):
    def __init__(self, error_type):
        self.error_type = error_type

    def __str__(self):
        if self.error_type == byteStreamErrorTypes.ByteStreamErrorType.NoError:
            error_string = "No Error"
        elif self.error_type == byteStreamErrorTypes.ByteStreamErrorType.NoMessageTypeMatch:
            error_string = "The request isn't recognised by this device"
        elif self.error_type == byteStreamErrorTypes.ByteStreamErrorType.LoginOrPasswordWrong:
            error_string = "Login/Password wrong. A login should be 5-20 characters long, a password 8-20"
        else:
            error_string = "regular error input"
        return "Error: " + error_string