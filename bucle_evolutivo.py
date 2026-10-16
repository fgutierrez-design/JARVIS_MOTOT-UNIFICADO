# -*- coding: utf-8 -*-
"""Bucle de evolucion en segundo plano (cada N minutos)."""
from __future__ import annotations
import json, threading, time
from pathlib import Path

ROOT = Path(__file__).resolve().parent
_stop = threading.Event()
_thread = None


def _interval():
    try:
        cfg = json.loads((ROOT / "config_motor.json").read_text(encoding="utf-8"))
        return max(60, int(float(cfg.get("intervalo_evolucion_min", 30)) * 60))
    except Exception:
        return 30 * 60


def _loop():
    time.sleep(10)
    while not _stop.is_set():
        try:
            import enjambre_unificado as ej
            ej.ciclo_enjambre()
            ej.aplicar_params_a_config_motor()
        except Exception as e:
            print("[bucle_evolutivo]", e)
        for _ in range(_interval()):
            if _stop.is_set():
                break
            time.sleep(1)


def iniciar():
    global _thread
    if _thread and _thread.is_alive():
        return {"ok": True, "mensaje": "ya corria"}
    _stop.clear()
    _thread = threading.Thread(target=_loop, name="JARVIS-Evolucion", daemon=True)
    _thread.start()
    return {"ok": True, "mensaje": "bucle evolucion iniciado", "interval_seg": _interval()}


def detener():
    _stop.set()
    return {"ok": True}
