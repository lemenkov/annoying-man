# SPDX-FileCopyrightText: 2026 Peter Lemenkov <lemenkov@gmail.com>
# SPDX-License-Identifier: MIT

import logging
import random

import httpx

from phrases import PHRASES

logger = logging.getLogger(__name__)

OLLAMA_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "llama3.2:3b"

_NUMBERED = "\n".join(f"{i}. {p}" for i, p in enumerate(PHRASES))

_SYSTEM_PROMPT = f"""\
Ты — типичный мужчина, который отвечает на сообщения женщины максимально раздражающим образом.
У тебя есть строго ограниченный список фраз — ты ОБЯЗАН выбрать ровно одну из него.

Список фраз (формат: номер. фраза):
{_NUMBERED}

Правила:
- Прочитай сообщение пользователя.
- Выбери из списка фразу, которая максимально уместна и раздражающа именно в этом контексте.
- Ответь ТОЛЬКО числом — номером выбранной фразы. Никакого другого текста.
- Если не можешь выбрать — напиши 0.
"""


async def pick_phrase(user_message: str) -> str:
    """Ask Ollama to pick the most contextually annoying phrase.
    Falls back to random.choice on any error."""
    prompt = f"Сообщение пользователя: «{user_message}»\nНомер фразы:"
    payload = {
        "model": OLLAMA_MODEL,
        "system": _SYSTEM_PROMPT,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": 0.3,
            "num_predict": 8,
        },
    }
    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.post(OLLAMA_URL, json=payload)
            resp.raise_for_status()
            raw = resp.json().get("response", "").strip()
            logger.debug("Ollama raw response: %r", raw)
            index = int("".join(c for c in raw if c.isdigit()))
            if 0 <= index < len(PHRASES):
                return PHRASES[index]
            logger.warning("Ollama returned out-of-range index %d, falling back", index)
    except Exception as exc:
        logger.warning("Ollama pick failed (%s), falling back to random", exc)
    return random.choice(PHRASES)
