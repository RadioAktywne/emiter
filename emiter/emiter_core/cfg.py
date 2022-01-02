import json

#just read config from JSON file and share as dict
with open('/etc/emiter.conf') as f:
    cfg = json.load(f)


