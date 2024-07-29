from typing import List
import httpx
from ollama_config import OLLAMA_CONFIG, OLLAMA_ENDPOINT


def query_prompt(prompt):
    response = httpx.post(
        OLLAMA_ENDPOINT,
        json={"prompt": prompt, **OLLAMA_CONFIG},
        headers={"Content-Type": "application/json"},
        timeout=300000,
    )
    if response.status_code != 200:
        print("Error", response.status_code)
        return None
    return str(response.json()["response"].strip())
