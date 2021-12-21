import sys
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

from PyQt5.uic import loadUi

from main_window_ui import Ui_MainWindow
from client_window_ui import UiForm
from server_window_ui import Ui_ServerWind

from threading import *

from client import *
from reg_error_types import *
from server import *
from key_server import *

import time


class MainMenu(QMainWindow, Ui_MainWindow):
    def __init__(self, parent = None):
        super().__init__(parent)
        self.setupUi(self)
        self.M_ClientCreateButton.clicked.connect(self.create_client_window)
        self.M_ServerOverviewButton.clicked.connect(self.create_server_overview)
        self.M_CreateKeyServerButton.clicked.connect(self.create_keyserver_overview)

        self.client_windows = []
        self.newClientWindow = None
        self.server_overview = None
        self.keyserver_overview = None

    def create_client_window(self):
        self.newClientWindow = ClientWindow()
        self.newClientWindow.show()
        self.client_windows.append(self.newClientWindow)

    def create_server_overview(self):
        self.server_overview = ServerOverview()
        self.server_overview.show()

    def create_keyserver_overview(self):
        self.keyserver_overview = KeyServerOverview()
        self.keyserver_overview.show()

    def closeEvent(self, event):
        app = QApplication.instance()
        app.closeAllWindows()


class ClientWindow(QWidget, UiForm):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui(self)
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
        #self.H_Refresh_Contacts.clicked.connect(self.refresh_contacts)
        self.H_CreateNewConvButton.clicked.connect(self.create_conversation)
        self.H_CC_BackButton.clicked.connect(self.exit_CC)
        self.H_CC_AddConvButton.clicked.connect(self.finalise_conversations)
        self.H_RefreshConvsButton.clicked.connect(self.get_conversations)

        self.username = None
        # self.password = None
        self.contactList = []
        self.client = Client()

    def login(self):
        self.username = self.H_usernameBox.toPlainText()
        self.password = self.H_passwordBox.text()
        successful = self.client.login(self.username, self.password)
        print(successful)

        if successful:
            self.H_LogErrorTextBox.clear()
            self.stackedWidget.setCurrentWidget(self.page_2)
            tile = "User: " + self.username
            self.setWindowTitle(tile)
            self.update_thread = Thread(target=self.check_for_message)
            self.update_thread.start()

        else:
            self.H_LogErrorTextBox.setText("Wrong username or password")

    def check_for_message(self):
        while True:

            self.check_for_message_once()

    def check_for_message_once(self):
        time.sleep(2)
        targets = self.H_ContactList.selectedItems()
        possible_senders = []
        for target in targets:
            possible_senders.append(target.text())

        if len(possible_senders) > 0:
            messages = self.client.get_messages(possible_senders)
            print("messages received at gui")
            self.H_ConvList.clear()
            for message in messages:
                self.H_ConvList.addItem(QListWidgetItem(message))

    def logout(self):
        self.stackedWidget.setCurrentWidget(self.page)
        self.H_passwordBox.clear()
        self.setWindowTitle("NewClient")
        self.H_ContactList.clear()

    def register(self):
        self.username = self.H_RegUsernameBox.text()
        self.password1 = self.H_RegpasswordBox1.text()
        self.password2 = self.H_RegpasswordBox2.text()
        self.password3 = self.H_RegpasswordBox3.text()

        regerror = self.client.register(self.username,self.password1,self.password2,self.password3)
        if regerror == RegisterErrorType.NoUsername:
            self.H_RegErrorTextBox.setText("No username has been entered")
        elif regerror == RegisterErrorType.NoPasswordMatch:
            self.H_RegErrorTextBox.setText("Passwords don't match")
        elif regerror == RegisterErrorType.NoPassword:
            self.H_RegErrorTextBox.setText("No password has been entered")
        elif regerror == RegisterErrorType.UsernameAlreadyInUse:
            self.H_RegErrorTextBox.setText("Username already in use")
        else:
            self.H_RegErrorTextBox.setText("Succes!")

    def contact_clicked(self):
        pass
        #TODO import conv and display on right side

    def send_msg(self):
        msg = self.H_MessageBox.text()
        receivers = []
        targets = self.H_ContactList.selectedItems()
        # targets is leeg omdat self.H_ContactList.selectedItems() niet meer op de GUI is
        for target in targets:
            receivers.append(target.text())

        if len(receivers) > 0:
            print(receivers)
            self.H_MsgErrorLabel.clear()
            #TODO implement with client
            self.check_for_message_once()

        else:
            self.H_MsgErrorLabel.setText("No target was selected")
        self.client.send_message(receivers, msg)

    def create_conversation(self):
        self.stackedWidget_2.setCurrentWidget((self.CC_activated))
        self.H_CC_AllUserList.clear()
        self.client.request_contacts()
        time.sleep(0.5)
        allusers = self.client.get_contacts()
        for user in allusers:
            self.H_CC_AllUserList.addItem(QListWidgetItem(user))

    def finalise_conversations(self):
        targets = self.H_CC_AllUserList.selectedItems()
        if len(targets) != 0:
            targets_str = []
            for target in targets:
                targets_str.append(target.data(0))

            print(targets_str)
            self.client.start_conversation(targets_str)
            self.H_CC_ErrorLabel.clear()
            self.stackedWidget_2.setCurrentWidget((self.CC_standard))

        else:
            self.H_CC_ErrorLabel.setText("No partisipants were selected")
        #TODO create new conv in client with this list

    def exit_CC(self):
        self.stackedWidget_2.setCurrentWidget((self.CC_standard))

    def get_conversations(self):
        self.H_ContactList.clear()
        convnames = self.client.get_conversations()
        print(convnames)

        for name in convnames:
            self.H_ContactList.addItem(QListWidgetItem(name))

    #def refresh_contacts(self):
        #self.contactList = self.client.request_contacts()

        #for contact in self.contactList:
            #self.H_ContactList.addItem(QListWidgetItem(contact))




