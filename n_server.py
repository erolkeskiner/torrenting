import socket
import threading
import time
from multiprocessing import Queue
import pickle
import os


# logger threadimiz sadece ekrana basiyor ve QUIT yazarsak cikiyor
# dosyaya yazan seklinde degistirebiliriz
# burda cagiriliyor zaten
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


loggerQueue = Queue()
lThread = LoggerThread("NServerLoggerThread", loggerQueue)
lThread.start()


# Serverimizin aptal clienti
# liste yenilemede ve yeni baglantilari test etmede kullaniyoruz
# gerekli yerlerde cagriliyor zaten
class ServerIdiotClient (threading.Thread):
    def __init__(self, name, address, logQueue, fihrist, uid):
        threading.Thread.__init__(self)
        self.name = name
        self.address = address
        self.lQueue = logQueue
        self.fihrist = fihrist
        # karsi tarafin uuid degeri
        self.uid = uid

    def run(self):
        # baslayinca karsi tarafla baglanti kurup DLT komutunu gonderiyor
        # bu komut gerceklik testi(server testi yada download testi de diyorum)
        # yapmamizi sagliyor
        self.lQueue.put("Starting " + self.name)
        s = socket.socket()
        host = self.address
        port = 12345
        s.connect((host, port))
        s.send("DLT".encode())
        # komutu gonderdikten sonra dinlemeye basliyoruz. eger bize gonderecegi uuid
        # bizdeki uuid ile ayni ise okeyliyoruz
        # FIXME karsi taraf bize bisey gondermezse sonsuza kadar beklicek miyiz?
        while True:
            data = s.recv(1024).decode()
            data = data.strip().split(" ")
            if len(data) == 2:
                if data[0] == "ULT" and data[1] == self.uid:
                    if self.uid in self.fihrist:
                        # zaman damgasini basip okey veriyoruz
                        self.fihrist[self.uid][2] = 1
                        self.fihrist[self.uid][1] = time.ctime()
                        break
        self.lQueue.put("Exiting " + self.name)
        s.close()


# ip listelerini guncelleyen thread gerekli degerler verilip ana thread uzerinden cagirilacak
class ListUpdaterThread (threading.Thread):
    def __init__(self, name, address, logQueue, fihrist, uid, uid2):
        threading.Thread.__init__(self)
        self.name = name
        self.address = address
        self.lQueue = logQueue
        self.fihrist = fihrist
        # uid karsinin uuid
        self.uid = uid

    def run(self):
        while True:
            for a in self.fihrist:
                # her 4 dakika da bir listeyi kontrol ediyor. 10 dakikadir timestampi yenilenmemis olanlari ve
                # download testi gecmemis olanlari test ediyor gecerlerse zaman damgasi basip okey veriyor
                if self.fihrist[a][2] == 0 or (time.time() - time.mktime(self.fihrist[a][1]) > 600):

                    sic = ServerIdiotClient("ServerIdiotClient", self.address, self.lQueue, self.fihrist,
                                            self.uid)
                    sic.start()
                # 10 dakikadir baglantiyi duzgun kurammais birileri varsa onlarin testini false yapiyor(aslinda 0)
                if time.time() - time.mktime(self.fihrist[a][1]) > 600:
                    self.fihrist[a][2] = 0
            # 4 dakika bekle bu sayede 10 dakikalik izin suresi icinde 2 defa kontrol edilebilirler ve
            # gecikmelere tolerans gosterilebilir
            time.sleep(240)


