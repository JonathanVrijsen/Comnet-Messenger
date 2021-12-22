import sys
import threading

from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *


from main_window_ui import Ui_MainWindow
from client_window_ui import Ui_Form
from server_window_ui import Ui_ServerWind

from threading import *

from client import *
from reg_error_types import *
from server import *
from key_server import *

import time


class MainMenu(QMainWindow, Ui_MainWindow): #Set up of mainwi
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.setWindowTitle("Main menu")

        self.M_ClientCreateButton.clicked.connect(self.create_client_window)

        self.client_windows = []
        self.newClientWindow = None
        self.server_overview = None
        self.keyserver_overview = None

        self.server_overview = ServerOverview() #Create the Main and key server windows immediatly
        self.keyserver_overview = KeyServerOverview()

        self.sg = QDesktopWidget().screenGeometry() #code to place server windows on right hand side of screen
        server_g = self.server_overview.geometry()
        x = self.sg.width() - server_g.width()
        y = 0
        self.server_overview.move(x, y)
        y = self.sg.height() - server_g.height()
        self.keyserver_overview.move(x, y)

        self.keyserver_overview.show()
        self.server_overview.show()


    def create_client_window(self): #creates a clientwindow when button is clicked
        self.newClientWindow = ClientWindow()
        client_g = self.newClientWindow.geometry()
        x = 10
        y = int((self.sg.height() - client_g.height())/2)

        self.newClientWindow.move(x,y)
        self.newClientWindow.show()

        self.client_windows.append(self.newClientWindow)

    def closeEvent(self, event):
        app = QApplication.instance()
        app.closeAllWindows()
        event.accept()


