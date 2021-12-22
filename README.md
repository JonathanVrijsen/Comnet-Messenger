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

<img alt="Keyserver overview" src="https://github.com/JonathanVrijsen/Comnet-Messenger/blob/main/src/Images/GUI_KeyServerOverView.png" title="Keyserver overview"/>


Clicking the button "Create new client" on the Main menu, generates a new client and displays a new client window.
From this window, one can register new users and log into their account.

<img alt="Login screen" src="https://github.com/JonathanVrijsen/Comnet-Messenger/blob/main/src/Images/GUI_LoginScreen.png" title="Login screen"/>

Once logged in using the correct username and password, the user's conversations are shown.
When a specific conversation is selected in the list on the left-hand side, 
all the messages are shown in the window.

<img alt="Message screen" src="https://github.com/JonathanVrijsen/Comnet-Messenger/blob/main/src/Images/GUI_MessageScreen.png" title="Message screen"/>

### Register and login

Registering a new user is done by filling out the fields underneath "Or make an account:".
A user can be logged in by filling out the Username and Password fields at the top half of the window and clicking
the login button.

<img alt="Register And Login" src="https://github.com/JonathanVrijsen/Comnet-Messenger/blob/main/src/Images/RegisterAndLogin.gif" title="Register And Login"/>

### Creating new conversation / Sending messages

Once logged in, the user can create a new conversation.
First, click "Create conversation". This will show all possible contacts in the list on the left-hand side.
Next, the desired conversation partner has to be selected and "Create conversation" clicked. The conversation is created.

After a conversation has been initialized, the user can send messages in the conversation.
First, select the conversation in which a message should be sent. Next, a message can be sent by inputting the
message in the text box and clicking the send button.
Receiving messages happens automatically and are shown once received.

<img alt="CreateNewConv" src="https://github.com/JonathanVrijsen/Comnet-Messenger/blob/main/src/Images/CreateNewConv.gif" title="CreateNewConv"/>


### Creating group conversation

It is also possible to create a group chat. This is done by selecting multiple conversation partners.

<img alt="CreateGroupConv" src="https://github.com/JonathanVrijsen/Comnet-Messenger/blob/main/src/Images/CreateGroupConv.gif" title="CreateGroupConv"/>


### Logout

In one client window, any user can be logged out and logged in again without losing any information.

<img alt="Logout" src="https://github.com/JonathanVrijsen/Comnet-Messenger/blob/main/src/Images/Logout.gif" title="Logout"/>

## Known issues

- Closing a client window can sometimes still throw some errors.
- It is possible that "Refresh conversation" needs to be clicked multiple times to actually refresh the conversations.
- Thread safety could be improved.
- fqsdfdsqf

## Contributors

| [Jonathan Vrijsen](https://github.com/JonathanVrijsen) | [Wannes Nevens](https://github.com/WannesN) | [Sam Van de Velde](https://github.com/SamVandeVelde) | [Louis Van Eeckhoudt](https://github.com/Louis-Van-Eeckhoudt) |
|--------------------------------------------------------|---------------------------------------------|------------------------------------------------------|---------------------------------------------------------------|



