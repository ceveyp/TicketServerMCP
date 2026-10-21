from functools import lru_cache
from typing import List

import tiktoken

from app.settings import get_settings


class Encoder:
    def __init__(self):
        settings = get_settings()
        self._encoding = tiktoken.get_encoding(settings.tiktoken_encoding_model)

    def encode(self, text: str) -> List[int]:
        return self._encoding.encode(text)

    def count(self, text: str) -> int:
        return len(self.encode(text))


@lru_cache
def get_encoder() -> Encoder:
    return Encoder()
