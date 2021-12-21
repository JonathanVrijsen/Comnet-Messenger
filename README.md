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

To run the code and launch the application, the file GuiTest.py should be run.
The program has been tested and therefore is compatible 
for Windows and macOS. Other operating systems shouldn't be a problem
as long as python and the used libraries are compatible for that operating system.

## Features

Upon compilation, three windows are opened. the window allowing you to create clients, 
the central messaging server and the key server are launched.


<img alt="Main Menu" src="/Users/louisvaneeckhoudt/Desktop/Available - MainMenu.png" title="Main Menu" width="500"/>

## Contributors

| [Jonathan Vrijsen](https://github.com/JonathanVrijsen) | [Wannes Nevens](https://github.com/WannesN) | [Sam Van de Velde](https://github.com/SamVandeVelde) | [Louis Van Eeckhoudt](https://github.com/Louis-Van-Eeckhoudt) |
|----------------------|-------------------|----------------------|-------------------------|



