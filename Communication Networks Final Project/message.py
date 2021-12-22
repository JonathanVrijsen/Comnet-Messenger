# class message as saved in the server and the local memory of the client

class Message:
    def __init__(self, sender, content):
        self.sender = sender
        self.content = content