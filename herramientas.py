# -*- coding: utf-8 -*-
"""Herramientas del motor JARVIS: web, archivos, codigo, memoria, aprendizaje."""
from __future__ import annotations

import ast
import json
import math
import operator
import os
import re
import traceback
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Dict, List

import requests

_DIR = Path(__file__).resolve().parent
_MEM = _DIR / "memoria"
_CONOC = _DIR / "conocimiento"
_LOGS = _DIR / "logs"
for d in (_MEM, _CONOC, _LOGS):
    d.mkdir(parents=True, exist_ok=True)

MEMORIA_JSON = _MEM / "memoria_permanente.json"
APRENDIZAJE_JSON = _CONOC / "aprendizaje_continuo.json"
BITACORA = _LOGS / "herramientas.log"


def _log(msg: str) -> None:
    try:
        with open(BITACORA, "a", encoding="utf-8") as f:
            f.write(f"[{datetime.now().isoformat(timespec='seconds')}] {msg}\n")
    except Exception:
        pass


def _load_json(path: Path, default):
    try:
        if path.exists():
            return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        pass
    return default


def _save_json(path: Path, data) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


# ------------------------------------------------------------------
# Implementaciones
# ------------------------------------------------------------------
def buscar_web(consulta: str, max_resultados: int = 5) -> str:
    """Busca en internet (DuckDuckGo HTML / instant)."""
    consulta = (consulta or "").strip()
    if not consulta:
        return "Falta la consulta."
    out = []
    try:
        r = requests.get(
            "https://api.duckduckgo.com/",
            params={"q": consulta, "format": "json", "no_redirect": 1, "no_html": 1},
            timeout=12,
            headers={"User-Agent": "JARVIS-Motor/1.0"},
        )
        d = r.json()
        if d.get("AbstractText"):
            out.append(d["AbstractText"])
        for t in (d.get("RelatedTopics") or [])[:max_resultados]:
            if isinstance(t, dict) and t.get("Text"):
                out.append(t["Text"])
            elif isinstance(t, dict) and "Topics" in t:
                for sub in t["Topics"][:2]:
                    if sub.get("Text"):
                        out.append(sub["Text"])
    except Exception as e:
        out.append(f"(DDG instant fallo: {e})")
    # fallback HTML lite
    if len(out) < 2:
        try:
            r = requests.get(
                "https://html.duckduckgo.com/html/",
                params={"q": consulta},
                timeout=15,
                headers={"User-Agent": "Mozilla/5.0 JARVIS-Motor"},
            )
            textos = re.findall(r'class="result__snippet"[^>]*>(.*?)</', r.text, re.S)
            for t in textos[:max_resultados]:
                limpio = re.sub(r"<[^>]+>", "", t).strip()
                if limpio:
                    out.append(limpio)
        except Exception as e:
            out.append(f"(busqueda HTML fallo: {e})")
    _log(f"buscar_web: {consulta[:80]}")
    return "\n".join(out[:max_resultados]) if out else "Sin resultados."


def leer_url(url: str, max_chars: int = 12000) -> str:
    url = (url or "").strip()
    if not url.startswith("http"):
        return "URL invalida (debe empezar con http)."
    try:
        r = requests.get(url, timeout=20, headers={"User-Agent": "Mozilla/5.0 JARVIS-Motor"})
        r.raise_for_status()
        texto = re.sub(r"(?is)<script[^>]*>.*?</script>", " ", r.text)
        texto = re.sub(r"(?is)<style[^>]*>.*?</style>", " ", texto)
        texto = re.sub(r"<[^>]+>", " ", texto)
        texto = re.sub(r"\s+", " ", texto).strip()
        _log(f"leer_url: {url}")
        return texto[:max_chars]
    except Exception as e:
        return f"Error leyendo URL: {e}"


def leer_archivo(ruta: str, max_chars: int = 50000) -> str:
    p = Path(ruta).expanduser()
    if not p.exists():
        return f"No existe: {p}"
    try:
        data = p.read_text(encoding="utf-8", errors="ignore")
        return data[:max_chars]
    except Exception as e:
        return f"Error: {e}"


def escribir_archivo(ruta: str, contenido: str) -> str:
    p = Path(ruta).expanduser()
    try:
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(contenido or "", encoding="utf-8")
        _log(f"escribir_archivo: {p}")
        return f"OK escrito: {p} ({len(contenido or '')} chars)"
    except Exception as e:
        return f"Error escribiendo: {e}"


