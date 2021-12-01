#file.py - zarządzanie plikami, katalogami, czyszczenie i przerzuty

from emiter_core import cfg, validate_file as vf
import os
import sys
import time
import shutil
import audioread
import subprocess

import logging

#na serwerze RA (i u mnie na pc tak samo)
#uid = 33 #www-data
#gid = 133 #liquidsoap (grupa)

uid = cfg.cfg["file_uid"]
gid = cfg.cfg["file_gid"]

#akceptowane rozszerzenia plików audio
allow_exts = ["wav","mp3","ogg","flac"]

def create(path):
    # uwaga! to może robić tylko root. inaczej wywala błąd.
    try:
        os.mkdir(path)
        logging.info(path + " Utworzony")

        os.chown(path, uid, gid)
        os.chmod(path, 0o775)

    except FileExistsError:
        logging.info(path + " Juz istnieje")
    except PermissionError:
        logging.error("Skrypt nie ma uprawnień do tego. Musi to zrobić root.")
    except FileNotFoundError:
        logging.error("Katalog matka nie istnieje")


def create_audition_dirs(slug):
    path = cfg.cfg["path_auditions"] + slug

    create(path)
    create(path + "/powtorka")
    #create(path + "/powtorka/powtorka_puszki")
    create(path + "/archiwum")
    create(path + "/puszka")

def update_audition_dirs(slugs):
    #sprawdza wszystkie audycje i dodaje nowe, jeśli się takowe pojawiły
    for slug in slugs:
        if os.path.isfile(cfg.cfg['path_auditions']+slug) == False:
            if slug is not "":
                create_audition_dirs(slug)

    #todo może jakieś archiwizowanie dawnych audycji


def get_playout_files(slug,is_replay):
    """
    Szuka plików w katalogach audycji

    Args:
        slug - kod audycji
        is_replay - czy powtórka (True) czy puszka (False)
    Returns:
        list [{dur=długość w sekundach,  path=ścieżkę do pliku}, ...]
   

    """
    
    path = cfg.cfg["path_auditions"] + slug


    #sprawdź czy istnieje katalog audycji
    if not os.path.isdir(path):
        logging.error("Katalog dla audycji "+slug+" nie istnieje")

    #czy powtórka czy puszka?
    if is_replay:
        fp = path +'/powtorka/'
    else:
        fp = path +'/puszka/'

    return get_track_files(fp)

def get_track_files(fp):
    """
    Szuka plików audio i zwraca ich listę posortowaną alfabetycznie
    
    Args:
        fp - ścieżka    
    Returns:
        list [{dur=długość w sekundach,  path=ścieżkę do pliku}, ...]
    """
    file_list = []
    
    #sprawdź czy istnieje folder audycji
    if os.path.isdir(fp):

        #posortuj pliki 
        files = sorted(os.listdir(fp))

        for f in files:

            #rozszerzenie pliku
            file_ext = f.split(".")[-1]
            
            #rozmiar pliku
            stat = os.stat(fp+f)
            size = stat.st_size

            #jeśli plik większy niż 100kB i ma prawidłowe rozszerzenie
            if size > 1102400 and file_ext in allow_exts:
                logging.info(f+' ma więcej niż 100 kB, zwracam...')
                file_path = fp+f 
                dur = duration(file_path)
                file_list.append({"path":file_path,"duration":dur})
                
    else:
        logging.info('Katalog '+fp+' nie istnieje.')
    
    return file_list

def get_file_status(path):
    return vf.validate_file(path)


#wykonuje przerzut przed audycją wg nowej filozofii:
def replay_file_flow(slug):

    path = cfg.cfg["path_auditions"] + slug

    #szukaj plików w  /powtorka
    try:
        files = os.listdir(path+ '/powtorka')
    except:
        logging.warn("błąd, prawdopoddobnie nie ma katalogu dla audycji "+slug)
        return False
    
    #jeśli są, to przerzuć pliki do /archiwum
    for f in files:
        #przenoś tylko pliki a nie katalogi
        if not os.path.isdir(path+"/powtorka/"+f):
            os.rename(path + '/powtorka/'+f, path + '/archiwum/'+f)
            logging.info("przeniesiono plik "+ f)
        else:
            logging.info(f + " jest katalogiem")

    #szukaj pliku w /puszka
    try:
        files = os.listdir(path+ '/puszka')
    except:
        logging.info("błąd, prawdopoddobnie nie ma katalogu dla audycji "+slug)
        return False
    
    #jeśli są, to
    for f in files:   
        #przenoś tylko pliki a nie katalogi
        if not os.path.isdir(path+"/puszka/"+f):
            #kopiuj pliki do /powtorka
            try:
                shutil.copy(path + '/puszka/'+f, path + '/powtorka/')
                logging.info("plik "+f+" skopiowano pomyślnie do katalogu /powtorka")
            except IOError as e:
                logging.warn("Nie udało się skopiować pliku %s" % e)
            except:
                logging.warn("Unexpected error: ",sys.exc_info())
        else:
            logging.info(f + " jest katalogiem")




def clear_playout(slug):
    #czyści katalog /puszka
    path = cfg.cfg["path_auditions"] + slug

    #czyść katalog /powtorka
    logging.info("czyszczenie  /"+slug+"/puszka:")

    files = os.listdir(path+ '/puszka')
    for f in files:
        logging.info("\t"+f)
        os.remove(path+'/puszka/'+f)    

def merge_record_tracks(slug):
    path_temp_records = cfg.cfg["path_temp_records"]
    path_liquidsoap = cfg.cfg["path_liquidsoap_bin"]
    
    files = sorted(os.listdir(path_temp_records))
   
    files_to_merge_list = []
    files_to_merge = ""
    for f in files:
        #plik konczy się na RRRR-MM-DD_HH-MM-SS_slug
        if f.split("_")[-1] == slug+".ogg":
            files_to_merge_list.append(f)

    for f in files_to_merge_list:
        if files_to_merge != "":
            files_to_merge += "@"
        files_to_merge += (path_temp_records+f)


    #gdy są pliki do połączenia
    if files_to_merge != "":
        logging.info("merging files: "+files_to_merge)

        #nazwa pliku taka jak pierwszy plik z kolejki
        out_file_name = files_to_merge_list[0]
        out_file = cfg.cfg["path_auditions"] + slug + "/powtorka/"+ out_file_name

        #dodaj komendy
        subprocess.run([path_liquidsoap, cfg.cfg["home_path"]+"merge.liq","--", files_to_merge, out_file],check=True)
    else:
        logging.info("Nothing to merge")

def clear_cache_records():
    path = cfg.cfg["path_temp_records"]
    files = os.listdir(path)

    logging.info("Kasowanie plików z cache'a ("+path+"):")

    for f in files:
        if f.split(".")[-1] == "ogg":
            logging.info("\t"+f)
            os.remove(path+f)    

def clear_spy(days=21):
    """
        clears expired audio files from spy dir
    """
    secs_expire = days * 24 * 3600
    tnow = time.time()

    path = cfg.cfg["path_spy"]
    files = os.listdir(path)
    for f in files:
        time_file = os.path.getmtime(path+f)
        if tnow-time_file > secs_expire:
            logging.info("Removing expired file "+path+f+":")
            os.remove(path+f)




#długość pliku
def duration(path):
    d = 0
    #STUB
    #with audioread.audio_open(path) as f:
    #    d = int(f.duration)
    return d
