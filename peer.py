import socket
import threading
import time
from multiprocessing import Queue
import pickle
import os

MB1 = 1048576

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
lThread = LoggerThread("PeerLoggerThread", loggerQueue)
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
        port = 55555
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
        # bizim uuid
        self.uid2 = uid2

    def run(self):
        self.lQueue.put("Starting " + self.name)
        while True:
            for a in self.fihrist:
                # kendi serverimizi test etmeye gerek yok
                if a == self.uid2:
                    continue
                # her 4 dakika da bir listeyi kontrol ediyor. 10 dakikadir timestampi yenilenmemis olanlari ve
                # download testi gecmemis olanlari test ediyor gecerlerse zaman damgasi basip okey veriyor
                if self.fihrist[a][2] == 0:

                    sic = ServerIdiotClient("ServerIdiotClient", self.address, self.lQueue, self.fihrist,
                                            self.uid)
                    sic.start()
                # 10 dakikadir baglantiyi duzgun kurammais birileri varsa onlarin testini false yapiyor(aslinda 0)
                if time.time() - time.mktime(self.fihrist[a][1]) > 600:
                    self.fihrist[a][2] = 0
                # 20 dakikadir baglanamiyorsak listeden cikariyoruz
                if time.time() - time.mktime(self.fihrist[a][1]) > 1200:
                    del self.fihrist[a]
            # 4 dakika bekle bu sayede 10 dakikalik izin suresi icinde 2 defa kontrol edilebilirler ve
            # gecikmelere tolerans gosterilebilir
            time.sleep(240)
        # FIXME program kapatilirken donguden cikmasi gerek
        # self.lQueue.put("Exiting " + self.name)


# server threadimiz reader writer diye ayrilmadi cunku bir server threadinin birden fazla clienti ilgilendiren
# bir durumu yok. gerekirse bakariz
class ServerThread (threading.Thread):
    def __init__(self, name, sock, address, logQueue, fihrist, uid2, interface_queue):
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
        self.ifrQueue = interface_queue

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
            elif len(msg) == 2:
                # Search komutlari burda
                if msg[0] == "SHN":
                    list_of_files = os.listdir("./torrent_files")
                    if msg[1] in list_of_files:
                        a = self.meta_data_returner(msg[1])
                        self.sock.send(("VAN " + " ".join(a)).encode())
                    else:
                        # TODO benzer isimleri dondurmeli
                        self.sock.send("YON".encode())
                elif msg[0] == "SHC":
                    list_of_files = os.listdir("./torrent_files")
                    if msg[1] in list_of_files:
                        self.sock.send("VAC".encode())
                    else:
                        self.sock.send("YOC".encode())
            elif len(msg) == 3 and msg[0] == "DWL":
                if msg[1] in os.listdir("./torrent_files/"):
                    chunk = self.chunk_returner(msg[1], msg[2])
                    self.sock.send(("UPL " + " ".join([msg[1:], str(chunk)])).encode())
                else:
                    self.sock.send("ERR: File does not exists.".encode())
            elif len(msg) >= 3 and msg[0] == "MSG":
                if msg[1] == self.uid2:
                    self.sock.send("MOK".encode())
                    self.ifrQueue.put("MSG " + " ".join(msg[1:]))
                else:
                    self.sock.send(("MNO " + msg[1]).encode())


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

    def chunk_returner(self, md5sum, chunk_no):
        with open("./torrent_files/" + md5sum, 'rb') as file:
            file.seek(MB1*chunk_no)
            return file.read(MB1)

    def meta_data_returner(self, filename):
        with open("./torrent_files/" + filename, "rb") as f:
            msg = f.readline()
            msg = str(msg.strip())
            a = []
            a.append(msg)
            msg = f.readline()
            msg = str(msg.strip())
            a.append(msg)
            return a

# client threadimiz. isteklerde bulunacak threadimiz
class ClientWriterThread (threading.Thread):
    def __init__(self, name, sock, address, logQueue, clientQueue, fihrist, uid2):
        threading.Thread.__init__(self)
        self.name = name
        self.sock = sock
        self.address = address
        self.lQueue = logQueue
        self.cQueue = clientQueue
        self.fihrist = fihrist
        # TODO uuid unique secilecek
        self.uid2 = uid2
        self.exitf = False

    def run(self):
        self.lQueue.put("Starting " + self.name)
        while not self.exitf:
            msg = self.cQueue.get()
            self.parser(msg)
        self.lQueue.put("Exiting " + self.name)

    def parser(self, msg):
        msg = msg.strip().split(" ")
        if len(msg) == 1 and msg[0] == "TIC":
            self.sock.send("TIC".encode())
        elif len(msg) == 1 and msg[0] == "LSQ":
            self.sock.sen("LSQ".encode())
        elif len(msg) == 1 and msg[0] == "QUI":
            self.sock.send("QUI".encode())
            self.exitf = 1
        elif len(msg) == 1 and msg[0] == "USR":
            self.sock.send(("USR " + self.uid2 + " 1").encode())
        elif len(msg) == 2 and msg[0] == "SHN":
            self.sock.send(("SHN " + msg[1]).encode())
        elif len(msg) == 2 and msg[0] == "SHC":
            self.sock.send(("SHC " + msg[1]).encode())
        elif len(msg) == 3 and msg[0] == "MSG":
            self.sock.send(("MSG " + msg[1] + " " + " ".join(msg[2:])).encode())
        elif len(msg) == 3 and msg[0] == "DWL":
            self.sock.send("DWL " + msg[1] + " " + msg[2])

        # FIXME burasi daha bitmedi!!


