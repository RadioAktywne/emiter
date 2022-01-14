#autoplaylist - automatyczne tworzenie playlist

import mutagen
import json
import logging
import random
import os

from emiter_core import cfg

#importowanie dane z json-a
ap_config = cfg.cfg['auto_playlist_config']

#TODO
#walidacja i uzupełnianie brakujących danych brakującymi wartościami


def build_playlist(name,length=300):
    #buduje playlistę

    plist_codes = []
    plist = []

    #pobieranie listy kontenerów i ustalanie reguł ich miksowania
    containers = ap_config["playlists"][name]["mixing"]
    cont_regules = []
    cont_dirs = {}
    cont_files = {}

    #parsowanie zapisu min-max
    for c in containers.keys():
        min = containers[c]["min"]
        max = containers[c]["max"]
        
        if max < min:
            logging.error("Error reading max and min track number in container "+c)
            logging.error("Check auto_playlist_config.json for proper track number boundaries.")
            return

        #ustalanie warunków
        try:
            track_repeat = containers[c]["track_repeat"]
        except KeyError:
            track_repeat = 0

        try:
            album_repeat = containers[c]["album_repeat"]
        except KeyError:
            album_repeat = 0

        try:
            artist_repeat = containers[c]["artist_repeat"]
        except KeyError:
            artist_repeat = 0

        cont_regules.append({
                        'code':c,
                        'min':min,
                        'max':max,
                        'track_repeat':track_repeat,
                        'album_repeat':album_repeat,
                        'artist_repeat':artist_repeat
        })
        
        cont_path = ap_config['music_containers'][c]
        cont_dirs[c] = cont_path
        
        logging.info("Loading music container "+c+" ("+cont_path+")...")
        files = os.listdir(cont_path)
        logging.info(str(len(files))+" files loaded.")

        cont_files[c] = files

    cont_index = 0
    track_index = 0

    logging.info("buffering playlist")

    while len(plist) < length:
        if track_index == 0:
            
            #następny kontener
            cont_index += 1
            if cont_index >= len(cont_regules):
                cont_index = 0

            #losuj nową liczbę tracków
            track_index = random.randint(cont_regules[cont_index]["min"],cont_regules[cont_index]["max"])

        track_index -= 1
        cd = cont_regules[cont_index]["code"]
        
        files = cont_files[cd]

        #losuj plik z bazy
        file_passed = False
        while not file_passed:

            file_passed = True
            file_candidate = cont_dirs[cd]+files[(random.randint(0,len(files)-1))]

            #odczyt metadanych
            meta = mutagen.File(file_candidate)
            
            try:
                album = meta['album'][0]
            except (KeyError, TypeError):
                try:
                    album = meta['TALB'].text[0]
                except (KeyError, TypeError):
                    album = ""
            try:
                artist = meta['artist'][0]
            except (KeyError, TypeError):
                try:
                    artist = meta['TPE1'].text[0]
                except (KeyError, TypeError):
                    artist = ""

            #proces skanowania reszty playlisty
            scan_track_repeat = cont_regules[cont_index]["track_repeat"]
            scan_album_repeat = cont_regules[cont_index]["album_repeat"]
            scan_artist_repeat = cont_regules[cont_index]["artist_repeat"]
            
            for p in plist[::-1]:
                #jeśli kontener się zgadza
                if p["code"] == cd:
                    
                    #track_repeat
                    if scan_track_repeat > 0:
                        if p["file"] == file_candidate:
                            logging.debug("- odrzucono "+file_candidate)
                            file_passed = False
                            break

                        scan_track_repeat -= 1

                    if scan_album_repeat > 0:
                        if album != "" and album.lower() == p["album"].lower():
                            logging.debug("* odrzucono "+file_candidate)
                            file_passed = False
                            break

                        scan_album_repeat -= 1

                    if scan_artist_repeat > 0:
                        if artist != "" and artist.lower() == p["artist"].lower():
                            logging.debug("$ odrzucono "+file_candidate)
                            file_passed = False
                            break
                        scan_artist_repeat -= 1


                if scan_track_repeat == 0 and scan_album_repeat == 0 and scan_artist_repeat == 0:
                    #skończyły się tracki do skanowania
                    break    

        #gdy plik zatwierdzony
        plist.append({ "file":file_candidate, "artist":artist, "album":album, "code":cd })
        logging.debug("added "+file_candidate)
        
    #zapis do pliku
    pl_path = cfg.cfg["path_playlists"]+name+".csv"
    logging.info("zapis do "+pl_path)

    lines = 0
    with open(pl_path,mode='w', encoding="utf-8") as f:
        for i in range(0,len(plist)):
            f.write(plist[i]["code"] + ";" + plist[i]["file"]+"\n")
            lines += 1

    logging.info("wrote "+str(lines)+" lines")

def rebuild_all_playlists(length=300):
    logging.info("Rebuilding playlists...")
    #buduje wszystkie playlisty:
    for name in ap_config["playlists"].keys():
        build_playlist(name,length=length)

