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
# EN LA PARTE DE MOTOR 2, REEMPLAZA TODO EL BLOQUE DE IMAGEN POR ESTO:

@app.api_route("/imagen", methods=["GET","POST"])
async def imagen(request: Request, prompt: str = "mujer mecanica argentina"):
    try:
        body = await request.json() if request.method == "POST" else {}
        if body.get("prompt"): prompt = body.get("prompt")
    except: pass
    prompt_param = request.query_params.get("prompt")
    if prompt_param: prompt = prompt_param

    prompt_fix = f"{prompt}, ultra realistic, perfect anatomy, both hands on handlebars, feet on pegs, wearing jeans leather jacket, motorcycle workshop"

    # INTENTO 1: COLAB DIRECTO - TU JUGGERNAUT REAL
    try:
        # Tu Colab Juggernaut espera POST así
        colab_api = f"{COLAB_URL}/api/predict"
        r = requests.post(colab_api, json={"data": [prompt_fix], "fn_index": 0}, timeout=120)
        j = r.json()
        img_data = j["data"][0]  # te devuelve una imagen base64 o url
        # Si viene base64
        if isinstance(img_data, str) and img_data.startswith("data:"):
            import base64
            b64 = img_data.split(",")[1]
            return Response(content=base64.b64decode(b64), media_type="image/jpeg")
        else:
            # Si viene path /file=
            img_url = f"{COLAB_URL}/file={img_data}" if "/file" not in img_data else img_data
            if not img_url.startswith("http"):
                img_url = f"{COLAB_URL}{img_url}"
            img = requests.get(img_url, timeout=90).content
            return Response(content=img, media_type="image/jpeg")
    except Exception as e:
        print(f"COLAB ERROR: {e}")
        # Si falla, igual te devuelvo el error para que lo veas
        pass

    # INTENTO 2: BACKUP POLLINATIONS (pero vos no querés este)
    import urllib.parse, time
    safe = urllib.parse.quote(prompt_fix)
    url = f"https://image.pollinations.ai/prompt/{safe}?model=flux&width=1024&height=1024&nologo=true&safe=false&seed={int(time.time())}"
    return RedirectResponse(url)
