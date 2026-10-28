import os, requests
from fastapi import FastAPI
from fastapi.responses import Response, RedirectResponse

app = FastAPI(title="JARVIS MOTOT V4.1")

HF_TOKEN = os.getenv("HF_TOKEN")
MODEL = "RunDiffusion/Juggernaut-XL-v9"

@app.api_route("/", methods=["GET","POST","HEAD","OPTIONS"])
def home():
    return {"status":"JARVIS V4.1 ONLINE","motor":MODEL,"keepalive":"100%"}

@app.api_route("/keepalive", methods=["GET","POST","HEAD","OPTIONS"])
def keepalive():
    return {"ping":"pong","status":"Arriba 100%"}

@app.api_route("/imagen", methods=["GET","POST"])
def imagen(prompt: str = "moto motot tuning ultra realista 8k"):
    # 1. Intentamos Juggernaut con la NUEVA API
    if HF_TOKEN:
        try:
            url_hf = f"https://router.huggingface.co/hf-inference/models/{MODEL}"
            headers = {"Authorization": f"Bearer {HF_TOKEN}"}
            r = requests.post(url_hf, headers=headers, json={"inputs": prompt}, timeout=120)
            if r.status_code == 200 and b"image" in r.headers.get("content-type","") or len(r.content) > 10000:
                return Response(content=r.content, media_type="image/jpeg")
        except Exception as e:
            print(f"HF fail: {e}")

    # 2. Backup 100% funcional - FLUX (calidad pro)
    safe_prompt = requests.utils.quote(prompt)
    final_url = f"https://image.pollinations.ai/prompt/{safe_prompt}?model=flux&width=1024&height=1024&enhance=true&nologo=true"
    return RedirectResponse(url=final_url)

@app.api_route("/jarvis", methods=["GET","POST"])
def jarvis_endpoint(texto: str = "moto motot", modo: str = "imagen"):
    return imagen(texto)
