import os
import time
import json
import requests
from fastapi import FastAPI, Request
from fastapi.responses import Response, JSONResponse
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="JARVIS MOTOT UNIFICADO - FER",
    description="Motor 1 (Pensar) + Motor 2 (Juggernaut XL v9 7GB)",
    version="2.1"
)

# ================= CORS =================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)

# ================= CONFIG =================
COLAB_URL = "https://f4293cfa40b9f3e36d.gradio.live"  # ← actualizá cuando reinicies Colab
HF_TOKEN = os.getenv("HF_TOKEN")

# ================= MOTOR 1: KEEP ALIVE + STATUS =================
@app.api_route("/", methods=["GET", "POST", "HEAD", "OPTIONS"])
@app.api_route("/keepalive", methods=["GET", "POST", "HEAD", "OPTIONS"])
@app.api_route("/status", methods=["GET", "POST"])
async def keepalive():
    return {
        "jarvis": "MOTOT UNIFICADO",
        "motor_1": "UNIFICADO - Activo",
        "motor_2": "IMAGEN Juggernaut XL v9 7GB - Activo",
        "colab": COLAB_URL,
        "censura": 0,
        "status": "Live",
        "version": "2.1"
    }


# ================= MOTOR 1: CHAT / UNIFICADO =================
@app.api_route("/chat", methods=["GET", "POST"])
@app.api_route("/unificado", methods=["GET", "POST"])
async def chat_unificado(request: Request):
    try:
        if request.method == "POST":
            try:
                data = await request.json()
            except:
                data = {}
        else:
            data = {}

        prompt = (
            data.get("prompt")
            or data.get("q")
            or request.query_params.get("prompt")
            or request.query_params.get("q")
            or "Hola Jarvis"
        )
    except Exception:
        prompt = request.query_params.get("prompt") or request.query_params.get("q") or "Hola Jarvis"

    # ← Acá después vas a meter tu lógica real de pensamiento
    respuesta = (
        f"🏍️ JARVIS MOTOT UNIFICADO: Recibí tu consulta '{prompt}'. "
        f"Motor 1 funcionando. Motor 2 (Juggernaut XL v9) listo para generar imagen."
    )

    return JSONResponse({
        "respuesta": respuesta,
        "prompt": prompt,
        "motor": "unificado",
        "status": "ok"
    })


# ================= MOTOR 2: IMAGEN JUGGERNAUT XL v9 =================
@app.api_route("/imagen", methods=["GET", "POST"])
async def imagen(request: Request):
    start_time = time.time()

    try:
        # 1. Extraer prompt de forma robusta
        body = {}
        if request.method == "POST":
            try:
                body = await request.json()
            except:
                pass

        prompt = (
            body.get("prompt")
            or body.get("q")
            or request.query_params.get("prompt")
            or request.query_params.get("q")
            or "mujer mecanica argentina sentada correctamente en moto 110 tuning"
        )

        # 2. Prompt reforzado (anatomía + estilo MOTOT)
        prompt_final = (
            f"{prompt}, ultra realistic, 8k, highly detailed, motorcycle workshop, "
            f"anatomically correct, both hands on handlebars, feet on pegs, "
            f"wearing jeans and leather jacket, argentine mechanic, perfect anatomy, "
            f"sharp focus, cinematic lighting"
        )

        negative = "deformed, bad anatomy, extra limbs, missing arms, blurry, cartoon, latex, deformed hands, low quality"

        print(f"[IMAGEN] Prompt recibido: {prompt}")
        print(f"[IMAGEN] Prompt final: {prompt_final[:120]}...")

        # 3. Llamada correcta a Gradio 6.x (SSE)
        call_url = f"{COLAB_URL.rstrip('/')}/gradio_api/call/generar_motot"

        r = requests.post(
            call_url,
            json={"data": [prompt_final]},
            timeout=30
        )
        r.raise_for_status()
        event_id = r.json().get("event_id")

        if not event_id:
            raise Exception("No se recibió event_id del Colab")

        print(f"[IMAGEN] event_id: {event_id}")

        # 4. Esperar resultado (SSE)
        result_url = f"{COLAB_URL.rstrip('/')}/gradio_api/call/generar_motot/{event_id}"
        img_url = None

        with requests.get(result_url, stream=True, timeout=180) as resp:
            for line in resp.iter_lines(decode_unicode=True):
                if not line:
                    continue
                if line.startswith("data: ") and line.strip() != "data: null":
                    try:
                        data = json.loads(line[6:])
                        if isinstance(data, list) and len(data) > 0:
                            file_data = data[0]
                            if isinstance(file_data, dict) and "url" in file_data:
                                img_url = file_data["url"]
                                break
                    except Exception as e:
                        print(f"[IMAGEN] Error parseando línea SSE: {e}")
                        continue

        if not img_url:
            raise Exception("No se recibió URL de imagen del Colab (timeout o error interno)")

        print(f"[IMAGEN] Imagen lista: {img_url}")

        # 5. Descargar y devolver la imagen
        img_resp = requests.get(img_url, timeout=90)
        img_resp.raise_for_status()

        elapsed = round(time.time() - start_time, 1)
        print(f"[IMAGEN] Generación completada en {elapsed}s")

        return Response(
            content=img_resp.content,
            media_type="image/webp",
            headers={
                "X-Generation-Time": str(elapsed),
                "X-Motor": "Juggernaut-XL-v9",
                "X-Prompt": prompt[:80]
            }
        )

    except Exception as e:
        elapsed = round(time.time() - start_time, 1)
        error_msg = str(e)
        print(f"[IMAGEN ERROR] {error_msg} (después de {elapsed}s)")

        return JSONResponse(
            {
                "error": error_msg,
                "motor": "Juggernaut XL v9",
                "colab": COLAB_URL,
                "elapsed": elapsed,
                "status": "failed"
            },
            status_code=500
        )


# ================= Health check extra =================
@app.get("/health")
async def health():
    return {"status": "ok", "service": "JARVIS MOTOT UNIFICADO"}
