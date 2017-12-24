#!/usr/bin/env python
# -*- coding: utf-8 -*-

import glob
import re
from difflib import SequenceMatcher
# bu import sıkıntı çıkarabilir linux'ta denemedim
from chunkManagement import separateAndUnite
import hashlib
import os

# glob modulu bir dizindeki dosyaların isimlerini alabilmemizi saglayan modul


pattern = "([0-9\s]*)\s---\s(.*)$"
list= []

# eski odevden similarity suggestions gerceklemesi
def parser(fileName):
    ret = {}
    with open(fileName,'r') as f:
        for line in f:
            searchObj = re.match(pattern,line)
            if searchObj:
                ret[searchObj.group(2)] = searchObj.group(1)
    return ret

def main():
    for name in glob.glob('shared/*'):
        print (name)
        x = name.split('\\')
        list.append(x[1])


    print (list)

    # burada ismi dogru girene kadar bekletiyoruz kullanıcıyı
    # bunu arayuzde butonlarla sorarsak daha hızlı bir UX tasarlayabiliriz
    while True:
        ask = input("File Name: ")
        if ask in list:
            print("%s file is in shared directory" % (ask))
            print('Do you want me to chunk it for you?')
            answer=input('Decision')
            if(answer == 'y'):

                # bu scripti calistirdigin dizinde bir shared klasoru bulunmalı
                # bu dizin paylasima acik olan dizin
                with open('shared/'+ask, 'rb') as f:
                    content = f.read()
                    print(len(content))

                    chunkSize = 10240  # as bytes

                    fn, file_extension = os.path.splitext(ask)

                    print('File name: ')
                    print(fn)
                    print('File extension: ')
                    print(file_extension)

                    print(len(content) / chunkSize)
                    chunkNumber = int(len(content) / chunkSize) + 1
                    lastChunkSize = len(content) % chunkSize
                    print('chunk sayısı')
                    print(chunkNumber)
                    print(lastChunkSize)
                    m = separateAndUnite.md5sum(f.name)
                    print('md5')
                    print(type(m))
                    separateAndUnite.separate_to_chunks(ask,2097152,m,chunkNumber)
                    #chunks_to_file(m, chunkNumber)


        else:
            print("file not found.")
            similarity = lambda x: SequenceMatcher(None, ask, x).ratio()
            m = sorted(list, key=similarity)
            m.reverse()
            print("Did you mean: %s or %s or %s" % (m[0], m[1], m[2]))


if __name__ == '__main__':
    main()