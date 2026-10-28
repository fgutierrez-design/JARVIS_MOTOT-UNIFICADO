import os, requests, time
from fastapi import FastAPI
from fastapi.responses import Response

app = FastAPI(title="JARVIS MOTOT JUGGERNAUT V4 Puro")

HF_TOKEN = os.getenv("HF_TOKEN")
MODEL = "RunDiffusion/Juggernaut-XL-v9"

@app.api_route("/", methods=["GET","POST","HEAD","OPTIONS"])
def home():
    return {"status": "JUGGERNAUT PURO ONLINE", "censura": "NINGUNA"}

@app.api_route("/keepalive", methods=["GET","POST","HEAD","OPTIONS"])
def keepalive():
    return {"ping": "pong", "motor": "juggernaut-xl-v9", "censura": "0%"}

@app.api_route("/imagen", methods=["GET","POST"])
def imagen(prompt: str = "moto motot 110cc tuning argentina, ultra realista, 8k, taller motot"):
    if not HF_TOKEN:
        return {"error": "Falta HF_TOKEN en Render"}
    
    # NUEVA API 2026 SIN CENSURA
    url = f"https://router.huggingface.co/hf-inference/models/{MODEL}"
    headers = {"Authorization": f"Bearer {HF_TOKEN}"}
    
    # Juggernaut tarda 20-40 seg en despertar la primera vez
    for intento in range(3):
        try:
            r = requests.post(url, headers=headers, json={"inputs": prompt}, timeout=120)
            if r.status_code == 200:
                return Response(content=r.content, media_type="image/jpeg")
            elif r.status_code == 503:
                # Modelo despertando
                time.sleep(15)
                continue
            else:
                return {"juggernaut_error": r.text[:500], "status": r.status_code}
        except Exception as e:
            time.sleep(10)
    
    return {"error": "Juggernaut despertando, proba de nuevo en 30 seg", "prompt": prompt}
