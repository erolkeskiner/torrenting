import socket
import threading
import time
from multiprocessing import Queue
import pickle
import os
import uuid


class LoggerThread (threading.Thread):
    def __init__(self, name, lQueue):
        threading.Thread.__init__(self)
        self.name = name
        self.lQueue = lQueue

    def run(self):
        print(self.name + " starting.")
        while True:
            msg = self.lQueue.get()
            if msg == "QUIT":
                print(self.name + ": QUIT received.")
                break
            print(str(msg))
        print(self.name + " exiting.")


logQueue = Queue()
lThread = LoggerThread("LoggerThread", logQueue)
lThread.start()


class ServerThread (threading.Thread):
    def __init__(self, name, sock, address, logQueue, clientQueue, fihrist):
        threading.Thread.__init__(self)
        self.name = name
        self.sock = sock
        self.address = address
        self.lQueue = logQueue
        self.cQueue = clientQueue
        self.fihrist = fihrist
        self.uuid = False
        self.exitf = True
        self.trueTest = False

    def run(self):
        self.lQueue.put("Starting " + self.name)
        while self.exitf:
            data = self.sock.recv(1024).decode()
            self.parser(data)
        self.lQueue.put("Exiting " + self.name)

    def parser(self, data):
        msg = data.strip().split(" ")
        if len(msg) == 1 and msg[0] == "TIC":
            self.sock.send("TOC".encode())
        elif not self.uuid:
            if len(msg) != 3:
                val = "ERR: Need Login"
                self.lQueue.put(time.ctime() + "-" + str(self.address) + ": " + val)
                self.sock.send(val.encode())
            else:
                if msg[0] == "USR":
                    if msg[1] not in self.fihrist and (msg[2] == True or msg[2] == False):
                        self.uuid = msg[1]
                        self.sock.send(("HEL " + msg[1]).encode())
                        self.lQueue.put(time.ctime() + "-" + self.address + ":" + self.uuid + " has added to list.\n")
                        self.fihrist[self.uuid] = [self.address, time.ctime(), self.trueTest, msg[2]]
                        # TODO gerceklik testi gerceklestir
                    else:
                        self.lQueue.put(time.ctime() + "-" + self.address + ":" + self.uuid + " has renewed.\n")
                        self.fihrist[self.uuid][1] = time.ctime()
                        # TODO gerceklik testi gerceklestir
                else:
                    val = "ERR: Need Login"
                    self.lQueue.put(time.ctime() + "-" + str(self.address) + ": " + val)
                    self.sock.send(val.encode())
        elif self.trueTest:
            if len(msg) == 1 and msg[0] == "LSQ":
                peer_list_pickle = pickle.dumps(self.fihrist)
                # FIXME send komutuyla iki eleman gonderiliyor mu kontrol edilecek
                self.sock.send("LSA ".encode(), peer_list_pickle)
            elif len(msg) == 1 and msg[0] == "QUI":
                if self.uuid in self.fihrist:
                    del self.fihrist[self.uuid]
            elif len(msg) == 2:
                if msg[0] == "SHN":
                    list_of_files = os.listdir("./torrent_files")
                    if msg[1] in list_of_files:
                        meta_data_pickle = pickle.load(msg[1])
                        # FIXME send komutuyla iki eleman gonderiliyor mu kontrol edilecek
                        self.sock.send("VAN".encode(), meta_data_pickle)
                    else:
                        # TODO benzer isimleri dondurmeli
                        self.sock.send("YON".encode())
                elif msg[0] == "SHC":
                    list_of_files = os.listdir("./torrent_files")
                    if msg[1] in list_of_files:
                        # TODO meta datasi gonderilmeli
                        self.sock.send("VAC".encode())
                    else:
                        self.sock.send("YOC".encode())

            # TODO DWL komutu icin UPL komutu yazilmali

        # FIXME Parser henuz bitmedi!! MSG komutu eklenecek


class ClientThread (threading.Thread):
    def __init__(self, name, sock, address, logQueue, clientQueue, fihrist):
        threading.Thread.__init__(self)
        self.name = name
        self.sock = sock
        self.address = address
        self.lQueue = logQueue
        self.cQueue = clientQueue
        self.fihrist = fihrist
        self.uuid = False
        self.exitf = True
        self.trueTest = False

    def run(self):
            while self.exitf == 0:
                msg = self.cQueue.get()
                self.parser(msg)

    def parser(self, msg):
        msg = msg.strip().split(" ")
        # TODO uuid unique secilecek
        newUuid = uuid.uuid4()
        if len(msg) == 1 and msg[0] == "TIC":
            self.sock.send("TOC".encode())
        # FIXME burasi daha bitmedi!!