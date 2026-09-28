import requests

from backend.config import (
    OLLAMA_URL,
    EMBEDDING_MODEL
)


def create_embedding(text):

    url = f"{OLLAMA_URL}/api/embed"

    response = requests.post(
        url,
        json={
            "model": EMBEDDING_MODEL,
            "input": text
        },
        timeout=120
    )

    response.raise_for_status()

    data = response.json()

    return data["embeddings"][0]