# server threadimiz reader writer diye ayrilmadi cunku bir server threadinin birden fazla clienti ilgilendiren
# bir durumu yok. gerekirse bakariz
class ServerThread (threading.Thread):
    def __init__(self, name, sock, address, logQueue, fihrist, uid2):
        threading.Thread.__init__(self)
        self.name = name
        self.sock = sock
        self.address = address
        self.lQueue = logQueue
        self.fihrist = fihrist
        # uid karsi tarafin uuid degeri
        self.uid = False
        # uid2 bizim uuid degerimiz sistem basalarken bi tane olusturulup butun threadlere dagitilacak
        self.uid2 = uid2
        # gercek bir serveri var mi
        self.trueTest = 0
        self.exitf = 0

    def run(self):
        self.lQueue.put("Starting " + self.name)
        while not self.exitf:
            data = self.sock.recv(1024).decode()
            self.parser(data)
        self.lQueue.put("Exiting " + self.name)

    def parser(self, data):
        # Mesaji temizliyoruz
        msg = data.strip().split(" ")
        # Mesaj tek elamn ve TIC ise TOC gonder
        if len(msg) == 1 and msg[0] == "TIC":
            self.sock.send("TOC".encode())
        # server testi yapmak isteyene uuid degerimizi direk basiyoruz
        # gercek bir senaryoda guvenlik riski olusturur mu oturup tartismak gerek
        elif len(msg) == 1 and msg[0] == "DLT":
            self.sock.send(("ULT " + self.uid2).encode())
        # eger USR ile bize kayit olmamissa
        elif not self.uid:
            # USR <uuid> <(server mi peer mi)> toplamda uc tane eleman olcak
            # yoksa hata verdiricez
            if len(msg) != 3:
                val = "ERR: Need Login"
                self.lQueue.put(time.ctime() + "-" + str(self.address) + ": " + val)
                self.sock.send(val.encode())
            else:
                if msg[0] == "USR":
                    # msg[2] dedigimiz 1 ise peer, 0 ise N_Server. peer fihrist icinde yoksa
                    # kaydediyoruz ve downloadTest yapiyoruz
                    if msg[1] not in self.fihrist and (msg[2] == 0 or msg[2] == 1):
                        self.uid = msg[1]
                        self.sock.send(("HEL " + msg[1]).encode())
                        self.lQueue.put(time.ctime() + "-" + self.address + ":" + self.uid + " has added to list.\n")
                        # fihrist icinde sirasiyla adres, en son baglati zamani, gerceklik testi(downloadTest)
                        # false icin 0 true icin 1 ve son olarak peer mi server mi
                        self.fihrist[self.uid] = [self.address, time.ctime(), self.trueTest, msg[2]]
                        # serveri gercekten varmi diye bakiyoruz
                        sic = ServerIdiotClient("ServerIdiotClient", self.address, self.lQueue, self.fihrist,
                                                self.uid)
                        sic.start()
                    # peer fihrist icinde varsa zaman damgasini yenileyip test yapiyoruz
                    else:
                        self.lQueue.put(time.ctime() + "-" + self.address + ":" + self.uid + " has renewed.\n")
                        self.fihrist[self.uid][1] = time.ctime()
                        sic = ServerIdiotClient("ServerIdiotClient", self.address, self.lQueue, self.fihrist,
                                                self.uid)
                        sic.start()
                # 3 tane parametre gondermis ama birincisi USR degilse buraya girecek
                # neden bastan kontrol etmedin derseniz.. Bilmiyorum. O an mantikli gelmisti.
                else:
                    val = "ERR: Need Login"
                    self.lQueue.put(time.ctime() + "-" + str(self.address) + ": " + val)
                    self.sock.send(val.encode())
        # buraya girerse testi gecmis ve istedigini yapabilir
        elif self.trueTest:
            if len(msg) == 1 and msg[0] == "LSQ":
                self.sock.send(("LSA " + self.list_returner()).encode())
            # QUI komutu gelmisse bu thread kapatilacak main threadler hala calisiyor olacak ama
            elif len(msg) == 1 and msg[0] == "QUI":
                if self.uid in self.fihrist:
                    del self.fihrist[self.uid]
                self.exitf = 1

    # fihrist icindeki ip listesini string yapip donduruyor
    def list_returner(self):
        b = ""
        for a in self.fihrist:
            if self.fihrist[a][2] == 1:
                for c in self.fihrist[a]:
                    b += str(c) + "?"
                b = b.strip("?")
                b += "|"
        b = b.strip("|")
        return b

    # baskasindan aldigimiz liste stringini parcalayip fihristin icine atiyor
    # FIXME bu fonksiyon client icinde olacakti
    def list_parser(self, msg):
        # FIXME liste bos donerse ne olacak bakmak lazim
        msg = msg.strip("|").split("|")
        for a in msg:
            b = a.split("?")
            if not (b[0] in self.fihrist):
                self.fihrist[b[0]] = b[1:]
