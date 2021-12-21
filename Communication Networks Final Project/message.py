import json

from user import User


# class message as saved in the server


class Message:
    def __init__(self, *args):
        if len(args) == 1:
            self.from_json(args[0])
        else:
            self.sender = args[0]
            self.content = args[1]

    def to_json(self):
        json_dict = dict()
        json_dict["sender"] = str(self.sender)
        json_dict["content"] = str(self.content)
        return json.dumps(json_dict)

    def from_json(self, json_string):
        json_dict = json.loads(json_string)
        self.sender = json_dict["sender"]
        self.content = json_dict["content"]
        pass


