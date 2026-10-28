from fastapi import FastAPI

app = FastAPI()

@app.api_route("/", methods=["GET", "POST", "HEAD", "OPTIONS"])
def home():
    return {"status": "online"}

@app.api_route("/keepalive", methods=["GET", "POST", "HEAD", "OPTIONS"])
def keepalive():
    return {"ping": "pong"}