def listar_archivos(ruta: str = ".", max_items: int = 200) -> str:
    p = Path(ruta).expanduser()
    if not p.exists():
        return f"No existe: {p}"
    items = []
    try:
        for i, x in enumerate(sorted(p.iterdir())):
            if i >= max_items:
                items.append("...")
                break
            items.append(f"{'[D]' if x.is_dir() else '[F]'} {x.name}")
        return "\n".join(items) or "(vacio)"
    except Exception as e:
        return f"Error: {e}"


def ejecutar_python(codigo: str) -> str:
    """Ejecuta Python en sandbox local (sin red interna forzada)."""
    codigo = codigo or ""
    # Bloqueo minimo solo de os.system peligroso extremo opcional — usuario pidio sin limites
    # Permitimos casi todo; capturamos salida
    import io
    import contextlib
    buf = io.StringIO()
    env = {"__builtins__": __builtins__}
    try:
        with contextlib.redirect_stdout(buf), contextlib.redirect_stderr(buf):
            exec(compile(codigo, "<jarvis>", "exec"), env, env)
        out = buf.getvalue()
        return out if out.strip() else "(sin salida, OK)"
    except Exception:
        return "Error:\n" + traceback.format_exc()


def calcular(expresion: str) -> str:
    expresion = (expresion or "").strip()
    ops = {
        ast.Add: operator.add, ast.Sub: operator.sub, ast.Mult: operator.mul,
        ast.Div: operator.truediv, ast.Pow: operator.pow, ast.USub: operator.neg,
        ast.Mod: operator.mod,
    }
    def _eval(node):
        if isinstance(node, ast.Expression):
            return _eval(node.body)
        if isinstance(node, ast.Constant):
            return node.value
        if isinstance(node, ast.Num):
            return node.n
        if isinstance(node, ast.BinOp):
            return ops[type(node.op)](_eval(node.left), _eval(node.right))
        if isinstance(node, ast.UnaryOp):
            return ops[type(node.op)](_eval(node.operand))
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
            if node.func.id in ("sqrt", "sin", "cos", "log", "abs", "round"):
                fn = getattr(math, node.func.id, None) or __builtins__[node.func.id]
                return fn(*[_eval(a) for a in node.args])
        raise ValueError("expresion no permitida")
    try:
        return str(_eval(ast.parse(expresion, mode="eval")))
    except Exception as e:
        return f"Error calculo: {e}"


def recordar(clave: str, valor: str) -> str:
    data = _load_json(MEMORIA_JSON, {})
    data[clave] = {"valor": valor, "fecha": datetime.now().isoformat(timespec="seconds")}
    _save_json(MEMORIA_JSON, data)
    _log(f"recordar: {clave}")
    return f"Recordado: {clave}"


def recuperar(clave: str = "") -> str:
    data = _load_json(MEMORIA_JSON, {})
    if not clave:
        if not data:
            return "(memoria vacia)"
        return "\n".join(f"- {k}: {v.get('valor') if isinstance(v, dict) else v}" for k, v in list(data.items())[-30:])
    v = data.get(clave)
    if v is None:
        return f"No hay memoria para '{clave}'"
    return v.get("valor") if isinstance(v, dict) else str(v)


def aprender(tema: str, conocimiento: str, fuente: str = "usuario") -> str:
    """Aprendizaje continuo: acumula conocimiento por tema."""
    data = _load_json(APRENDIZAJE_JSON, {"version": "1.0", "items": []})
    data.setdefault("items", []).append({
        "tema": tema,
        "conocimiento": conocimiento,
        "fuente": fuente,
        "fecha": datetime.now().isoformat(timespec="seconds"),
    })
    # cap suave 2000 entradas (rotacion, no borrado agresivo)
    if len(data["items"]) > 2000:
        data["items"] = data["items"][-2000:]
    data["actualizado"] = datetime.now().isoformat(timespec="seconds")
    _save_json(APRENDIZAJE_JSON, data)
    _log(f"aprender: {tema}")
    return f"Aprendido sobre '{tema}' (total {len(data['items'])} entradas)."


def consultar_aprendizaje(tema: str = "", limit: int = 10) -> str:
    data = _load_json(APRENDIZAJE_JSON, {"items": []})
    items = data.get("items") or []
    if tema:
        q = tema.lower()
        items = [i for i in items if q in str(i.get("tema", "")).lower() or q in str(i.get("conocimiento", "")).lower()]
    items = items[-limit:]
    if not items:
        return "Sin conocimiento guardado para esa consulta."
    return "\n".join(f"- [{i.get('tema')}] {i.get('conocimiento')}" for i in items)


def hora_actual() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


