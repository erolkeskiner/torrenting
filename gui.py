import sys
from PyQt5 import QtWidgets,QtGui,QtCore
import uuid
import os.path
import searchByFileName



listDosya = ['dosya1','dosya2','dosya3']

class Window(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()

        self.init_ui()

    def init_ui(self):


        self.fileNameLabel = QtWidgets.QLabel("File name :")
        self.fileNameLabel.setGeometry(QtCore.QRect(10, 20, 71, 16))
        self.fileNameLabel.setObjectName("fileNameLabel")
        self.fileNameTextEdit = QtWidgets.QTextEdit("Search for a file")
        self.fileNameTextEdit.setGeometry(QtCore.QRect(80, 10, 81, 31))
        self.fileNameTextEdit.setObjectName("fileNameTextEdit")
        self.searchButton = QtWidgets.QPushButton("Search")
        self.searchButton.setGeometry(QtCore.QRect(190, 10, 91, 32))
        self.searchButton.setObjectName("searchButton")

        self.searchButton.clicked.connect(self.search)

        self.resultOfSearch = QtWidgets.QListWidget()
        self.resultOfSearch.setGeometry(QtCore.QRect(10, 50, 271, 192))
        self.resultOfSearch.setObjectName("resultOfSearch")

        for dosya in listDosya:
            self.resultOfSearch.addItem(dosya)
        self.iconforprogress = QtWidgets.QLabel("Progress Icon")
        self.iconforprogress.setGeometry(QtCore.QRect(160, 10, 31, 16))
        self.iconforprogress.setObjectName("iconforprogress")
        self.downloadButton = QtWidgets.QPushButton("Download")
        self.downloadButton.setGeometry(QtCore.QRect(10, 290, 271, 32))
        self.downloadButton.setObjectName("downloadButton")
        self.downloadButton.clicked.connect(self.start_download)
        self.foundCheckBrowser = QtWidgets.QTextBrowser()
        self.foundCheckBrowser.setGeometry(QtCore.QRect(10, 250, 271, 31))
        self.foundCheckBrowser.setObjectName("foundCheckBrowser")

        self.userListWidget = QtWidgets.QListWidget()
        self.userListWidget.setGeometry(QtCore.QRect(290, 50, 91, 261))
        self.userListWidget.setObjectName("userListWidget")
        self.viewMessages = QtWidgets.QTextBrowser()
        self.viewMessages.setGeometry(QtCore.QRect(390, 10, 261, 201))
        self.viewMessages.setObjectName("viewMessages")
        self.messageToSend = QtWidgets.QTextEdit("Message to Send")
        self.messageToSend.setGeometry(QtCore.QRect(390, 220, 261, 61))
        self.messageToSend.setObjectName("messageToSend")
        self.sendButton = QtWidgets.QPushButton("Send")
        self.sendButton.setGeometry(QtCore.QRect(380, 290, 271, 32))
        self.sendButton.setObjectName("sendButton")
        self.sendButton.clicked.connect(self.sendMessage)
        self.userListLabel = QtWidgets.QLabel("User List")
        self.userListLabel.setGeometry(QtCore.QRect(10, 20, 71, 16))
        self.userListLabel.setObjectName("userListLabel")
        self.messagesLabel = QtWidgets.QLabel("Messages")
        self.messagesLabel.setGeometry(QtCore.QRect(10, 20, 71, 16))
        self.messagesLabel.setObjectName("messagesLabel")

        mainHBox = QtWidgets.QHBoxLayout()

        torrentVBox = QtWidgets.QVBoxLayout()
        messageVBox = QtWidgets.QHBoxLayout()

        hSearchBox = QtWidgets.QHBoxLayout()

        hSearchBox.addWidget(self.fileNameLabel)

        hSearchBox.addWidget(self.fileNameTextEdit)



        hSearchBox.addWidget(self.searchButton)


        torrentVBox.addLayout(hSearchBox)

        torrentVBox.addWidget(self.resultOfSearch)

        torrentVBox.addWidget(self.foundCheckBrowser)

        torrentVBox.addWidget(self.downloadButton)

        mainHBox.addLayout(torrentVBox)


        listVBox = QtWidgets.QVBoxLayout()

        listVBox.addWidget(self.userListLabel)

        listVBox.addWidget(self.userListWidget)


        messageVBox.addLayout(listVBox)


        mVBox = QtWidgets.QVBoxLayout()
        mVBox.addWidget(self.messagesLabel)
        mVBox.addWidget(self.viewMessages)

        mVBox.addWidget(self.messageToSend)

        mVBox.addWidget(self.sendButton)


        messageVBox.addLayout(mVBox)

        mainHBox.addLayout(messageVBox)
        # mainHBox.addStretch()

        self.setLayout(mainHBox)

        self.show()

    def search(self):
        filename = self.fileNameTextEdit.toPlainText()
        b , l = searchByFileName.search(filename)
        self.resultOfSearch.clear()
        if b is True:
            self.resultOfSearch.addItem(filename)
            self.foundCheckBrowser.setText('File Found!')
        else:
            self.foundCheckBrowser.setText('File Not Found! Similar results are in the list')
            for f in l:
                self.resultOfSearch.addItem(f)


    def start_download(self):
        fileChoise = self.resultOfSearch.selectedItems()
        print(fileChoise.text())
    def sendMessage(self):
        message = self.messageToSend.toPlainText()

        print(message)



app = QtWidgets.QApplication(sys.argv)
a_window = Window()
sys.exit(app.exec_())