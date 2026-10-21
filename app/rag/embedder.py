from functools import lru_cache
from typing import List

from openrouter import OpenRouter
from openrouter.operations import CreateEmbeddingsResponseBody

from app.rag.encoder import Encoder
from app.settings import get_settings


class Embedder(Encoder):
    def __init__(self):
        super().__init__()
        self._settings = get_settings()
        self._client = OpenRouter(api_key=self._settings.openrouter_api_key)

    def embed(self, text: str) -> List[float]:
        res: CreateEmbeddingsResponseBody = self._client.embeddings.generate(
            model=self._settings.embedding_model,
            input=text,
            dimensions=self._settings.embedding_size
        )
        return res.data[0].embedding


@lru_cache
def get_embedder() -> Embedder:
    return Embedder()
