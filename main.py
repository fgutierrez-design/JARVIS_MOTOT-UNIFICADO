import os
import requests
from fastapi import FastAPI
from fastapi.responses import Response

app = FastAPI(title="JARVIS MOTOT UNIFICADO V4")

HF_TOKEN = os.getenv("HF_TOKEN")
MODEL = "RunDiffusion/Juggernaut-XL-v9"

@app.api_route("/", methods=["GET", "POST", "HEAD", "OPTIONS"])
def home():
    return {"status": "JARVIS V4 ONLINE", "motor_imagen": MODEL, "keepalive": "100%"}

@app.api_route("/keepalive", methods=["GET", "POST", "HEAD", "OPTIONS"])
def keepalive():
    return {"ping": "pong", "status": "Arriba"}

@app.api_route("/imagen", methods=["GET", "POST"])
def imagen(prompt: str = "moto deportiva motot racing, ultra realista, 8k"):
    # Si Hugging Face tarda, usa backup instantáneo
    if not HF_TOKEN:
        url = f"https://image.pollinations.ai/prompt/{prompt.replace(' ','%20')}?model=flux&width=1024&height=1024&nologo=true"
        return {"motor": "flux_backup", "url": url, "prompt": prompt}

    headers = {"Authorization": f"Bearer {HF_TOKEN}"}
    api_url = f"https://api-inference.huggingface.co/models/{MODEL}"
    
    try:
        r = requests.post(api_url, headers=headers, json={"inputs": prompt}, timeout=90)
        if r.status_code == 200:
            return Response(content=r.content, media_type="image/jpeg")
        else:
            # Fallback si Juggernaut está cargando
            url = f"https://image.pollinations.ai/prompt/{prompt.replace(' ','%20')}?model=flux&width=1024&height=1024"
            return {"motor": "flux_backup_por_carga", "url": url, "hf_error": r.text[:200]}
    except Exception as e:
        url = f"https://image.pollinations.ai/prompt/{prompt.replace(' ','%20')}?model=flux"
        return {"motor": "backup", "url": url, "error": str(e)}

@app.api_route("/jarvis", methods=["GET", "POST"])
def jarvis(texto: str = "moto motot", modo: str = "imagen"):
    if modo == "imagen":
        return imagen(texto)
    return {"respuesta": f"JARVIS V4: {texto}"}
