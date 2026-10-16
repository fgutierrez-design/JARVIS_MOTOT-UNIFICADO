# -*- coding: utf-8 -*-
"""API Motor Unificado JARVIS — Groq + Enjambre. Sin Ollama."""
from __future__ import annotations
import json, os, time
from flask import Flask, request, jsonify, Response, stream_with_context
from flask_cors import CORS
import motor_core
import herramientas
import enjambre_unificado as enjambre
import bucle_evolutivo

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})
PUERTO = int(os.environ.get("JARVIS_MOTOR_PORT", "11435"))
CLAVE = os.environ.get("JARVIS_MOTOR_CLAVE", "").strip()


def _ok_auth():
    if not CLAVE:
        return True
    a = request.headers.get("Authorization") or ""
    if a.startswith("Bearer "):
        return a[7:].strip() == CLAVE
    return (request.headers.get("X-API-Key") or "") == CLAVE


@app.route("/health")
@app.route("/api/estado")
def health():
    return jsonify({"ok": True, **motor_core.estado()})


@app.route("/v1/models", methods=["GET"])
def models():
    cfg = motor_core.cargar_config()
    return jsonify({"object": "list", "data": [{"id": cfg["modelo"], "object": "model", "owned_by": "jarvis-unificado"}]})


@app.route("/v1/chat/completions", methods=["POST"])
def chat_completions():
    if not _ok_auth():
        return jsonify({"error": "No autorizado"}), 401
    data = request.get_json(force=True, silent=True) or {}
    messages = data.get("messages") or []
    cfg = motor_core.cargar_config()
    historial, ultimo = [], ""
    for m in messages:
        role, content = m.get("role"), m.get("content") or ""
        if role == "system":
            continue
        if role == "user":
            ultimo = content if isinstance(content, str) else str(content)
            historial.append({"role": "user", "content": ultimo})
        elif role == "assistant":
            historial.append({"role": "assistant", "content": content if isinstance(content, str) else str(content)})
    if historial and historial[-1]["role"] == "user":
        historial = historial[:-1]
    usar = data.get("usar_herramientas")
    if usar is None:
        usar = True
    resultado = motor_core.pensar(ultimo, historial, cfg, usar_herramientas=usar)
    texto = resultado.get("respuesta") or ""
    if data.get("stream"):
        def gen():
            payload = {"id": "chatcmpl-jarvis", "object": "chat.completion.chunk", "created": int(time.time()),
                       "model": cfg["modelo"], "choices": [{"index": 0, "delta": {"role": "assistant", "content": texto}, "finish_reason": None}]}
            yield f"data: {json.dumps(payload, ensure_ascii=False)}\n\n"
            fin = {"id": "chatcmpl-jarvis", "object": "chat.completion.chunk", "created": int(time.time()),
                   "model": cfg["modelo"], "choices": [{"index": 0, "delta": {}, "finish_reason": "stop"}]}
            yield f"data: {json.dumps(fin, ensure_ascii=False)}\n\n"
            yield "data: [DONE]\n\n"
        return Response(stream_with_context(gen()), mimetype="text/event-stream")
    return jsonify({
        "id": "chatcmpl-jarvis", "object": "chat.completion", "created": int(time.time()), "model": cfg["modelo"],
        "choices": [{"index": 0, "message": {"role": "assistant", "content": texto}, "finish_reason": "stop"}],
        "usage": {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0},
        "jarvis": {"backend": "unificado", "herramientas": resultado.get("herramientas_usadas"), "pasos": resultado.get("pasos_totales")},
    })


@app.route("/api/pensar", methods=["POST"])
def api_pensar():
    if not _ok_auth():
        return jsonify({"error": "No autorizado"}), 401
    data = request.get_json(force=True, silent=True) or {}
    texto = data.get("texto") or data.get("mensaje") or ""
    if not str(texto).strip():
        return jsonify({"error": "Falta texto"}), 400
    return jsonify(motor_core.pensar(texto, data.get("historial", []), usar_herramientas=data.get("usar_herramientas", True)))


@app.route("/api/enjambre/ciclo", methods=["POST"])
def api_enjambre():
    if not _ok_auth():
        return jsonify({"error": "No autorizado"}), 401
    return jsonify(enjambre.ciclo_enjambre())


@app.route("/api/enjambre/estado", methods=["GET"])
def api_enjambre_estado():
    return jsonify(enjambre.estado())


@app.route("/api/evolucionar", methods=["POST"])
def api_evolucionar():
    if not _ok_auth():
        return jsonify({"error": "No autorizado"}), 401
    return jsonify(motor_core.forzar_evolucion())


@app.route("/api/aprender", methods=["POST"])
def api_aprender():
    if not _ok_auth():
        return jsonify({"error": "No autorizado"}), 401
    data = request.get_json(force=True, silent=True) or {}
    k = data.get("conocimiento") or data.get("texto") or ""
    if not k:
        return jsonify({"error": "Falta conocimiento"}), 400
    return jsonify({"ok": True, "resultado": herramientas.aprender(data.get("tema") or "general", k, data.get("fuente", "api"))})


if __name__ == "__main__":
    e = motor_core.estado()
    print("=" * 60)
    print("  JARVIS MOTOR UNIFICADO U1.0")
    print("  Groq + Tools + Enjambre | SIN Ollama | SIN censura")
    print("=" * 60)
    print(f"  Puerto: {PUERTO}")
    print(f"  Modelo: {e.get('modelo')}")
    print(f"  GROQ:   {'OK' if e.get('motor_respondiendo') else e.get('error')}")
    print(f"  Enjambre ciclos: {(e.get('enjambre') or {}).get('ciclos')}")
    try:
        print(" ", bucle_evolutivo.iniciar())
        print(" ", enjambre.activar())
    except Exception as ex:
        print("  arranque parcial:", ex)
    print("=" * 60)
    app.run(host="0.0.0.0", port=PUERTO, threaded=True)
