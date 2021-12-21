import byte_stream_error_types
import server_error_types


class CustomError(Exception):
    def __init__(self, error_type):
        self.error_type = error_type

    def __str__(self):
        if self.error_type == byte_stream_error_types.ByteStreamErrorType.NoError or self.error_type == server_error_types.ServerErrorType.NoError:
            error_string = "No Error"
        elif self.error_type == byte_stream_error_types.ByteStreamErrorType.NoMessageTypeMatch:
            error_string = "The request isn't recognised by this device"
        elif self.error_type == byte_stream_error_types.ByteStreamErrorType.LoginOrPasswordWrong:
            error_string = "Login/Password wrong. A login should be 5-20 characters long, a password 8-20"
        elif self.error_type == server_error_types.ServerErrorType.IncorrectPassword:
            error_string = "Incorrect login/password combination; try again."
        elif self.error_type == server_error_types.ServerErrorType.AccountAlreadyExists:
            error_string = "This account already exists. Did you intend to log in?"
        elif self.error_type == server_error_types.ServerErrorType.AccountDoesntExist:
            error_string = "This account doesn't exist."
        else:
            error_string = "regular error"
        return "Error: " + error_string
