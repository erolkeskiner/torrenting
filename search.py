#!/usr/bin/env python
# -*- coding: utf-8 -*-

import glob
import re
from difflib import SequenceMatcher
# bu import sıkıntı çıkarabilir linux'ta denemedim



# glob modulu bir dizindeki dosyaların isimlerini alabilmemizi saglayan modul






def search(fileName):
    list = []
    for name in glob.glob('./shared/*'):

        # print (name)
        x = name.split('\\')
        list.append(x[1])


    # print (list)

    # burada ismi dogru girene kadar bekletiyoruz kullanıcıyı
    # bunu arayuzde butonlarla sorarsak daha hızlı bir UX tasarlayabiliriz

    ask = fileName
    if ask in list:
        # print("%s file is in shared directory" % (ask))

        return  True, [ask]



    else:
        # print("file not found.")
        similarity = lambda x: SequenceMatcher(None, ask, x).ratio()
        m = sorted(list, key=similarity)
        m.reverse()
        if len(m) >= 3:
            return False,[m[0], m[1], m[2]]
        elif len(m) ==2:
            return False,[m[0],m[1]]
        elif len(m) ==1:
            return False,[m[0]]
        else:

            return False, []

