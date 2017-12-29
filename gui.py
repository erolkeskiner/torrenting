import sys
from PyQt5 import QtWidgets,QtGui,QtCore
import uuid
import os.path
import search
import queue
import time
import glob
from peer import ClientStarter, ServerStarterThread, ListUpdaterThread, LoggerThread, MB1


inDict = {'msg': queue.Queue(),'listF':[],'res':queue.Queue(),'fUsers':{}}
logQueue = queue.Queue()

userList={}
clientDict = {}

if os.path.exists('peeruuid.txt'):
    with open('peeruuid.txt','r') as f:
        uid= f.read()
else:
    uid = uuid.uuid4()

    with open('peeruuid.txt','w') as f:
        f.write(str(uid))




class Window(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()

        self.init_ui()

    def init_ui(self):


        self.fileNameLabel = QtWidgets.QLabel("File name :")
        self.fileNameLabel.setGeometry(QtCore.QRect(10, 20, 71, 16))
        self.fileNameLabel.setObjectName("fileNameLabel")
        self.fileNameTextEdit = QtWidgets.QLineEdit()
        self.fileNameTextEdit.setGeometry(QtCore.QRect(80, 10, 81, 31))
        self.fileNameTextEdit.setObjectName("fileNameTextEdit")

        self.searchButton = QtWidgets.QPushButton("Search")
        self.searchButton.setGeometry(QtCore.QRect(190, 10, 91, 32))
        self.searchButton.setObjectName("searchButton")

        self.searchButton.clicked.connect(self.search)

        self.resultOfSearch = QtWidgets.QListWidget()
        self.resultOfSearch.setGeometry(QtCore.QRect(10, 50, 271, 192))
        self.resultOfSearch.setObjectName("resultOfSearch")


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
        for u in userList:
            self.userListWidget.addItem(u)


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

        self.connectLabel = QtWidgets.QLabel("Connect to network with IP")
        self.connectLabel.setObjectName("connectLabel")

        self.connectIp = QtWidgets.QLineEdit()
        self.connectIp.setObjectName('connectIp')

        self.connectButton = QtWidgets.QPushButton("Connect")
        self.connectButton.setObjectName("connectButton")

        self.connectButton.clicked.connect(self.connectToNetwork)

        self.progress = QtWidgets.QProgressBar(self)
        self.progress.setGeometry(200, 80, 250, 20)



        mainHBox = QtWidgets.QHBoxLayout()

        torrentVBox = QtWidgets.QVBoxLayout()
        messageVBox = QtWidgets.QHBoxLayout()

        hSearchBox = QtWidgets.QHBoxLayout()

        hSearchBox.addWidget(self.fileNameLabel)
        hSearchBox.addStretch()

        hSearchBox.addWidget(self.fileNameTextEdit)
        hSearchBox.addStretch()


        hSearchBox.addWidget(self.searchButton)
        hSearchBox.addStretch()


        torrentVBox.addLayout(hSearchBox)
        torrentVBox.addStretch()
        torrentVBox.addWidget(self.resultOfSearch)
        torrentVBox.addStretch()
        torrentVBox.addWidget(self.foundCheckBrowser)
        torrentVBox.addStretch()
        torrentVBox.addWidget(self.downloadButton)
        torrentVBox.addStretch()
        torrentVBox.addWidget(self.progress)
        torrentVBox.addStretch()


        lmHBox = QtWidgets.QHBoxLayout()

        listVBox = QtWidgets.QVBoxLayout()
        connectHBox = QtWidgets.QHBoxLayout()
        connectHBox.addWidget(self.connectLabel)
        connectHBox.addWidget(self.connectIp)
        connectHBox.addWidget(self.connectButton)

        listVBox.addLayout(connectHBox)

        listVBox.addWidget(self.userListLabel)

        listVBox.addWidget(self.userListWidget)

        lmHBox.addLayout(listVBox)




        mVBox = QtWidgets.QVBoxLayout()
        mVBox.addWidget(self.messagesLabel)
        mVBox.addStretch()
        mVBox.addWidget(self.viewMessages)
        mVBox.addStretch()
        mVBox.addWidget(self.messageToSend)
        mVBox.addStretch()
        mVBox.addWidget(self.sendButton)
        mVBox.addStretch()

        lmHBox.addLayout(mVBox)

        messageVBox.addLayout(lmHBox)
        messageVBox.addStretch()

        mainHBox.addLayout(messageVBox)
        mainHBox.addStretch()
        mainHBox.addLayout(torrentVBox)
        mainHBox.addStretch()


        self.setLayout(mainHBox)

        self.show()



    def search(self):
         self.resultOfSearch.clear()
         print(inDict)
         inDict['listF'] = []
         inDict['fUsers'] = {}


         fileName = self.fileNameTextEdit.text()

         proMessage = ('SHN '+fileName).encode()
         for user , q in userList.items():
             if (user == uid):
                 continue
             ClientStarter(userList[user][0],logQueue,clientDict,userList,user,uid,inDict)
             print(userList[user])
             clientDict[user].put(proMessage)




         time.sleep(3)
         print(inDict)
         for l in inDict['listF']:
             self.resultOfSearch.addItem(l)

         self.resultOfSearch.repaint()
         for user, q in userList.items():
             clientDict[user].put("QUI")


    def connectToNetwork(self):

        ip = self.connectIp.text()
        print(ip)
        clientDict['n_server'] = queue.Queue()
        ClientStarter(ip,logQueue,clientDict,userList,'n_server',str(uid),inDict)


        protocolMessage = 'USR'
        clientDict['n_server'].put(protocolMessage)
        time.sleep(5)
        print('USR gönderildi')
        protocolMessage = 'LSQ'
        clientDict['n_server'].put(protocolMessage)
        print('LSQ gönderildi')

        protocolMessage = 'QUI'
        clientDict['n_server'].put(protocolMessage)
        print('QUI gönderildi')





    def start_download(self):
        fileChoise = self.resultOfSearch.currentItem().text()
        l = fileChoise.split(" ")

        numberOfChunks = int(l[2] / MB1)

        if (l[2] % MB1 != 0):
            numberOfChunks += 1
        md5 = l[1]

        for user in userList:
            if(userList[user][2] == 1):
                ClientStarter(userList[user][0], logQueue, clientDict, userList, user, uid, inDict)
                clientDict[user].put('SHC ' + md5)

        time.time(1)
        for user in userList:
            clientDict[user].put('QUI')


        time.sleep(1)

        for user in inDict['fUsers']:
            ClientStarter(inDict['fUsers'][user][0],logQueue,clientDict,userList,user,uid,inDict)
            clientDict[user].put('USR')

        time.sleep(1)



        dwdDict = {}
        for i in range(numberOfChunks):
            dwdDict[i] = False
        c = 0
        liste = []
        for x in inDict['fUsers']:
            liste.append((c,x))
            c += 1
        boyutListe = len(liste)

        count = 0
        self.completed = 0
        while count < (numberOfChunks - 1) :
            fileList = os.listdir('./tmp/')
            for i in fileList:
                b = i.split('-')
                if (b[0]==md5):
                    dwdDict[b[1]] = True
            counter = 0


            for d in dwdDict:
                if dwdDict[d] == False:
                    protocolMessage = 'DWL '+ md5+' '+str(d)

                clientDict[liste[counter][1]].put(protocolMessage)
                counter += 1
                if(counter == boyutListe):
                    counter = 0

            time.sleep(1)

            count = len(glob.glob1('./tmp/',md5+"-*"))
            self.completed = (100 / numberOfChunks) * count
            self.progress.setValue(self.completed)










    def sendMessage(self):
        message = self.messageToSend.toPlainText()

        print(message)

    def update_userList(self):
        for i in userList:
            self.userListWidget.addItem(i)



loggerThread = LoggerThread('LoggerTest',logQueue)
loggerThread.start()

serverStarter = ServerStarterThread('ServerStarterTest',logQueue,userList,uid,inDict)
serverStarter.start()
listUpdater = ListUpdaterThread('ListUpdatertest', logQueue, userList, str(uid))
listUpdater.start()



app = QtWidgets.QApplication(sys.argv)
a_window = Window()



sys.exit(app.exec_())