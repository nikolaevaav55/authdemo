# 📚 Literature News Bot

Автоматический бот для поиска и публикации актуальных новостей о литературе в Telegram канале.

## 🌟 Возможности

- **Автоматический поиск новостей** из множества источников (RSS каналы, News API)
- **Фильтрация по тематике** - только новости, связанные с литературой
- **Умное форматирование** сообщений для Telegram
- **Планировщик задач** с настраиваемыми интервалами обновления
- **Защита от дубликатов** - отправляет только новые новости
- **Логирование** всех операций
- **Многоязычная поддержка** (русский и английский)

## 🚀 Быстрый старт

### 1. Установка зависимостей

```bash
pip install -r requirements.txt
```

### 2. Настройка

1. Создайте Telegram бота через [@BotFather](https://t.me/botfather)
2. Получите токен бота
3. Создайте Telegram канал и добавьте бота как администратора
4. Скопируйте `.env.example` в `.env` и заполните настройки:

```bash
cp .env.example .env
```

Отредактируйте `.env`:
```env
TELEGRAM_BOT_TOKEN=your_bot_token_here
TELEGRAM_CHANNEL_ID=@your_channel_name_or_chat_id
NEWS_API_KEY=your_news_api_key_here  # Опционально
UPDATE_INTERVAL_HOURS=6
MAX_NEWS_PER_UPDATE=5
```

### 3. Запуск

```bash
python main.py
```

## ⚙️ Конфигурация

### Обязательные параметры

- `TELEGRAM_BOT_TOKEN` - токен Telegram бота
- `TELEGRAM_CHANNEL_ID` - ID или username канала (например, `@mychannel` или `-1001234567890`)

### Опциональные параметры

- `NEWS_API_KEY` - ключ API для [NewsAPI.org](https://newsapi.org/) (для расширенного поиска)
- `UPDATE_INTERVAL_HOURS` - интервал обновлений в часах (по умолчанию: 6)
- `MAX_NEWS_PER_UPDATE` - максимальное количество новостей за одно обновление (по умолчанию: 5)

## 📡 Источники новостей

Бот использует следующие источники:

### RSS каналы
- Publishers Weekly
- The Guardian Books
- New York Times Book Review
- Goodreads Blog
- Literary Hub
- Bookmarks Reviews

### News API
- Поиск по ключевым словам в международных новостных источниках
- Фильтрация по языкам (русский, английский)

## 🔍 Фильтрация новостей

Бот автоматически фильтрует новости по ключевым словам:

**Русские:** книга, автор, писатель, роман, поэзия, литература, издательство, публикация, рецензия, бестселлер, премия

**Английские:** book, author, writer, novel, poetry, literature, publisher, publishing, review, bestseller, award, fiction, non-fiction, memoir, biography, anthology, manuscript

## 🕐 Расписание работы

По умолчанию бот работает по следующему расписанию:
- Каждые N часов (настраивается в `UPDATE_INTERVAL_HOURS`)
- Ежедневно в 09:00, 15:00 и 21:00 (дополнительно)

## 📁 Структура проекта

```
literature-news-bot/
├── main.py              # Основной файл бота
├── news_scraper.py      # Модуль поиска новостей
├── telegram_bot.py      # Модуль Telegram бота
├── config.py           # Конфигурация
├── requirements.txt    # Зависимости Python
├── .env.example       # Пример конфигурации
├── README.md          # Документация
└── sent_news.json     # База отправленных новостей (создается автоматически)
```

## 🧪 Тестирование

### Тест поиска новостей
```bash
python news_scraper.py
```

### Тест Telegram бота
```bash
python telegram_bot.py
```

## 📝 Логирование

Бот ведет подробные логи в файле `literature_bot.log` и выводит информацию в консоль.

Уровни логирования:
- `INFO` - обычная работа
- `WARNING` - предупреждения
- `ERROR` - ошибки

## 🔧 Исправления совместимости

### Python 3.13+ Совместимость
Бот полностью совместим с Python 3.13+. Исправлены проблемы с модулем `cgi`:
- Обновлен `feedparser` до версии 6.0.11
- Добавлены правильные импорты `html` и `urllib.parse`
- Улучшена обработка RSS каналов с fallback механизмами
- Добавлено подробное логирование для отладки

### Тестирование исправлений
Запустите тест совместимости:
```bash
python3 test_fix.py
```

## 🔧 Устранение неполадок

### Ошибка "Bot token is invalid"
- Проверьте правильность токена бота
- Убедитесь, что бот активен

### Ошибка "Chat not found"
- Проверьте правильность ID канала
- Убедитесь, что бот добавлен в канал как администратор
- Для публичных каналов используйте формат `@channelname`
- Для приватных каналов используйте числовой ID (например, `-1001234567890`)

### Не находит новости
- Проверьте интернет-соединение
- Убедитесь, что RSS каналы доступны
- Проверьте ключевые слова в `config.py`

### Проблемы с News API
- Проверьте правильность API ключа
- Убедитесь, что не превышен лимит запросов
- API ключ опционален, бот работает и без него

## 🚀 Развертывание на сервере

### Systemd сервис (Linux)

Создайте файл `/etc/systemd/system/literature-bot.service`:

```ini
[Unit]
Description=Literature News Bot
After=network.target

[Service]
Type=simple
User=your_user
WorkingDirectory=/path/to/literature-news-bot
ExecStart=/usr/bin/python3 main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Запустите сервис:
```bash
sudo systemctl enable literature-bot
sudo systemctl start literature-bot
sudo systemctl status literature-bot
```

### Docker

Создайте `Dockerfile`:
```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
CMD ["python", "main.py"]
```

Запустите:
```bash
docker build -t literature-bot .
docker run -d --name literature-bot --env-file .env literature-bot
```

## 📄 Лицензия

Этот проект распространяется под лицензией MIT.

## 🤝 Поддержка

Если у вас есть вопросы или предложения, создайте issue в репозитории проекта.

## 📈 Возможные улучшения

- [ ] Веб-интерфейс для управления ботом
- [ ] Поддержка нескольких каналов
- [ ] Категоризация новостей
- [ ] Интеграция с социальными сетями
- [ ] Машинное обучение для лучшей фильтрации
- [ ] Поддержка других языков