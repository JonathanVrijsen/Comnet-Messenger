from user import User
from message import Message

class Conversation:
    def __init__(self, members):
        self.messages = []
        self.members = members

    def addMessage(self, content, sender):
        message = Message(sender, content)
        self.messages.append(message)
