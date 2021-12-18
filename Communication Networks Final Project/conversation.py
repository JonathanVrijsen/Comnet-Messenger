from user import User
from message import Message

class Conversation:
    def __init__(self, members, id):
        self.messages = []
        self.members = members
        self.id = id

    def add_message(self, content, sender):
        message = Message(sender, content)
        self.messages.append(message)
