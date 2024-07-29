from typing import Any, Dict


OLLAMA_ENDPOINT = "http://localhost:11434/api/generate"
OLLAMA_CONFIG: Dict[str, Any] = {
    "model": "mistral:7b-instruct-v0.2-q4_K_S",
    "keep_alive": "5m",
    "stream": False,
}
