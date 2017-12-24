import hashlib
import os
import time

writepath = 'outTest/'

def md5sum(filename, blocksize=2097152):
    hash = hashlib.md5()
    with open(filename, "rb") as f:
        for block in iter(lambda: f.read(blocksize), b""):
            hash.update(block)
    return hash.hexdigest()

def separate_to_chunks(filename,blocksize,mSum,N):

    with open('shared/'+filename, "rb") as f:
        with open(str(mSum)+'.meta','w+') as meta:
            meta.write('FileName:' + f.name + '\n')
            statinfo = os.stat(f.name)
            meta.write('FileSize:'+str(statinfo.st_size)+'\n')
            meta.write('MD5SUM:'+mSum+'\n')
            print(mSum)
            meta.write('NumberOfChunks:'+str(N)+'\n')

        for i in range(N):

            # dosyanın md5sumi ve chunkların sira numaraları seklinde isimlendirilmis chunklar tmp dizininde olusuyor
            with open('chunkManagement/tmp/'+mSum+'-{}'.format(i),'wb') as o:
                o.write(f.read(blocksize))


# burası scriptin oldugu dizinde
# ismi md5sum ve toplam chunk sayisi verilen dosyayı yaratır
def chunks_to_file(fileName,mSum,c):

    with open(fileName,'wb') as o:
        for i in range(c):
            with open('tmp/'+mSum+'-{}'.format(i),'rb') as chunk:
                o.write(chunk.read())