class ServerOverview(QWidget, Ui_ServerWind):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.setWindowTitle("Server Overview")

        self.MainServer = Server()

        self.S_PrvtKeyLabel.setText(str(self.MainServer.privKey))
        self.S_PblcKeyLabel.setText(str(self.MainServer.pubKey))

        self.S_RegDataTable.setRowCount(10)
        self.S_RegDataTable.setColumnCount(3)
        self.S_RegDataTable.setHorizontalHeaderLabels(("Username;Pasword;Symkey").split(";"))

        self.stop_thread = False
        self.listen_thread = Thread(target = self.server_listen)
        self.listen_thread.start()

    def server_listen(self):
        i = 0
        while True:
            self.MainServer.listen()
            if self.stop_thread:
                break

    def closeEvent(self, event):
        self.stop_thread = True
        self.MainServer.stop_listening()
        self.listen_thread.join()


class KeyServerOverview(QWidget, Ui_ServerWind):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.setWindowTitle("Keyserver Overview")

        self.KeyServer = keyServer()

        self.S_PrvtKeyLabel.setText(str(self.KeyServer.privKey))
        self.S_PblcKeyLabel.setText(str(self.KeyServer.pubKey))

        self.S_RegDataTable.setRowCount(10)
        self.S_RegDataTable.setColumnCount(2)
        self.S_RegDataTable.setHorizontalHeaderLabels(("Username;Pasword").split(";"))

        self.S_ConnectDataTable.setRowCount(10)
        self.S_ConnectDataTable.setColumnCount(2)
        self.S_ConnectDataTable.setHorizontalHeaderLabels(("Username;Symkey").split(";"))

        self.S_RefreshButton.clicked.connect(self.update_data)

        self.stop_thread = False
        self.listen_thread = Thread(target=self.server_listen)
        self.listen_thread.start()

    def server_listen(self):
        while True:
            self.KeyServer.listen()
            if self.stop_thread:
                break
             #users = self.KeyServer.getUsers()
            #self.S_RegDataTable.clear()
            #i=0
            #for j in users:
             #   self.S_RegDataTable.setItem(i, 0, QTableWidgetItem(j))
              #  self.S_RegDataTable.setItem(i, 1, QTableWidgetItem(users[j][0]))
               # i=i+1

    def update_data(self):
        regusers = self.KeyServer.getUsers()
        print(regusers)

        self.S_RegDataTable.clearContents()
        i = 0
        for user in regusers:
            self.S_RegDataTable.setItem(i,0,QTableWidgetItem(user[0]))
            self.S_RegDataTable.setItem(i, 1, QTableWidgetItem(user[1]))
            i =i+1

        conclients = self.KeyServer.getConnectedClients()

        self.S_ConnectDataTable.clearContents()
        i = 0
        for conclient in conclients:
            if conclient.user != None:
                self.S_ConnectDataTable.setItem(i, 0, QTableWidgetItem(conclient.user.username))
            else:
                self.S_ConnectDataTable.setItem(i, 0, QTableWidgetItem("Unknown"))
            self.S_ConnectDataTable.setItem(i, 1, QTableWidgetItem(str(conclient.symKey)))
            i = i+1

    def closeEvent(self, event):
        self.stop_thread = True
        self.KeyServer.stop_listening()
        self.listen_thread.join()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = MainMenu()
    win.show()
    sys.exit(app.exec())