class ClientWindow(QWidget, Ui_Form):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.setWindowTitle("NewClient")

        self.H_passwordBox.setEchoMode(QLineEdit.Password)
        self.H_RegpasswordBox1.setEchoMode(QLineEdit.Password)
        self.H_RegpasswordBox2.setEchoMode(QLineEdit.Password)
        self.H_RegpasswordBox3.setEchoMode(QLineEdit.Password)

        self.stackedWidget.setCurrentWidget(self.page)
        self.stackedWidget_2.setCurrentWidget(self.CC_standard)
        self.H_LoginButton.clicked.connect(self.login)
        self.H_LogoutButton.clicked.connect(self.logout)
        self.H_ContactList.clicked.connect(self.contact_clicked)
        self.H_sendButton.clicked.connect(self.send_msg)
        self.H_RegButton.clicked.connect(self.register)
        self.H_CreateNewConvButton.clicked.connect(self.create_conversation)
        self.H_CC_BackButton.clicked.connect(self.exit_CC)
        self.H_CC_AddConvButton.clicked.connect(self.finalise_conversations)
        self.H_RefreshConvsButton.clicked.connect(self.get_conversations)

        self.current_threads = []
        self.stop_all_threads = False

        self.username = None
        self.contactList = []
        self.client = Client() #Each window creates it's own client

    def login(self): #on login clicked, start login process:
        self.username = self.H_usernameBox.text()
        self.password = self.H_passwordBox.text()
        successful = self.client.login(self.username, self.password)

        if successful:
            self.H_LogErrorTextBox.clear()
            self.stackedWidget.setCurrentWidget(self.page_2)
            tile = "User: " + self.username
            self.setWindowTitle(tile)
            self.update_thread = Thread(target=self.check_for_message)
            self.update_thread.start()
            self.current_threads.append(self.update_thread)

        else:
            self.H_LogErrorTextBox.setText("Wrong username or password")

        self.H_passwordBox.clear()

    def check_for_message(self): #loop on thread to ask for new messages
        while True:
            if self.stop_all_threads:
                break
            time.sleep(2)
            self.check_for_message_once()

    def check_for_message_once(self):

        targets = self.H_ContactList.selectedItems()
        if len(targets)>0:
            target = targets[0]
            possible_senders = target.text().split(", ")

            messages = self.client.get_messages(possible_senders)
            self.H_ConvList.clear()
            for message in messages:
                self.H_ConvList.addItem(QListWidgetItem(message))

    def logout(self): #on logout all windows are cleared
        self.stackedWidget.setCurrentWidget(self.page)
        self.H_passwordBox.clear()
        self.setWindowTitle("NewClient")
        self.H_ContactList.clear()
        self.H_ConvList.clear()
        self.client.log_out()

    def register(self):
        self.username = self.H_RegUsernameBox.text()
        self.password1 = self.H_RegpasswordBox1.text()
        self.password2 = self.H_RegpasswordBox2.text()
        self.password3 = self.H_RegpasswordBox3.text()

        reg_error = self.client.register(self.username, self.password1, self.password2, self.password3)
        if reg_error == RegisterErrorType.NoUsername:
            self.H_RegErrorTextBox.setText("No username has been entered")
        elif reg_error == RegisterErrorType.NoPasswordMatch:
            self.H_RegErrorTextBox.setText("Passwords don't match")
        elif reg_error == RegisterErrorType.NoPassword:
            self.H_RegErrorTextBox.setText("No password has been entered")
        elif reg_error == RegisterErrorType.UsernameAlreadyInUse:
            self.H_RegErrorTextBox.setText("Username already in use")
        else:
            self.H_RegUsernameBox.clear()
            self.H_RegpasswordBox1.clear()
            self.H_RegpasswordBox2.clear()
            self.H_RegpasswordBox3.clear()
            self.H_RegErrorTextBox.setText("Succes!")

    def contact_clicked(self): #if a contact is clicked, immediately check for new messages
        self.check_for_message_once()

    def send_msg(self):
        msg = self.H_MessageBox.text()
        targets = self.H_ContactList.selectedItems()

        # targets is empty because self.H_ContactList.selectedItems() isn't on the GUI anymore

        if len(targets) > 0:
            target = targets[0]
            receivers = target.text()
            receivers = receivers.split(", ")
            self.H_MsgErrorLabel.clear()
            # TODO implement with client
            self.check_for_message_once()
            self.client.send_message(receivers, msg)
            self.H_MessageBox.clear()
        else:
            self.H_MsgErrorLabel.setText("No target was selected")


    def create_conversation(self): #switch to create conversationview
        self.stackedWidget_2.setCurrentWidget(self.CC_activated)
        self.H_CC_AllUserList.clear()
        self.client.request_contacts()
        time.sleep(0.5)
        all_users = self.client.get_contacts()
        for user in all_users:
            self.H_CC_AllUserList.addItem(QListWidgetItem(user))

    def finalise_conversations(self): #actually make the new conversation according to selected users
        targets = self.H_CC_AllUserList.selectedItems()
        if len(targets) != 0:
            targets_str = []
            for target in targets:
                targets_str.append(target.data(0))

            self.client.start_conversation(targets_str)
            self.H_CC_ErrorLabel.clear()
            self.stackedWidget_2.setCurrentWidget(self.CC_standard)

            self.get_conversations()

        else:
            self.H_CC_ErrorLabel.setText("No participants were selected")
        # TODO create new conv in client with this list

    def exit_CC(self): #leave create conv window without creating conv
        self.stackedWidget_2.setCurrentWidget(self.CC_standard)

    def get_conversations(self):
        refresh_conversations_thread = threading.Thread(target=self.refresh_conversations)
        refresh_conversations_thread.start()
        self.current_threads.append(refresh_conversations_thread)


    def refresh_conversations(self): #check for new conversations
        # self.H_ContactList.clear()

        conv_names = self.client.get_conversations()
        self.H_ContactList.clear()
        for name in conv_names:
            self.H_ContactList.addItem(QListWidgetItem(name))

    def closeEvent(self, event):
        self.stop_all_threads = True

        self.client.stop_client()

        for thread in self.current_threads:
            thread.join(1)
        del self.client
        event.accept()




