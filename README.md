# Telegram Lead Bot

## Возможности
- 4 языка: польский, украинский, русский, английский;
- имя и фамилия;
- телефон через кнопку Telegram;
- email;
- город Warszawa;
- Google Sheets;
- отправка в тему `Telegram Ads`;
- Telegram ID, username и профиль;
- параметр `/start` для Telegram Ads;
- защита от случайных дублей.

## Запуск
1. Установите Python 3.11+.
2. Создайте окружение:
```bash
python -m venv .venv
```
3. Активируйте его и установите зависимости:
```bash
pip install -r requirements.txt
```
4. Скопируйте `.env.example` в `.env`.
5. Вставьте новый Bot Token в `.env`.
6. Положите ключ Google рядом с проектом под именем `service_account.json`.
7. Запустите:
```bash
python -m app.main
```

## Рекламные ссылки
```text
https://t.me/USERNAME_BOT?start=ads_ru
https://t.me/USERNAME_BOT?start=ads_ua
https://t.me/USERNAME_BOT?start=ads_pl
https://t.me/USERNAME_BOT?start=ads_en
```

## Docker
```bash
docker compose up -d --build
```
