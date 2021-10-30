#eventlog - logowanie do pliku playout.csv

from emiter_core import cfg
import time

#zaloguj wiadomość do log.csv
def log_message(code,slur):
    path = '/var/log/emiter/playout.csv'

    stamp = time.strftime("%Y-%m-%d_%H-%M-%S")

    with open(path,mode='a', encoding="utf-8") as f:
        f.write(stamp + ";" + code + ";" + slur +"\n")
