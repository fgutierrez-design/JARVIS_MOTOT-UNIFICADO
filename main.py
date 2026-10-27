from fastapi import FastAPI
import datetime

app = FastAPI()

@app.get("/")
def home():
    return {"JARVIS V4":"Online 24/7","status":"Motor Unificado Limpio OK","timestamp":str(datetime.datetime.now())}

@app.get("/keepalive")
def keepalive():
    return {"ping":"pong","status":"JARVIS despierto 24/7"}

@app.get("/health")
def health():
    return {"status":"ok"}
