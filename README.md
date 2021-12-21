# Welcome to Available chatapp

Available is a messaging application created in python.
This project was completed in order to pass the course ELEC-H417: "Communication Networks Protocols and Architectures"
taught at the ULB by professor Jean-Michel Dricot.

The goal of this project is to design and implement
a basic chat app enabling private communication.
The application relies on a centralized architecture, 
meaning a central server handles the communication between
clients. An extra server, called key server, was implemented
to ensure private communication. The complete architecture
is described in detail in the [report.](https://github.com/link_to_report)

## Prerequisites

In the source code a couple of external libraries were used.
In order to run the messaging application correctly the following
libraries are necessary.

- PyQt5 

```
pip install PyQt5
```
- rsa 

```
pip install rsa
```
- cryptography

```
pip3 install cryptography
```

## Running the code

To run the code and launch the application, the file main.py should be run.
The program has been tested and therefore is compatible 
for Windows and macOS. Other operating systems shouldn't be a problem
as long as python and the previously mentioned libraries are compatible for that operating system.

## Features

### General

Upon compilation, Main menu, Server Overview and Keyserver Overview are initialized and displayed.
From the main window it is possible to create new client windows.

<img alt="Main menu" src="https://github.com/JonathanVrijsen/Comnet-Messenger/blob/main/src/Images/GUI_MainMenu.png" title="Main menu"/>

The Server Overview and Keyserver Overview windows can be used to analyse the server's behaviour and information. To update the information the button "Refresh" should be clicked.

<img alt="Server overview" src="https://github.com/JonathanVrijsen/Comnet-Messenger/blob/main/src/Images/GUI_ServerOverView.png" title="Server overview"/>

Clicking on the button "Create new client" on the Main menu, generates a new client and displays a new client window.
From this window, one can register new users and log into their account.

<img alt="Login screen" src="https://github.com/JonathanVrijsen/Comnet-Messenger/blob/main/src/Images/GUI_LoginScreen.png" title="Login screen"/>

Once logged in using the correct username and password, the user's conversations are shown.
When a specific conversation is selected in the list on the left-hand side, 
all the messages are shown in the window.
<img alt="Message screen" src="https://github.com/JonathanVrijsen/Comnet-Messenger/blob/main/src/Images/GUI_MessageScreen.png" title="Message screen"/>

### Creating new conversation

### Sending messages

### Logout


## Contributors

| [Jonathan Vrijsen](https://github.com/JonathanVrijsen)   | [Wannes Nevens](https://github.com/WannesN) | [Sam Van de Velde](https://github.com/SamVandeVelde) | [Louis Van Eeckhoudt](https://github.com/Louis-Van-Eeckhoudt) |
|----------------------------------------------------------|---------------------------------------------|------------------------------------------------------|---------------------------------------------------------------|



