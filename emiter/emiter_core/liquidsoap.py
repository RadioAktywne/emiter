
#liquidsoap.py - integracja python -> liquidsoap

from emiter_core import cfg

from json.decoder import JSONDecodeError
import os
import time
import logging
import json
import subprocess

user = cfg.cfg['default_user']
cmd = "/home/"+user+"/.opam/4.08.0/bin/liquidsoap -d "
cmd_fg = "/home/"+user+"/.opam/4.08.0/bin/liquidsoap "

#uruchamia w foreground
def run():
    return subprocess.Popen([cmd_fg, cfg.cfg['home_path']+"radio.liq" ], bufsize=1, stdout=subprocess.PIPE, universal_newlines=True)

#śledzi nowe linie w procesie
def trace(proc):
    while proc.poll() is None:
        line = proc.stdout.readline()

        if "<mqtt>" in line:
            logging.info(line)

def kill(proc):
    logging.info("killing liquid")
    proc.kill()

def send(command):
    socket_path = '/var/run/emiter/socket'
    result = os.popen("( echo '"+command+"'; echo exit ) | socat "+socket_path+' -').read()
    return result

def multisend(commands):
    socket_path = cfg.cfg['home_path']+'socket'
    commandlist = ''
    for c in commands:
        send(c)
        time.sleep(1)

#pobiera pid
def get_pid():
    is_pid = os.path.isfile(cfg.cfg['home_path']+"radio.pid")
    p_id = ""
    if is_pid:
        with open(cfg.cfg['home_path']+"radio.pid") as f:
            p_id = f.read().rstrip()

            #sprawdź, czy proces istnieje
            pid_list = os.popen("pgrep liquidsoap").read().splitlines()

            if p_id not in pid_list:
                logging.info("znaleziono plik .pid, ale proces nie pracuje")
                is_pid = False
    
    return {'is':is_pid, 'pid':p_id}

#start prcoesu
def start():
    p_id = get_pid()

    if p_id['is']:
        logging.info("proces pracuje (PID "+p_id['pid']+"). Użyj emiter.py restart")
    else:
        logging.info("uruchamiam liquidsoap")
        #print(cmd + cfg.cfg['home_path'] + "radio.liq")
        os.popen(cmd + cfg.cfg['home_path'] + "radio.liq")

#zatrzymanie procesu
def stop():
    p_id = get_pid()

    if p_id['is']:
        logging.info("zamykam liquidsoap (PID "+p_id['pid']+")")
        os.popen("kill -TERM "+p_id['pid'])
    else:
        logging.info("Proces nie pracuje. użyj emiter.py start")

def status():
    #pobierz status z liquidsoapa
    input = send("status").split("END")[0]
    
    status = {"alive":True}
    try:
        status.update(json.loads(input))
    except JSONDecodeError:
        status = {"alive":False}    
    return status

if __name__ == "__main__":
    print(status())