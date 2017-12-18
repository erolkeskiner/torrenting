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

def separete_to_chunks(filename,blocksize,mSum,N):

    with open(filename, "rb") as f:
        with open(str(mSum)+'.meta','w+') as meta:
            meta.write('FileName:' + f.name + '\n')
            statinfo = os.stat(f.name)
            meta.write('FileSize:'+str(statinfo.st_size)+'\n')
            meta.write('MD5SUM:'+mSum+'\n')
            meta.write('NumberOfChunks:'+str(N)+'\n')

        for i in range(N):
            with open('tmp/'+mSum+'-{}'.format(i),'wb') as o:
                o.write(f.read(blocksize))

def chunks_to_file(mSum,c):

    with open('out1.pdf','wb') as o:
        for i in range(c):
            with open('tmp/'+mSum+'-{}'.format(i),'rb') as chunk:
                o.write(chunk.read())



p = time.time()

fileName ='asd.pdf'

with open(fileName,'rb') as f:
    content = f.read()
    print (len(content))

    chunkSize = 10240 # as bytes

    fn, file_extension = os.path.splitext(fileName)

    print('File name: ')
    print(fn)
    print('File extension: ')
    print(file_extension)

    print (len(content)/chunkSize)
    chunkNumber = int(len(content)/chunkSize) + 1
    lastChunkSize = len(content) % chunkSize
    print('chunk sayısı')
    print(chunkNumber)
    print(lastChunkSize)
    m = md5sum(f.name)
    print('md5')
    print (type(m))
    #separete_to_chunks(fileName,2097152,m,chunkNumber)
    chunks_to_file(m,chunkNumber)



pEnd = time.time()

print (str(pEnd - p))

    
    
    
