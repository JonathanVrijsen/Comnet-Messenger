from user import User
from message import Message

class Conversation:
    def __init__(self, sender, receivers):
        self.messages = []
        self.members = sender + receivers

    def addMessage(self, content, sender):
        message = Message(sender, content)
        self.messages.append(message)