class ClientReaderThread (threading.Thread):
    def __init__(self, name, sock, address, logQueue, clientQueue, fihrist, uid2, interface_reader_queue):
        threading.Thread.__init__(self)
        self.name = name
        self.sock = sock
        self.address = address
        self.lQueue = logQueue
        self.cQueue = clientQueue
        self.fihrist = fihrist
        # TODO uuid unique secilecek
        self.uid2 = uid2
        self.exitf = False
        self.ifrQueue = interface_reader_queue
        self.meta_exists = 0

    def run(self):
        self.lQueue.put("Starting " + self.name)
        while not self.exitf:
            msg = self.sock.recv(MB1 + 64).decode()
            self.parser(msg)
        self.lQueue.put("Exiting " + self.name)

    def parser(self, msg):
        msg = msg.strip().split(" ")
        if len(msg) == 2 and msg[0] == "LSA":
            self.list_parser(msg[1])
            self.ifrQueue.put("List has renewed")
        elif len(msg) == 1 and msg[0] == "HEL":
            self.ifrQueue.put(msg[0])
        elif len(msg) >= 2 and msg[0] == "REJ":
            self.ifrQueue.put(" ".join(msg))
        elif len(msg) >= 2 and msg[0] == "VAN":
            self.ifrQueue.put(" ".join(msg))
        elif len(msg) >= 1 and msg[0] == "YON":
            self.ifrQueue.put(" ".join(msg))
        elif len(msg) == 1 and msg[0] == "VAC":
            self.ifrQueue.put(" ".join(msg))
        elif len(msg) >= 1 and msg[0] == "YOC":
            self.ifrQueue.put(" ".join(msg))
        elif len(msg) == 1 and msg[0] == "MOK":
            self.ifrQueue.put(msg[0])
        elif len(msg) == 2 and msg[0] == "MNO":
            self.ifrQueue.put(" ".join(msg))
        elif len(msg) >= 4 and msg[0] == "UPL":
            # FIXME chunkin sonu bosluk karakteri falansa ne olacak?
            self.chunk_writer(msg[1], msg[2], " ".join(msg[3:]))


    # baskasindan aldigimiz liste stringini parcalayip fihristin icine atiyor
    def list_parser(self, msg):
        # FIXME liste bos donerse ne olacak bakmak lazim
        msg = msg.strip("|").split("|")
        for a in msg:
            b = a.split("?")
            if not (b[0] in self.fihrist):
                self.fihrist[b[0]] = b[1:]

    def chunk_writer(self, md5sum, chunk_no, chunk_data):
        chunk_data = chunk_data.encode()
        with open("./torrent_files/" + md5sum, "wb+") as f:
            f.seek(MB1*chunk_no)
            f.write(chunk_data)


class ServerStarterThread (threading.Thread):
    def __init__(self, name, sock, address, logQueue, fihrist, uid2, interface_queue):
        threading.Thread.__init__(self)
        self.name = name
        self.sock = sock
        self.address = address
        self.lQueue = logQueue
        self.fihrist = fihrist
        # uid2 bizim uuid degerimiz sistem basalarken bi tane olusturulup butun threadlere dagitilacak
        self.uid2 = uid2
        # gercek bir serveri var mi
        self.exitf = 0
        self.ifQueue = interface_queue

    def run(self):
        self.lQueue.put("Starting " + self.name)
        s = socket.socket()
        host = "0.0.0.0"
        port = 55555
        s.bind((host, port))
        s.listen(100)

        thread_c = 0

        while not self.exitf:
            self.lQueue.put("Waiting for connection..." + "\n")
            c, a = s.accept()
            self.lQueue.put("Got connection from " + str(a) + "\n")
            thread_c += 1
            sThread = ServerThread("ServerThread-" + str(thread_c), c, a, self.lQueue, self.fihrist, self.uid2, self.ifQueue)
            sThread.start()

        # FIXME programi kapatirken donguden cikilmali
        self.lQueue.put("Exiting " + self.name)












