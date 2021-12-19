import sys
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

from PyQt5.uic import loadUi

from main_window_ui import Ui_MainWindow
from client_window_ui import Ui_Form
from server_window_ui import Ui_ServerWind

from threading import *

from client import Client
from server import *
from keyServer import *


class MainMenu(QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.M_ClientCreateButton.clicked.connect(self.create_client_window)
        self.M_ServerOverviewButton.clicked.connect(self.create_server_overview)
        self.M_CreateKeyServerButton.clicked.connect(self.create_keyserver_overview)

        self.client_windows = []
        self.newClientWindow = None
        self.server_overview = None
        self.keyserver_overview =None

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
        self.H_LoginButton.clicked.connect(self.login)
        self.H_LogoutButton.clicked.connect(self.logout)
        self.H_ContactList.clicked.connect(self.contact_clicked)
        self.H_sendButton.clicked.connect(self.send_msg)

        self.username = None
        # self.password = None
        self.contactList = []
        self.client = Client()

    def login(self):
        self.stackedWidget.setCurrentWidget(self.page_2)

        self.username = self.H_usernameBox.toPlainText()
        self.password = self.H_passwordBox.text()
        print(self.password)
        self.client.login(self.username, self.password)
        tile = "User: " + self.username
        self.setWindowTitle(tile)

        self.contactList = ["Jonathan", "Louis", "Sam"]
        for i in self.contactList:
            contact = QListWidgetItem(i)
            self.H_ContactList.addItem(contact)

    def logout(self):
        self.stackedWidget.setCurrentWidget(self.page)
        self.H_passwordBox.clear()
        self.setWindowTitle("NewClient")
        self.H_ContactList.clear()

    def contact_clicked(self, contact):
        contact = contact.data()
        self.H_ConvList.clear()
        print(contact)

        if contact == "Louis": #voorbeeld hoe gesprek uit te beelden
            msg1 = "hey"
            msg = QListWidgetItem(msg1)
            msg.setTextAlignment(Qt.AlignLeft)
            self.H_ConvList.addItem(msg)

            msg2 = "yow"
            msg = QListWidgetItem(msg2)
            msg.setTextAlignment(Qt.AlignRight)
            self.H_ConvList.addItem(msg)

    def send_msg(self):
        msg = self.H_MessageBox.text()
        self.client.send_message(msg)


class ServerOverview(QWidget, Ui_ServerWind):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.setWindowTitle("Server Overview")

        self.MainServer = Server()

        self.S_DataTable.setRowCount(10)
        self.S_DataTable.setColumnCount(3)

        self.stop_thread = False
        self.listen_thread = Thread(target = self.server_listen)
        self.listen_thread.start()

    def server_listen(self):
        i = 0
        while True:
            print(i)
            message,addr = self.MainServer.listen_silently()
            if self.stop_thread:
                break
            Ip = addr[0]
            port = str(addr[1])
            print(port)
            self.S_DataTable.setItem(i, 0, QTableWidgetItem(message))
            self.S_DataTable.setItem(i, 1, QTableWidgetItem(Ip))
            self.S_DataTable.setItem(i, 2, QTableWidgetItem(port))
            i = i+1

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

        self.S_DataTable.setRowCount(10)
        self.S_DataTable.setColumnCount(3)

        self.stop_thread = False
        self.listen_thread = Thread(target=self.server_listen)
        self.listen_thread.start()

    def server_listen(self):
        i = 0
        while True:
            print(i)
            message,addr = self.KeyServer.listen_silently()
            if self.stop_thread:
                break
            Ip = addr[0]
            port = str(addr[1])
            print(port)
            self.S_DataTable.setItem(i, 0, QTableWidgetItem(message))
            self.S_DataTable.setItem(i, 1, QTableWidgetItem(Ip))
            self.S_DataTable.setItem(i, 2, QTableWidgetItem(port))
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