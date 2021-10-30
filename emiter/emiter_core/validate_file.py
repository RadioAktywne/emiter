# Sprawdzenie, czy podany plik audio zostanie poprawnie uruchomiony przez liquidsoap
#  
# Autor: Konrad Bratosiewicz
# e-mail: konrad.bratosiewicz@radioaktywne.pl
# wersja: 1.1.1

import os
import sys
import subprocess
import logging, logging.handlers
from emiter_core import cfg
from datetime import datetime

# Sciezki zapisu logow i plikow tymczasowych
TMP = "/tmp/validation"
LOG = '/var/log/emiter/validation.log'

# Konfiguracja loggera
logger = logging.getLogger('validate_file')
logger.setLevel(logging.DEBUG)

handler = logging.FileHandler(LOG, mode='a')
handler.setLevel(logging.DEBUG)

formatter = logging.Formatter(fmt='%(asctime)s %(name)-8s %(message)s', 
                              datefmt='%y-%m-%d %H:%M:%S')

handler.setFormatter(formatter)
logger.addHandler(handler)

# Nota: moze sie okazac, ze istnieje przypadek, ktorego nie wykryjemy w ten sposob
# - wtedy konieczne bedzie uwzglednienie tego tutaj
def parse_log():
    '''Otwórz log i sprawdz jego zawartosc'''
    with open(TMP, "r") as file:
        for line in file:                   # przejdz przez wszystkie linie
            pass
        file.close()
        return line.find("failed") == -1    # jezeli nie znajdziemy slowa 'failed'
                                            # w ostatniej linii pliku - plik jest poprawny


def validate_file(PATH):
    '''Sprawdzenie, czy podany plik audio zostanie poprawnie uruchomiony przez liquidsoap'''
    tmp = open(TMP, "w")
    bashCommand = "liquidsoap -r " + PATH
    liquidsoap = subprocess.call(bashCommand, stdout=tmp, stderr=tmp, shell=True)
    tmp.close()
    
    if parse_log() == True:
        logger.debug("OK: {}".format(PATH))
        return "OK"
    else:
        with open(TMP, 'rb') as tmp:
            logger.debug("Error: {}\n{}".format(PATH, tmp.read()))
        return "Error"

# Testowanie
if __name__ == "__main__":
    print(validate_file(sys.argv[1]))