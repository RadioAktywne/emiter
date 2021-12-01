from emiter_core import liquidsoap
from fastapi import FastAPI

app = FastAPI()

#As-simple-as-possible API status client

@app.get("/status")
def status():
    return liquidsoap.status()
