import os, time, requests, urllib.parse
from fastapi import FastAPI, Request
from fastapi.responses import Response, RedirectResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="JARVIS MOTOT UNIFICADO - FER")

# CORS para que tu APP del celu pueda llamar
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# CONFIG - Tu Colab de ahora
COLAB_URL = "https://f4293cfa40b9f3e36d.gradio.live"
HF_TOKEN = os.getenv("HF_TOKEN")

# ================= MOTOR 1: JARVIS UNIFICADO =================
@app.api_route("/", methods=["GET","POST","HEAD","OPTIONS"])
@app.api_route("/keepalive", methods=["GET","POST","HEAD","OPTIONS"])
def keepalive():
    return {
        "jarvis": "MOTOT UNIFICADO",
        "motor_1": "UNIFICADO - Activo",
        "motor_2": "IMAGEN Juggernaut XL v9 7GB - Activo",
        "colab": COLAB_URL,
        "censura": 0,
        "status": "Live"
    }

@app.api_route("/chat", methods=["GET","POST"])
@app.api_route("/unificado", methods=["GET","POST"])
async def chat_unificado(request: Request):
    try:
        data = await request.json() if request.method == "POST" else {}
        prompt = data.get("prompt") or request.query_params.get("prompt") or request.query_params.get("q") or "Hola Jarvis"
    except:
        prompt = request.query_params.get("prompt") or request.query_params.get("q") or "Hola Jarvis"
    
    # Acá va tu lógica de Jarvis Motot
    respuesta = f"🏍️ JARVIS MOTOT UNIFICADO: Recibí tu consulta '{prompt}'. Motor 1 funcionando, Motor 2 Juggernaut listo para imagen."
    return JSONResponse({"respuesta": respuesta, "prompt": prompt, "motor": "unificado"})

# ================= MOTOR 2: IMAGEN JUGGERNAUT =================
@app.api_route("/imagen", methods=["GET","POST"])
async def imagen(request: Request, prompt: str = "mujer mecanica argentina sentada correctamente en moto 110 tuning"):
    # Si viene por POST json
    try:
        if request.method == "POST":
            body = await request.json()
            if body.get("prompt"):
                prompt = body.get("prompt")
    except:
        pass
    
    # Prompt arreglado para no deformar
    prompt_fix = f"{prompt}, ultra realistic, anatomically correct, both hands on handlebars, feet on ground, wearing jeans and leather jacket, perfect anatomy, workshop, 8k"

    # INTENTO 1: COLAB TU JUGGERNAUT XL v9 7GB REAL
    try:
        from gradio_client import Client
        client = Client(COLAB_URL)
        result = client.predict(prompt_fix, api_name="/predict")
        # result puede ser url o path
        img_path = result[0] if isinstance(result, (list, tuple)) else result
        if img_path.startswith("http"):
            r = requests.get(img_path, timeout=90)
        else:
            # Si es archivo local de gradio, pedirlo al servidor
            r = requests.get(f"{COLAB_URL}/file={img_path}", timeout=90)
        if r.status_code == 200 and len(r.content) > 5000:
            return Response(content=r.content, media_type="image/jpeg")
    except Exception as e:
        print(f"[MOTOR 2] Colab falló: {e}")

    # INTENTO 2: HUGGING FACE con tu token (si lo tenes)
    if HF_TOKEN:
        try:
            url = "https://api-inference.huggingface.co/models/RunDiffusion/Juggernaut-XL-v9"
            r = requests.post(url, headers={"Authorization": f"Bearer {HF_TOKEN}"}, json={"inputs": prompt_fix}, timeout=90)
            if r.status_code == 200 and len(r.content) > 5000:
                return Response(content=r.content, media_type="image/jpeg")
        except Exception as e:
            print(f"[MOTOR 2] HF falló: {e}")

    # INTENTO 3: BACKUP Pollinations sin censura y sin limite (con seed)
    safe = urllib.parse.quote(prompt_fix)
    seed = int(time.time())
    backup_url = f"https://image.pollinations.ai/prompt/{safe}?model=flux&width=1024&height=1024&nologo=true&nofeed=true&safe=false&enhance=true&seed={seed}"
    return RedirectResponse(backup_url)
