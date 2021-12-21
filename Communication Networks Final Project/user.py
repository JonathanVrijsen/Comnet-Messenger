class User:

    def __init__(self, username, password= None):
        self.username = username
        self.password = password

    def change_username(self, new_user_name):
        self.username = new_user_name

    def show_user_name(self):
        print(self.username)
