import sys
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

from PyQt5.uic import loadUi

from main_window_ui import Ui_MainWindow
from host_window_ui import Ui_Form
from server_window_ui import Ui_ServerWind


class MainMenu(QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.M_HostCreateButton.clicked.connect(self.create_host)
        self.M_ServerOverviewButton.clicked.connect(self.create_server_overview)

        self.hosts = []
        self.NewHost = None
        self.server_overview = None

    def create_host(self):
        self.NewHost = HostWindow()
        self.NewHost.show()
        self.hosts.append(self.NewHost)

    def create_server_overview(self):
        self.server_overview = server_overview()
        self.server_overview.show()

    def closeEvent(self, event):
        app = QApplication.instance()
        app.closeAllWindows()


class HostWindow(QWidget, Ui_Form):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.setWindowTitle("NewHost")

        self.H_passwordBox.setEchoMode(QLineEdit.Password)

        self.stackedWidget.setCurrentWidget(self.page)
        self.H_LoginButton.clicked.connect(self.login)
        self.H_LogoutButton.clicked.connect(self.logout)
        self.H_ContactList.clicked.connect(self.contact_clicked)

        self.username = None
        self.contactList = []

    def login(self):
        self.stackedWidget.setCurrentWidget(self.page_2)

        self.username = self.H_usernameBox.toPlainText()
        tile = "User: " + self.username
        self.setWindowTitle(tile)

        self.contactList = ["Jonathan", "Louis", "Sam"]
        for i in self.contactList:
            contact = QListWidgetItem(i)
            self.H_ContactList.addItem(contact)

    def logout(self):
        self.stackedWidget.setCurrentWidget(self.page)
        self.H_passwordBox.clear()
        self.setWindowTitle("NewHost")
        self.H_ContactList.clear()

    def contact_clicked(self,contact):
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


class server_overview(QWidget, Ui_ServerWind):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.setWindowTitle("Server Overview")



if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = MainMenu()
    win.show()
    sys.exit(app.exec())