# ------------------------------------------------------------------
# Registro para el modelo (OpenAI tools style / Ollama)
# ------------------------------------------------------------------
REGISTRY: Dict[str, Callable[..., str]] = {
    "buscar_web": lambda consulta, max_resultados=5: buscar_web(consulta, int(max_resultados)),
    "leer_url": lambda url, max_chars=12000: leer_url(url, int(max_chars)),
    "leer_archivo": lambda ruta, max_chars=50000: leer_archivo(ruta, int(max_chars)),
    "escribir_archivo": lambda ruta, contenido: escribir_archivo(ruta, contenido),
    "listar_archivos": lambda ruta=".", max_items=200: listar_archivos(ruta, int(max_items)),
    "ejecutar_python": lambda codigo: ejecutar_python(codigo),
    "calcular": lambda expresion: calcular(expresion),
    "recordar": lambda clave, valor: recordar(clave, valor),
    "recuperar": lambda clave="": recuperar(clave),
    "aprender": lambda tema, conocimiento, fuente="usuario": aprender(tema, conocimiento, fuente),
    "consultar_aprendizaje": lambda tema="", limit=10: consultar_aprendizaje(tema, int(limit)),
    "hora_actual": lambda: hora_actual(),
}


def definiciones_para_modelo() -> List[dict]:
    return [
        {"type": "function", "function": {"name": "buscar_web", "description": "Busca informacion actual en internet",
            "parameters": {"type": "object", "properties": {"consulta": {"type": "string"}, "max_resultados": {"type": "integer"}}, "required": ["consulta"]}}},
        {"type": "function", "function": {"name": "leer_url", "description": "Lee el texto de una URL",
            "parameters": {"type": "object", "properties": {"url": {"type": "string"}, "max_chars": {"type": "integer"}}, "required": ["url"]}}},
        {"type": "function", "function": {"name": "leer_archivo", "description": "Lee un archivo local",
            "parameters": {"type": "object", "properties": {"ruta": {"type": "string"}, "max_chars": {"type": "integer"}}, "required": ["ruta"]}}},
        {"type": "function", "function": {"name": "escribir_archivo", "description": "Escribe/crea un archivo local",
            "parameters": {"type": "object", "properties": {"ruta": {"type": "string"}, "contenido": {"type": "string"}}, "required": ["ruta", "contenido"]}}},
        {"type": "function", "function": {"name": "listar_archivos", "description": "Lista archivos de una carpeta",
            "parameters": {"type": "object", "properties": {"ruta": {"type": "string"}, "max_items": {"type": "integer"}}, "required": []}}},
        {"type": "function", "function": {"name": "ejecutar_python", "description": "Ejecuta codigo Python y devuelve la salida",
            "parameters": {"type": "object", "properties": {"codigo": {"type": "string"}}, "required": ["codigo"]}}},
        {"type": "function", "function": {"name": "calcular", "description": "Evalua una expresion matematica",
            "parameters": {"type": "object", "properties": {"expresion": {"type": "string"}}, "required": ["expresion"]}}},
        {"type": "function", "function": {"name": "recordar", "description": "Guarda un dato permanente en memoria",
            "parameters": {"type": "object", "properties": {"clave": {"type": "string"}, "valor": {"type": "string"}}, "required": ["clave", "valor"]}}},
        {"type": "function", "function": {"name": "recuperar", "description": "Recupera memoria por clave o lista reciente",
            "parameters": {"type": "object", "properties": {"clave": {"type": "string"}}, "required": []}}},
        {"type": "function", "function": {"name": "aprender", "description": "Guarda conocimiento nuevo para aprendizaje continuo",
            "parameters": {"type": "object", "properties": {
                "tema": {"type": "string"}, "conocimiento": {"type": "string"}, "fuente": {"type": "string"}
            }, "required": ["tema", "conocimiento"]}}},
        {"type": "function", "function": {"name": "consultar_aprendizaje", "description": "Consulta lo aprendido sobre un tema",
            "parameters": {"type": "object", "properties": {"tema": {"type": "string"}, "limit": {"type": "integer"}}, "required": []}}},
        {"type": "function", "function": {"name": "hora_actual", "description": "Fecha y hora actual del sistema",
            "parameters": {"type": "object", "properties": {}, "required": []}}},
    ]


def ejecutar(nombre: str, argumentos: dict) -> str:
    fn = REGISTRY.get(nombre)
    if not fn:
        return f"Herramienta desconocida: {nombre}"
    try:
        args = argumentos or {}
        return str(fn(**args))
    except TypeError as e:
        return f"Argumentos invalidos para {nombre}: {e}"
    except Exception as e:
        return f"Error en {nombre}: {e}\n{traceback.format_exc()}"
