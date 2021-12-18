from user import User

#class message as saved in the server


class Message:
    sender = None
    content = None #in main server: encrypted by symmetric key related to conversation
    def __init__(self, sender, content):
        self.sender=sender
        self.content=content