#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sys 
import os
import time
from datetime import datetime
from emiter_core import *
import json
import logging


logging.basicConfig(handlers=[logging.FileHandler('/var/log/emiter/emiter.log'),logging.StreamHandler()], level=logging.INFO,format='%(asctime)s %(levelname)s: %(message)s')


if sys.argv[1] in ["start","stop","restart"]:
    key = os.environ.get('AM_I_IN_DOCKER', False)
    if key:
        logging.warning("start/stop/restart functions are unavailable in docker container.")
        exit()

if sys.argv[1] == "start":
    autoplaylist.rebuild_all_playlists()
    liquidsoap.start()
    eventlog.log_message("PGM_START","")

elif sys.argv[1] == "stop":
    liquidsoap.stop()
    eventlog.log_message("PGM_STOP","")

elif sys.argv[1] == "restart":
    liquidsoap.stop()
    time.sleep(2)
    
    autoplaylist.rebuild_all_playlists()
    liquidsoap.start()
    eventlog.log_message("PGM_RESTART","")
        
elif sys.argv[1] == "rebuild_playlist":
    if sys.argv[2] == "all":
        autoplaylist.rebuild_all_playlists()
    else:
        autoplaylist.build_playlist(sys.argv[2])

else:
    #komendy "produkcyjne"

    #ramówka
    schedule = program.Program(cfg.cfg["url_program_api"])

    if sys.argv[1] == "maintain":
        #komenda konserwująca

        #1.utwórz foldery nowych audycji
        logging.info("Tworzenie nowych katalogów audycji...")
        auds = schedule.list_all_slugs()
        file.update_audition_dirs(auds)

        #3. jeśli nie studio, czyść nagrania tymczasowe w /srv/record
        file.clear_cache_records()
        
        #4. czyść stare pliki ze szpiega
        logging.info("czyszczenie szpiega")
        file.clear_spy(days=cfg.cfg['spy_days_stored'])


    elif sys.argv[1] == "force_push":
        #wymuś odtworzenie puchy
        liquidsoap.send("playout.push '"+ sys.argv[2] +"'")

    elif sys.argv[1] == "push":

        if sys.argv[2] == 'playout':
            #pobierz info o aktualnej audycji
            aud = schedule.get_program_with_split_now(True)

            #czy jest audycja?
            if aud['found']:
                #czy audycja się zaczyna?
                if aud['changed']:
                    #pobierz ścieżkę do puchy
                    playouts = file.get_playout_files(aud['slug'],aud['replay'])

                    if len(playouts) > 0:
                        if aud['replay']:
                            eventlog.log_message("REPLAY_REQEST",aud['slug'])
                        else:
                            eventlog.log_message("PLAYOUT_REQUEST",aud['slug'])
                        
                        for playout in playouts:
                            liquidsoap.send("playout.push '"+ playout['path'] +"'")
                            logging.info("request pliku "+playout['path'])
                            time.sleep(0.5)
                    else:
                        logging.info(aud['slug']+ ": brak plików")
                else:
                    logging.info('audycja już trwa')

            else:
                logging.info('pusty slot')


        elif sys.argv[2] == "block":
            logging.info("under construction")
            #TODO - wdrożyć pełną obsługę bloków

    elif sys.argv[1] == "archive_replay":
        #czy zaczęła sie jakaś audycja?
        aud = schedule.get_program_with_split_now(True,time_margin=15)

        if aud['changed']:
            #czy to nie jest playlista ani nie powtorka?
            #czy to nie jest playlista
            if aud['found']:
                #czy to nie powtórka?
                if aud["replay"] == False:
                    logging.info("audycja "+aud['slug']+" zaczyna się, dokonuje przerzutu")
                    
                    #archiwizuj
                    file.replay_file_flow(aud['slug'])
                else:
                    logging.info("będzie powtorka, nic nie robie")
            else:
                logging.info("będzie playlista, nic nie robie")
        else:
            logging.info("nie zaczyna się żadna audycja")

    elif sys.argv[1] == "set_replay":
        #czy skończyła sie jakaś audycja?
        aud = schedule.get_program_with_split_now(False,time_margin=15)

        if aud['changed']:
            #czy to nie jest playlista ani nie powtorka?
            #czy to nie jest playlista
            if aud['found']:
                #czy to nie powtórka?
                if aud["replay"] == False:
                    logging.info("audycja "+aud['slug']+" zakończyła się")
                    file.merge_record_tracks(aud["slug"])
                else:
                    logging.info("była powtórka, nic nie robię")
            else:
                logging.info("była playlista, nic nie robie")
        else:
            logging.info("nie zakończyła się żadna audycja")

    elif sys.argv[1] in ["clear_playout","force_skip","status"]:
        #poniższe komendy wymagają statusu
        status = liquidsoap.status()
        if status['alive']:
            if sys.argv[1] == "clear_playout":
                #czy skończyła sie jakaś audycja?
                aud = schedule.get_program_with_split_now(False,time_margin=15)

                if aud['changed']:
                    #czy to nie jest playlista
                    if aud['found']:
                        #czy to nie powtórka?
                        if aud["replay"] == False:
                            logging.info("audycja "+aud['slug']+" zakończyła się")
                            #sprawdź, czy przypadkiem jeszcze nie gra plik
                            if status["source"] == "playout" and aud['slug'] in status['filename']:
                                logging.info("Chyba nie zakończyło się granie audycji " + aud['slug'] + ". Gra plik "+ status['filename']+". Skipuje..")
                                liquidsoap.send("PGM.skip")
                                time.sleep(5)
                            
                            file.clear_playout(aud['slug'])
                        else:
                            logging.info("była powtórka, nic nie robię")
                    else:
                        logging.info("była playlista, nic nie robie")
                else:
                    logging.info("nie zakończyła się żadna audycja")


            elif sys.argv[1] == "force_skip":
                #skipowanie utworów przed puszką
                if status["playout_ready"]:
                    try:
                        src = status["source"]
                    except KeyError:
                        #zdarza się, że metadane uciekną...
                        src = ""

                    if "playlista" in src:
                        logging.info("załadowano puszkę a gra muzyka, skipuję...")
                        liquidsoap.send("PGM.skip")
                    else:
                        logging.info("gra puszka lub studio, nie skupuję...")
                else:
                    logging.info("nie ma załadowanej puszki")

            elif sys.argv[1] == "status":
                print(status)

        else:
            logging.error("proces liquidsoapa nie odpowiedział prawidłowym statusem")
    else:
        logging.warning("nieznana komenda")





