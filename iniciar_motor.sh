#!/usr/bin/env bash
cd "$(dirname "$0")"
export JARVIS_MOTOR_PORT="${JARVIS_MOTOR_PORT:-11435}"
# export GROQ_API_KEY=...
python3 servidor_motor.py
