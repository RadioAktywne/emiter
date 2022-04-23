import json
from emiter_core import cfg
from fastapi import FastAPI

app = FastAPI()

#As-simple-as-possible API status client

@app.get("/status")
def status():
    status_path = cfg.cfg["path_playlists"]+"status.json"

    with open(status_path,mode='r',encoding='utf8') as f:
        return json.loads(f.read())
