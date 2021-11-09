#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sys 
import os
import time
from datetime import datetime
from emiter_core import *
import json
import logging

#from toolbox.api_integration import get_timeslots


#logging setup
if sys.argv[1] == "get":
    #ponieważ get wysyła informacje w stdout do innych procesów, loguj tylko błędy
    logging.basicConfig(level=logging.ERROR,format='%(asctime)s %(levelname)s: %(message)s')
else:
    #normalny loglevel
    logging.basicConfig(handlers=[logging.FileHandler('/var/log/emiter/emiter.log'),logging.StreamHandler()], level=logging.DEBUG,format='%(asctime)s %(levelname)s: %(message)s')


if sys.argv[1] == "start":
    #get_timeslots.sync(cfg.cfg["path_schedules"])
    autoplaylist.rebuild_all_playlists()
    liquidsoap.start()
    eventlog.log_message("PGM_START","")

elif sys.argv[1] == "stop":
    liquidsoap.stop()
    eventlog.log_message("PGM_STOP","")

elif sys.argv[1] == "restart":
    liquidsoap.stop()
    time.sleep(2)
    
    #get_timeslots.sync(cfg.cfg["path_schedules"])
    autoplaylist.rebuild_all_playlists()
    liquidsoap.start()
    eventlog.log_message("PGM_RESTART","")

#eksperymentalnie
elif sys.argv[1] == "fg":
    autoplaylist.rebuild_all_playlists()
    proc = liquidsoap.run()
    try:
        liquidsoap.trace(proc)
    except KeyboardInterrupt:
        liquidsoap.kill(proc)

        
elif sys.argv[1] == "rebuild_playlist":
    if sys.argv[2] == "all":
        autoplaylist.rebuild_all_playlists()
    else:
        autoplaylist.build_playlist(sys.argv[2])
    
elif sys.argv[1] == "update":
    
    #TODO
    #wywalamy integrację przez pliki
    #przesyłamy dane o puszkach w jakiś inny sposób
    #np przez API
    #zmieniamy format po stronie klienta na zgodny z API
    print("Under construction")


else:
    #komendy "produkcyjne"

    #ramówka
    schedule = program.Program(cfg.cfg["url_program_api"])

    #status
    status = liquidsoap.status()
    if status['alive']:
    #proces żyje, można wydawać komendy

        if sys.argv[1] == "force_push":
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
                            eventlog.log_message("PLAYOUT_REQEST",aud['slug'])
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

        elif sys.argv[1] == "archive":
            #TODO

            #czy skończyła sie jakaś audycja?
            aud = schedule.get_program_with_split_now(False)

            if aud['changed']:
                #czy to nie jest playlista ani nie powtorka?
                if aud['replay'] == False and aud['found']:
                    logging.info("audycja "+aud['slur']+" zakonczyła się, archiwizuje")
                    
                    #archiwizuj
                    file.replay_file_flow(aud['slug'])
                else:
                    logging.info("była playlista lub powtorka, nic nie robie")
            else:
                logging.info("nie zakończyła się żadna audycja")

        elif sys.argv[1] == "archive_replay":
            #czy zaczęła sie jakaś audycja?
            aud = schedule.get_program_with_split_now(True,time_margin=15)

            if aud['changed']:
                #czy to nie jest playlista ani nie powtorka?
                if aud['replay'] == False and aud['found']:
                    logging.info("audycja "+aud['slug']+" zaczyna się, dokonuje przerzutu")
                    
                    #archiwizuj
                    file.replay_file_flow(aud['slug'])
                else:
                    logging.info("będzie playlista lub powtorka, nic nie robie")
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

        elif sys.argv[1] == "clear_playout":
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

        elif sys.argv[1] == "maintain":
            #komenda konserwująca

            #1.utwórz foldery nowych audycji
            logging.info("Tworzenie nowych katalogów audycji...")
            auds = schedule.list_all_slugs()
            file.update_audition_dirs(auds)

            #3. jeśli nie studio, czyść nagrania tymczasowe w /srv/record
            file.clear_cache_records()
            
            #4. czyść stare pliki ze szpiega

            

        else:
            logging.warning("nieznana komenda")

    else:
        logging.error("proces liquidsoapa umarł")
        #TODO jakiś restart czy coś




