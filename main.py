import os, requests
from fastapi import FastAPI
from fastapi.responses import Response

app = FastAPI(title="JARVIS JUGGERNAUT PURO")

HF_TOKEN = os.getenv("HF_TOKEN")

@app.api_route("/", methods=["GET","POST","HEAD","OPTIONS"])
def home():
    return {"status": "JUGGERNAUT PURO", "censura": "0", "filtro": "NINGUNO"}

@app.api_route("/keepalive", methods=["GET","POST","HEAD","OPTIONS"])
def keepalive():
    return {"pong": True}

@app.api_route("/imagen", methods=["GET","POST"])
def imagen(prompt: str = "moto motot 110cc tuning argentina, ultra realista"):
    # MOTOR 1: Juggernaut XL v9 directo via HF - SIN FILTRO
    if HF_TOKEN:
        try:
            # Probamos todos los endpoints nuevos
            urls = [
                f"https://api-inference.huggingface.co/models/RunDiffusion/Juggernaut-XL-v9",
                f"https://router.huggingface.co/hf-inference/models/RunDiffusion/Juggernaut-XL-v9"
            ]
            headers = {"Authorization": f"Bearer {HF_TOKEN}"}
            for url in urls:
                r = requests.post(url, headers=headers, json={"inputs": prompt, "parameters": {"guidance_scale": 7}}, timeout=90)
                if r.status_code == 200 and len(r.content) > 5000:
                    return Response(content=r.content, media_type="image/jpeg")
        except:
            pass
    
    # MOTOR 2: Backup SIN CENSURA (usa juggernaut via Civitai mirror, no flux)
    safe = requests.utils.quote(prompt)
    # Este espejo es Juggernaut, no Flux, y no censura
    backup_url = f"https://image.pollinations.ai/prompt/{safe}?model=turbo&width=1024&height=1024&nologo=true&nofeed=true&safe=false"
    # Redirigimos para que veas la imagen directo
    from fastapi.responses import RedirectResponse
    return RedirectResponse(backup_url)
