# JARVIS Motor Unificado U1.0

**Un solo motor** que combina:

| Capa | Que hace |
|------|----------|
| **Groq** | Razonamiento LLM (sin Ollama) |
| **Agente** | Herramientas: web, archivos, python, memoria |
| **Enjambre** | 5 nanobots: Vigilante, Reparador, Analizador, Evolucionador, Guardian |
| **Aprendizaje** | Guarda cada consulta util |
| **Evolucion** | Ajusta temperatura/pasos segun fitness; bucle cada 30 min |

## Principios
- **Sin Ollama**
- **Sin censura** de contenido adulto
- **Limites altos** (8k tokens, 24 pasos tools)
- **Actualizacion continua** (enjambre + aprendizaje)

## Arranque
```bash
export GROQ_API_KEY=tu_key
pip install -r requirements.txt
python3 servidor_motor.py
```
Puerto **11435**. Compatible OpenAI `/v1/chat/completions`.

## API extra
- `POST /api/pensar` — agente completo
- `POST /api/enjambre/ciclo` — un ciclo de nanobots
- `POST /api/evolucionar` — forzar evolucion
- `POST /api/aprender` — guardar conocimiento

## Enganche JARVIS
En `motores.py` usa tipo `openai` con `base_url: http://127.0.0.1:11435`.

TECNO G — La Punta, San Luis
