# SPDX-FileCopyrightText: 2026 Peter Lemenkov <lemenkov@gmail.com>
# SPDX-License-Identifier: MIT

import os
import logging
import re
import random
import httpx
from phrases import PHRASES

logger = logging.getLogger(__name__)

DEEPSEEK_URL = "https://api.deepseek.com/v1/chat/completions"
DEEPSEEK_API_KEY = os.environ.get("DEEPSEEK_API_KEY")

_NUMBERED = "\n".join(f"{i}. {p}" for i, p in enumerate(PHRASES))
_SYSTEM_PROMPT = f"""\
Ты — типичный мужчина, который отвечает на сообщения женщины максимально раздражающим образом.
У тебя есть строго ограниченный список фраз — ты ОБЯЗАН выбрать ровно одну из него.
Список фраз (формат: номер. фраза):
{_NUMBERED}

Правила:
- Прочитай сообщение пользователя внимательно.
- В одном предложении определи: о чём просят, какие эмоции выражены, чего ждут в ответ.
- Выбери фразу, которая максимально раздражает именно в этом контексте — игнорирует суть, обесценивает или уклоняется.
- Напиши рассуждение строго в формате: МЫСЛЬ: <одно предложение>
- Затем напиши: ОТВЕТ: <только число>
- Никакого другого текста после ОТВЕТ.
"""

_ANSWER_RE = re.compile(r"ОТВЕТ:\s*(\d+)")

async def check_deepseek() -> bool:
    """Проверяет доступность DeepSeek API."""
    if not DEEPSEEK_API_KEY:
        logger.warning("DEEPSEEK_API_KEY not set")
        return False
    # Можно сделать лёгкий ping через небольшой запрос
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.post(
                DEEPSEEK_URL,
                headers={"Authorization": f"Bearer {DEEPSEEK_API_KEY}"},
                json={
                    "model": "deepseek-chat",
                    "messages": [{"role": "user", "content": "Привет"}],
                    "max_tokens": 5
                }
            )
            resp.raise_for_status()
            logger.info("DeepSeek API is reachable")
            return True
    except Exception as e:
        logger.warning(f"DeepSeek API is NOT reachable: {e}")
        return False

async def pick_phrase(user_message: str) -> str:
    """Отправляет запрос в DeepSeek и возвращает выбранную фразу."""
    if not DEEPSEEK_API_KEY:
        logger.warning("DEEPSEEK_API_KEY not set, falling back to random")
        return random.choice(PHRASES)

    prompt = f"Сообщение пользователя: «{user_message}»"
    payload = {
        "model": "deepseek-chat",
        "messages": [
            {"role": "system", "content": _SYSTEM_PROMPT},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.2,
        "max_tokens": 64,
    }
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(
                DEEPSEEK_URL,
                headers={
                    "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
                    "Content-Type": "application/json"
                },
                json=payload
            )
            resp.raise_for_status()
            data = resp.json()
            raw = data["choices"][0]["message"]["content"].strip()
            logger.debug("DeepSeek raw response: %r", raw)

            match = _ANSWER_RE.search(raw)
            if match:
                index = int(match.group(1))
                if 0 <= index < len(PHRASES):
                    return PHRASES[index]
                logger.warning("DeepSeek returned out-of-range index %d", index)
            else:
                logger.warning("No ОТВЕТ: found in DeepSeek response")
    except Exception as e:
        logger.warning(f"DeepSeek pick failed: {e}")

    return random.choice(PHRASES)
