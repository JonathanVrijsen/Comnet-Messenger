from message import Message

class Conversation:
    def __init__(self, members, id):
        self.messages = []
        self.members = members
        self.id = id

    def add_message(self, message):
        self.messages.append(message)

    def printmessages(self):
        for message in self.messages:
            print(message.content)
