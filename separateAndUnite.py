import hashlib
import os
import time
import pickle



def md5sum(filename, blocksize):

    hash = hashlib.md5()
    with open('shared/'+filename, "rb") as f:
        for block in iter(lambda: f.read(blocksize), b""):
            hash.update(block)
    return hash.hexdigest()

def makeMeta(filename,blocksize):
    mSum = md5sum(filename)
    filePath = 'shared/'+filename

    with open(filePath, "rb") as f:
        content = f.read()

        fn, file_extension = os.path.splitext(filename)

        chunkNumber = int(len(content) / blocksize) + 1
        statinfo = os.stat(f.name)
        dict = {'FileName': filename, 'FileSize':str(statinfo.st_size),'MD5SUM':mSum,'NumberOfChunks':chunkNumber}
        print(dict)
        pickle_out = open('meta/'+str(mSum)+'.pickle', 'wb')
        pickle.dump(dict,pickle_out)
        pickle_out.close()

def separete_to_chunks(filename,blocksize):
    filePath = 'shared/'+filename
    mSum = md5sum(filename)
    with open(filePath, "rb") as f:
        content = f.read()

        fn, file_extension = os.path.splitext(filename)

        chunkNumber = int(len(content) / blocksize) + 1
        statinfo = os.stat(f.name)
        dict = {'FileName': filename, 'FileSize':str(statinfo.st_size),'MD5SUM':mSum,'NumberOfChunks':chunkNumber}

        pickle_out = open('meta/'+str(mSum)+'.pickle', 'wb')
        pickle.dump(dict,pickle_out)
        pickle_out.close()


    with open(filePath,"rb") as f:
        for i in range(chunkNumber):
            with open('tmp/'+mSum+'-{}'.format(i),'wb') as o:
                o.write(f.read(blocksize))

def chunks_to_file(mSum):
    pickle_in = open('meta/'+str(mSum)+'.pickle', 'rb')
    dict = pickle.load(pickle_in)
    pickle_in.close()
    fileName = dict['FileName']
    print(dict['FileName'])
    fn, ext = os.path.splitext(fileName)
    c = dict['NumberOfChunks']


    with open('downloaded/'+fn+ext,'wb') as o:
        for i in range(c):
            with open('tmp/'+mSum+'-{}'.format(i),'rb') as chunk:
                o.write(chunk.read())
            os.remove('tmp/' + mSum + '-{}'.format(i))







fileName ='DSCF3403.MOV'
chunkSize = 1048576 # as bytes




m = md5sum(fileName)
print(m)

#makeMeta(fileName,chunkSize)

#separete_to_chunks(fileName,chunkSize)
chunks_to_file(m)






    
    
    
