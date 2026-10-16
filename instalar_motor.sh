#!/usr/bin/env bash
set -e
cd "$(dirname "$0")"
pip install -r requirements.txt
echo "SIN Ollama. Solo GROQ_API_KEY."
echo "python3 servidor_motor.py"
