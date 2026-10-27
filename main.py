from fastapi import FastAPI
app = FastAPI()

@app.get("/")
def home():
    return {"JARVIS V4": "Online 24/7", "status": "Motor Unificado Limpio OK"}

@app.get("/health")
def health():
    return {"status": "ok"}
