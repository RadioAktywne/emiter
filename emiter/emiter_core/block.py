#block.py - tworzenie i zarządzanie blokami (np. zajawkowymi)

from emiter_core import cfg
import os.path

import json
import time
import logging

class Blocks:

    #init - definuje nowy typ bloku
    def __init__(self,path_schedule_file):

        #ładuj plik
        with open(path_schedule_file) as f:
            lst = json.load(f)

            self.blocktypes = lst["blocktypes"]
            self.blocks = lst["blocks"]
            
        # #kod np. ZAJ - zajawka PLS - playlista
        # self.code = code
        
        # #liquidsoap request id
        # self.rid = 'block'
        # self.cmd = self.rid+'.push '

        # #format
        # self.append_format = ""
        # if format != "":
        #     self.append_format = "."+format

        # #ścieżka otwierająca blok
        # self.opening_track = ''
        # if os.path.isfile(cfg.cfg['path_playlist']+'block/'+code+'_open.wav'):
        #     self.opening_track = cfg.cfg['path_playlist']+'block/'+code+'_open.wav'
        

        # #ścieżka zamykająca blok
        # self.closing_track = ''
        # if os.path.isfile(cfg.cfg['path_playlist']+'block/'+code+'_close.wav'):
        #     self.closing_track = cfg.cfg['path_playlist']+'block/'+code+'_close.wav'

        # #kontener (katalog w którym są pliki do odtworzenia)
        # self.container = cfg.cfg['path_playlist']+'block/'+code+'/'

    #parsowanie listy podzielonej jakimś znakiem do playlisty
    #zwraca tablicę ze ścieżkami
    def parse_block(self,str):
        #split elements
        tracks = str.split("|")

        #buduj listę plików
        files = []

        #gdy mamy jakieś elementy
        if str != "":
            if self.opening_track != '':
                files.append(self.cmd+self.opening_track)

            for track in tracks:
                files.append(self.cmd+self.container+track+self.append_format)

            if self.closing_track != '':
                files.append(self.cmd+self.closing_track)
            
        return files

    #szukanie czy jest blok
    #zwraca słownik z danymi
    def get_block(self,wd,h,m):
        #TODO
        pass

    #sprawdza czy jest blok i zwraca listę plików do odtworzenia
    def get_block_playout(self,wd,h,m):
        block = self.get_block(wd,h,m)

        filelist = []
        if block is not False:
            filelist = self.parse_block(block["script"])

        return filelist


    def get_block_now(self):
        #jak w program.py
        pass

    def get_block_playout_now(self):
        #jak w program.py
        pass
