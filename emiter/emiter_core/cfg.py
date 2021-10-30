import json

with open('/etc/emiter.conf') as f:
    cfg = json.load(f)

#TODO
#umożliwić alternatywny config by móc odpalić np równolegle wersję testową i produkcję
#ewentualnie Docker i do boju
