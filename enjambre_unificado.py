# -*- coding: utf-8 -*-
"""Enjambre unificado: 5 nanobots + evolucion de parametros.
No requiere EvoX/JAX instalado; si estan, se usan para PSO-lite extra.
"""
from __future__ import annotations

import json
import random
import threading
import traceback
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

ROOT = Path(__file__).resolve().parent
DATOS = ROOT / "datos"
LOGS = ROOT / "logs"
EVOL = ROOT / "evolucion"
BACKUP = ROOT / "backup_auto"
for d in (DATOS, LOGS, EVOL, BACKUP):
    d.mkdir(parents=True, exist_ok=True)

PARAMS = EVOL / "parametros_evolucion.json"
MONITORS = DATOS / "monitors.json"
LOG_FILE = LOGS / "enjambre.log"

_lock = threading.RLock()
_estado = {"activo": False, "ciclos": 0, "ultimo": None, "nanobots": {}}

DEFAULT_PARAMS = {
    "version": "U1.0",
    "temperature": 0.7,
    "max_pasos": 24,
    "risk_factor": 0.7,
    "fitness_objetivo": 0.85,
    "mutacion": 0.03,
    "historial": [],
}


def _log(msg: str) -> None:
    line = f"[{datetime.now().isoformat(timespec='seconds')}] {msg}\n"
    with _lock:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(line)


def _load_params() -> dict:
    try:
        if PARAMS.exists():
            p = json.loads(PARAMS.read_text(encoding="utf-8"))
            out = dict(DEFAULT_PARAMS)
            out.update(p)
            return out
    except Exception:
        pass
    return dict(DEFAULT_PARAMS)


def _save_params(p: dict) -> None:
    p = dict(p)
    p["actualizado"] = datetime.now().isoformat(timespec="seconds")
    PARAMS.write_text(json.dumps(p, ensure_ascii=False, indent=2), encoding="utf-8")


def nanobot_vigilante() -> dict:
    info = {"nombre": "Vigilante", "ok": True, "alertas": []}
    try:
        if not (ROOT / "motor_core.py").exists():
            info["alertas"].append("falta motor_core.py")
            info["ok"] = False
        try:
            import psutil
            info["ram_pct"] = psutil.virtual_memory().percent
            info["cpu_pct"] = psutil.cpu_percent(interval=0.15)
            if info["ram_pct"] >= 92:
                info["alertas"].append(f"RAM alta {info['ram_pct']:.0f}%")
        except Exception:
            pass
        MONITORS.write_text(json.dumps({
            "ts": datetime.now().isoformat(timespec="seconds"),
            "alertas": info["alertas"],
            "ram_pct": info.get("ram_pct"),
            "cpu_pct": info.get("cpu_pct"),
        }, ensure_ascii=False, indent=2), encoding="utf-8")
    except Exception as e:
        info["ok"] = False
        info["alertas"].append(str(e))
    _log(f"Vigilante ok={info['ok']}")
    return info


def nanobot_reparador() -> dict:
    """Valida sintaxis de modulos criticos y respalda."""
    info = {"nombre": "Reparador", "ok": True, "acciones": []}
    import ast, shutil
    criticos = ["motor_core.py", "herramientas.py", "enjambre_unificado.py", "servidor_motor.py"]
    for name in criticos:
        path = ROOT / name
        if not path.exists():
            continue
        try:
            ast.parse(path.read_text(encoding="utf-8", errors="ignore"))
            # backup periodico
            if _estado["ciclos"] % 5 == 0:
                dest = BACKUP / f"{path.stem}_{datetime.now().strftime('%Y%m%d_%H%M%S')}{path.suffix}"
                shutil.copy2(path, dest)
                info["acciones"].append({"backup": dest.name})
        except SyntaxError as e:
            info["ok"] = False
            info["acciones"].append({"error_sintaxis": name, "detalle": str(e)})
            # intentar restaurar ultimo backup
            cands = sorted(BACKUP.glob(f"{path.stem}_*{path.suffix}"), key=lambda p: p.stat().st_mtime, reverse=True)
            if cands:
                try:
                    ast.parse(cands[0].read_text(encoding="utf-8", errors="ignore"))
                    shutil.copy2(cands[0], path)
                    info["acciones"].append({"restaurado": cands[0].name})
                    info["ok"] = True
                except Exception as e2:
                    info["acciones"].append({"restore_fail": str(e2)})
    _log(f"Reparador ok={info['ok']}")
    return info


def nanobot_analizador() -> dict:
    info = {"nombre": "Analizador", "ok": True, "fitness": 1.0}
    try:
        # fitness segun aprendizaje + errores recientes
        apr = ROOT / "conocimiento" / "aprendizaje_continuo.json"
        n = 0
        if apr.exists():
            data = json.loads(apr.read_text(encoding="utf-8"))
            n = len(data.get("items") or [])
        fitness = min(1.0, 0.5 + min(n, 100) / 200)
        # penalizar si monitors tiene alertas
        if MONITORS.exists():
            mon = json.loads(MONITORS.read_text(encoding="utf-8"))
            fitness -= 0.1 * len(mon.get("alertas") or [])
        info["fitness"] = round(max(0.0, fitness), 3)
        info["items_aprendidos"] = n
    except Exception as e:
        info["ok"] = False
        info["error"] = str(e)
    _log(f"Analizador fitness={info.get('fitness')}")
    return info