class ServerOverview(QWidget, Ui_ServerWind):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.setWindowTitle("Server Overview")

        self.MainServer = Server() #create the Mainserver object

        self.S_PrvtKeyLabel.setText(str(self.MainServer.priv_key))
        self.S_PblcKeyLabel.setText(str(self.MainServer.pub_key))

        self.S_RegDataTable.setRowCount(10)
        self.S_RegDataTable.setColumnCount(3)
        self.S_RegDataTable.setHorizontalHeaderLabels("ID;members;last message".split(";"))
        self.S_LeftTableLabel.setText("All saved conversations:")

        self.S_ConnectDataTable.setRowCount(10)
        self.S_ConnectDataTable.setColumnCount(2)
        self.S_ConnectDataTable.setHorizontalHeaderLabels("Username;Symkey".split(";"))
        self.S_RightTableLabel.setText("Connected clients:")

        self.S_RefreshButton.clicked.connect(self.update_data)

        self.stop_thread = False
        self.listen_thread = Thread(target=self.server_listen)
        self.listen_thread.start()

    def server_listen(self): #loop on thread to listin to incoming messages
        i = 0
        while True:
            self.MainServer.listen()
            if self.stop_thread:
                break

    def update_data(self): #request data saved in server to display
        convs = self.MainServer.get_conv_data()
        self.S_RegDataTable.clearContents()
        i = 0
        for conv in convs:
            self.S_RegDataTable.setItem(i, 0, QTableWidgetItem(conv[0]))
            self.S_RegDataTable.setItem(i, 1, QTableWidgetItem(conv[1]))
            self.S_RegDataTable.setItem(i, 2, QTableWidgetItem(conv[2]))
            i = i+1

        con_clients = self.MainServer.get_connected_clients()

        self.S_ConnectDataTable.clearContents()
        i = 0
        for con_client in con_clients:
            if con_client.user is not None:
                self.S_ConnectDataTable.setItem(i, 0, QTableWidgetItem(con_client.user.username))
            else:
                self.S_ConnectDataTable.setItem(i, 0, QTableWidgetItem("Unknown"))
            self.S_ConnectDataTable.setItem(i, 1, QTableWidgetItem(str(con_client.symKey)))
            i = i + 1

    def closeEvent(self, event):

        self.stop_thread = True
        self.MainServer.stop_listening()
        self.listen_thread.join(1)
        event.accept()

class KeyServerOverview(QWidget, Ui_ServerWind):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.setWindowTitle("Keyserver Overview")

        self.KeyServer = KeyServer() #create keyserver object

        self.S_PrvtKeyLabel.setText(str(self.KeyServer.priv_key))
        self.S_PblcKeyLabel.setText(str(self.KeyServer.pub_key))

        self.S_RegDataTable.setRowCount(10)
        self.S_RegDataTable.setColumnCount(2)
        self.S_RegDataTable.setHorizontalHeaderLabels("Username;Password".split(";"))

        self.S_ConnectDataTable.setRowCount(10)
        self.S_ConnectDataTable.setColumnCount(2)
        self.S_ConnectDataTable.setHorizontalHeaderLabels("Username;Symkey".split(";"))

        self.S_LeftTableLabel.setText("Registered users:")
        self.S_RightTableLabel.setText("Connected users:")
        self.S_RefreshButton.clicked.connect(self.update_data)

        self.stop_thread = False
        self.listen_thread = Thread(target=self.server_listen)
        self.listen_thread.start()

    def server_listen(self): #loop on thread for listening
        while True:
            self.KeyServer.listen()
            if self.stop_thread:
                break

    def update_data(self):#request data to update display
        reg_users = self.KeyServer.get_users()

        self.S_RegDataTable.clearContents()
        i = 0
        for user in reg_users:
            self.S_RegDataTable.setItem(i, 0, QTableWidgetItem(user[0]))
            self.S_RegDataTable.setItem(i, 1, QTableWidgetItem(user[1]))
            i = i + 1

        con_clients = self.KeyServer.get_connected_clients()

        self.S_ConnectDataTable.clearContents()
        i = 0
        for con_client in con_clients:
            if con_client.user is not None:
                self.S_ConnectDataTable.setItem(i, 0, QTableWidgetItem(con_client.user.username))
            else:
                self.S_ConnectDataTable.setItem(i, 0, QTableWidgetItem("Unknown"))
            self.S_ConnectDataTable.setItem(i, 1, QTableWidgetItem(str(con_client.symKey)))
            i = i + 1

    def closeEvent(self, event):
        self.stop_thread = True
        self.KeyServer.stop_listening()
        self.listen_thread.join(1)
        event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = MainMenu()
    win.show()
    sys.exit(app.exec())