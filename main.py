from fastapi import FastAPI
import datetime

app = FastAPI()

@app.get("/")
def home():
    return {"JARVIS V4": "Online 24/7", "status": "OK"}

@app.get("/keepalive")
def keepalive():
    return {"ping": "pong", "status": "despierto"}

@app.get("/health")
def health():
    return {"status": "ok"}
