#!/usr/bin/python3
# -*- coding: utf-8 -*-

import os
import sys

path = sys.argv[1] + "/"
files = os.listdir(path)

for f in files:
    fn = f.encode("ascii","replace").decode()

    #czy nazwa się zmieniła
    if f == fn:
        print("Plik "+f+" nie zawiera znaków spoza ASCII. zostawiam.")
    else:
        #sprawdza, czy nazwa pliku się nie powtarza
        if os.path.isfile(fn):
            print("Plik "+fn + " istnieje")
            index = 1

            while True:

                test_fn = str(index) + "_" + fn
                if not os.path.isfile(test_fn):
                    fn = test_fn
                    break
                else:
                    print("Plik "+test_fn + " istnieje")
                    index +=1
        
        print("Zmiana nazwy na "+fn)
        os.rename(path+f,path+fn)
        

