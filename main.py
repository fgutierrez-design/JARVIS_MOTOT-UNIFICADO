from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def home():
    return {"status": "online"}

@app.get("/keepalive")
def keepalive():
    return {"ping": "pong"}
