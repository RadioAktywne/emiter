#!/usr/bin/python3

import httplib2
import os
import sys

from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage

import uuid
import json
import logging

# try:
#     import argparse
#     flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
# except ImportError:
#     flags = None

# If modifying these scopes, delete your previously saved credentials
# at ~/.credentials/sheets.googleapis.com-python-quickstart.json
SCOPES = 'https://www.googleapis.com/auth/spreadsheets.readonly'
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'Google Sheets API Python Quickstart'

pos1=0
pos2=0

def get_credentials():
    """Gets valid user credentials from storage.

    If nothing has been stored, or if the stored credentials are invalid,
    the OAuth2 flow is completed to obtain the new credentials.

    Returns:
        Credentials, the obtained credential.
    """
    home_dir = os.path.dirname(__file__)
    credential_dir = os.path.join(home_dir, '.credentials')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir,
                                   'ralssynch.json')

    store = Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        if flags:
            credentials = tools.run_flow(flow, store, flags)
        else: # Needed only for compatibility with Python 2.6
            credentials = tools.run(flow, store)
        logging.info('Storing credentials to ' + credential_path)
    return credentials


#def parse_program_timeslots(schedule, programs):
def parse_program_timeslots(schedule,program_list):
    
    #krok w minutach
    step = 30

    #wczytaj programy
    programs = {}
    programs_by_slug = {}
    for p in program_list:
        slug = p[0]
        name = p[1].encode().decode('utf-8')
        rds = p[2].encode().decode('utf-8')

        #czy slug poprawny (zawiera tylko litery lub cyfry)
        if slug.isalnum():
            pgm_dict = {
                "slug":slug,
                "name":name,
                "rds":rds,
                "broadcast_visible":True
            }
            programs[str(uuid.uuid4())] = pgm_dict
            programs_by_slug[slug] = pgm_dict
            
    
    #print(programs)

    timeslots = {}

    row = 0
    col = 1
    cell = schedule[row][col]

    start_weekday = 1
    start_h = 0
    start_m = 0

    pgm_len = 0
    pgm_weekday = 0
    pgm_start_h = 0
    pgm_start_m = 0
    back_to_begin = False
    #scan schedule
    while True:
        slug = schedule[row][col]

        if slug != cell:
            #początek timeslotu
            cell = slug
            
            #nowy timeslot
            pgm_weekday = weekday
            pgm_start_h = start_h
            pgm_start_m = start_m

            pgm_len = step

        else:
            #gdy kontynuacja audycji
            #zwiększ licznik
            pgm_len += step
            
        #krok do przodu
        row+=1

        start_m += step
        while start_m >= 60:
            start_h += 1
            start_m -= 60

        if '-' in schedule[row][col]:
            row = 0
            col +=1

            start_h = 0
            start_m = 0

            if col > 7:
                col = 1
                back_to_begin = True

        weekday = col
        slug = schedule[row][col]

        if slug != cell:
            #koniec timeslotu
            if cell.lower() != "playlista":

                #czy powtórka?
                replay = cell[-2:] == "_p"
                if replay:
                    pgm_slug = cell.split("_")[0]
                else:
                    pgm_slug = cell

                #print("%s from %d - %d:%d dur %d REPL %s" % (pgm_slug,pgm_weekday,pgm_start_h,pgm_start_m,pgm_len,str(replay)))

                #sprawdź, czy jest program na liście audycji
                if pgm_slug in programs_by_slug.keys():
                    pgm_data = programs_by_slug[pgm_slug].copy()
                else:
                    #dane zastępcze
                    pgm_data = { "slug": pgm_slug, "name": pgm_slug, "rds": pgm_slug, "broadcast_visible":True }
                    
                #twórz nowe rekordy
                slot = {
                    "weekday":pgm_weekday,
                    "begin_h":pgm_start_h,
                    "begin_m":pgm_start_m,
                    "duration":pgm_len,
                    "program": pgm_data, 
                    "replay": replay
                }

                timeslots[str(uuid.uuid4())] = slot


            #gdy pełen obrót
            if back_to_begin:
                #wyjdź z pętli
                break
        
    #gdy  ta sama audycja na początku i końcu ramówki
    ts_keys = list(timeslots.keys())
    fst = ts_keys[0]
    last = ts_keys[-1]
    if timeslots[fst]["program"]["slug"] == timeslots[fst]["program"]["slug"] and timeslots[last]["replay"] == timeslots[last]["replay"]:
        logging.info("audycja "+timeslots[fst]["program"]["slug"] +" przechodzi przez koniec tygdonia, usuwam duplikat")
        del timeslots[fst]

    return timeslots, programs

def sync(path):
    """Shows basic usage of the Sheets API.

    Creates a Sheets API service object and prints the names and majors of
    students in a sample spreadsheet:
    https://docs.google.com/spreadsheets/d/1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms/edit
    """
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    discoveryUrl = ('https://sheets.googleapis.com/$discovery/rest?'
                    'version=v4')
    service = discovery.build('sheets', 'v4', http=http,
                              discoveryServiceUrl=discoveryUrl)

    spreadsheetId = '1xm5rDlxo6YlnIQjQRubALrVTtagnqorUIpues5ud0ng'
    rangeName = '[EMITER]ramowka!A1:H49'
    result = service.spreadsheets().values().get(
        spreadsheetId=spreadsheetId, range=rangeName).execute()
    schedule = result.get('values', [])
    
    programsRangeName = '[EMITER]audycje!A1:C100'
    result = service.spreadsheets().values().get(
        spreadsheetId=spreadsheetId, range=programsRangeName).execute()
    programs = result.get('values', [])
    
    ts,pgms = parse_program_timeslots(schedule,programs)
    
    
    if path is not None:
        with open(path+"/timeslots",mode='w', encoding="utf-8") as f:
            f.write(json.dumps(ts))
        with open(path+"/programs",mode='w', encoding="utf-8") as f:
            f.write(json.dumps(pgms))
    else:
        print(ts)
        print("---")
        print(pgms)

if __name__ == '__main__':
    if len(sys.argv) == 2:
        sync(sys.argv[1])
    else:
        sync(None)
