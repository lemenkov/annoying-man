<!--
SPDX-FileCopyrightText: 2026 Peter Lemenkov <lemenkov@gmail.com>
SPDX-License-Identifier: MIT
-->

# annoying_bot

A Telegram bot that responds to any message with a classic annoying men's phrase in Russian.

Inspired by the timeless internet query: *«мужские ответы, которые раздражают женщин»*.

## Phrases included

- Классика уклонения: «Сейчас», «Посмотрим», «Будет видно»…
- Великое «Нормально» и его братья: «Ок», «Ясно», 👍
- Обесценивание: «Успокойся», «Будь проще», «У тебя ПМС?»
- Перекладывание ответственности: «Тебе надо — ты и делай»…
- Отмазки: «Не заметил сообщение», «Уснул»…
- Бытовая беспомощность: «Где у нас вилки?»…
- И многое другое.

## Setup

```bash
pip install -r requirements.txt
# Put your bot token in bot.py (BOT_TOKEN)
python bot.py
```

## Systemd

```bash
sudo cp annoying-bot.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now annoying-bot
```

## License

MIT — see `LICENSES/MIT.txt`
