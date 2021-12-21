from message import Message


class Conversation:
    def __init__(self, members, id):
        self.messages = []
        self.members = members
        self.id = id

    def add_message(self, message):
        self.messages.append(message)

    def print_messages(self):
        for message in self.messages:
            print(message.content)

    def encode_conversation(self):
        # convention: id -- member1;;;member2;;;...;;;memberi -- sender;,;message1;;;sender;,;message2;;;...;;;sender;,;messagei
        to_encode_string = ""
        to_encode_string = to_encode_string + self.id + " -- "
        member_string = ""
        for member in self.members:
            member_string = member_string + member + ";;;"
        member_string = member_string[0:len(member_string) - 3]  # cut off last ";;;"
        to_encode_string = to_encode_string + member_string + " -- "

        message_string = ""
        for message in self.messages:
            message_string = message_string + message.sender + ";,;" + message.content + ";;;"
        message_string = message_string[0:len(message_string) - 3]  # cut off last ";;;"
        if message_string != "":
            to_encode_string = to_encode_string + message_string

        return to_encode_string

    def decode_conversation(self, to_decode_string):

        # first create an empty conversation, use this function on the empty conversation
        conv_attr = to_decode_string.split(" -- ")
        self.id = conv_attr[0]
        self.members = conv_attr[1].split(";;;")
        messages = conv_attr[2].split(";;;")
        if messages != ['']:
            for message_str in messages:
                message = message_str.split(";,;")
                self.messages.append(Message(message[0], message[1]))
