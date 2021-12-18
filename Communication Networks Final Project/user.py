class User:
    profilePicture = None

    def __init__(self, username, password= None):
        self.username = username
        self.password = password

    def changeUsername(self, newUsername):
        self.username = newUsername

    def showUsername(self):
        print(self.username)