def nanobot_evolucionador(fitness: float = 1.0) -> dict:
    """Mutacion suave de parametros (PSO-lite). Opcional EvoX si esta instalado."""
    info = {"nombre": "Evolucionador", "ok": True}
    p = _load_params()
    mut = float(p.get("mutacion", 0.03))
    if fitness < 0.6:
        p["temperature"] = max(0.25, float(p.get("temperature", 0.7)) - 0.05)
        p["max_pasos"] = min(30, int(p.get("max_pasos", 24)) + 2)
        info["ajuste"] = "conservador_refuerzo"
    elif fitness > 0.9:
        p["temperature"] = min(0.9, float(p.get("temperature", 0.7)) + mut)
        info["ajuste"] = "exploratorio"
    else:
        p["temperature"] = round(float(p.get("temperature", 0.7)) + random.uniform(-mut, mut), 3)
        p["temperature"] = max(0.2, min(0.95, p["temperature"]))
        info["ajuste"] = "estable"

    # Bonus EvoX si existe
    try:
        import evox  # noqa: F401
        info["evox"] = True
        # micro-perturbacion extra
        p["mutacion"] = round(min(0.1, mut * (1.0 + random.uniform(-0.1, 0.1))), 4)
    except Exception:
        info["evox"] = False

    hist = p.setdefault("historial", [])
    hist.append({
        "ts": datetime.now().isoformat(timespec="seconds"),
        "fitness": fitness,
        "temperature": p["temperature"],
        "max_pasos": p.get("max_pasos"),
        "ajuste": info["ajuste"],
    })
    p["historial"] = hist[-80:]
    _save_params(p)
    info["params"] = {"temperature": p["temperature"], "max_pasos": p.get("max_pasos"), "mutacion": p.get("mutacion")}
    _log(f"Evolucionador {info['ajuste']} {info['params']}")
    return info


def nanobot_guardian(reportes: List[dict]) -> dict:
    info = {"nombre": "Guardian", "ok": True}
    path = LOGS / f"guardian_{datetime.now().strftime('%Y%m%d')}.jsonl"
    resumen = {
        "ts": datetime.now().isoformat(timespec="seconds"),
        "ciclos": _estado["ciclos"],
        "reportes": [{k: r.get(k) for k in ("nombre", "ok", "fitness", "ajuste", "alertas") if k in r} for r in reportes],
    }
    with _lock:
        with open(path, "a", encoding="utf-8") as f:
            f.write(json.dumps(resumen, ensure_ascii=False) + "\n")
    info["log"] = str(path)
    return info


def ciclo_enjambre() -> dict:
    with _lock:
        _estado["ciclos"] += 1
        _estado["activo"] = True
    reportes = []
    try:
        v = nanobot_vigilante(); reportes.append(v)
        r = nanobot_reparador(); reportes.append(r)
        a = nanobot_analizador(); reportes.append(a)
        e = nanobot_evolucionador(float(a.get("fitness") or 1.0)); reportes.append(e)
        g = nanobot_guardian(reportes); reportes.append(g)
    except Exception:
        _log("ERROR ciclo\n" + traceback.format_exc())
        reportes.append({"nombre": "SISTEMA", "ok": False})
    with _lock:
        _estado["ultimo"] = datetime.now().isoformat(timespec="seconds")
        _estado["nanobots"] = {r.get("nombre", i): r for i, r in enumerate(reportes)}
    return {
        "ok": all(x.get("ok", True) for x in reportes),
        "ciclos": _estado["ciclos"],
        "timestamp": _estado["ultimo"],
        "nanobots": reportes,
        "params": _load_params(),
    }


def activar() -> dict:
    res = ciclo_enjambre()
    _log("ENJAMBRE ACTIVADO")
    return {"ok": True, "mensaje": "Enjambre unificado activo", "ciclo": res}


def estado() -> dict:
    return {
        "ok": True,
        "activo": _estado["activo"],
        "ciclos": _estado["ciclos"],
        "ultimo": _estado["ultimo"],
        "nanobots": _estado.get("nanobots") or {},
        "params": _load_params(),
    }


def aplicar_params_a_config_motor() -> dict:
    """Sincroniza temperature/max_pasos evolucionados hacia config_motor.json."""
    p = _load_params()
    cfg_path = ROOT / "config_motor.json"
    try:
        cfg = json.loads(cfg_path.read_text(encoding="utf-8")) if cfg_path.exists() else {}
        cfg["temperatura"] = p.get("temperature", cfg.get("temperatura", 0.7))
        cfg["max_pasos_herramientas"] = p.get("max_pasos", cfg.get("max_pasos_herramientas", 24))
        cfg_path.write_text(json.dumps(cfg, ensure_ascii=False, indent=2), encoding="utf-8")
        return {"ok": True, "temperatura": cfg["temperatura"], "max_pasos": cfg["max_pasos_herramientas"]}
    except Exception as e:
        return {"ok": False, "error": str(e)}
