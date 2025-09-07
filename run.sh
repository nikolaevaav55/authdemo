#!/bin/bash

# Скрипт для запуска Literature News Bot

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}🚀 Запуск Literature News Bot${NC}"

# Проверяем наличие Python
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python3 не найден. Установите Python3 для продолжения.${NC}"
    exit 1
fi

# Проверяем версию Python
PYTHON_VERSION=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
echo -e "${GREEN}🐍 Обнаружен Python ${PYTHON_VERSION}${NC}"

# Предупреждение для Python 3.13+
if python3 -c "import sys; exit(0 if sys.version_info >= (3, 13) else 1)" 2>/dev/null; then
    echo -e "${YELLOW}⚠️  Обнаружен Python 3.13+. Используем обновленные зависимости.${NC}"
fi

# Проверяем наличие pip
if ! command -v pip3 &> /dev/null; then
    echo -e "${RED}❌ pip3 не найден. Установите pip3 для продолжения.${NC}"
    exit 1
fi

# Проверяем наличие .env файла
if [ ! -f .env ]; then
    echo -e "${YELLOW}⚠️  Файл .env не найден. Копируем из .env.example${NC}"
    if [ -f .env.example ]; then
        cp .env.example .env
        echo -e "${YELLOW}📝 Пожалуйста, отредактируйте файл .env и добавьте ваши настройки:${NC}"
        echo -e "${YELLOW}   - TELEGRAM_BOT_TOKEN${NC}"
        echo -e "${YELLOW}   - TELEGRAM_CHANNEL_ID${NC}"
        echo -e "${YELLOW}Затем запустите скрипт снова.${NC}"
        exit 1
    else
        echo -e "${RED}❌ Файл .env.example не найден!${NC}"
        exit 1
    fi
fi

# Проверяем наличие виртуального окружения
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}📦 Создаем виртуальное окружение...${NC}"
    python3 -m venv venv
fi

# Активируем виртуальное окружение
echo -e "${GREEN}🔧 Активируем виртуальное окружение...${NC}"
source venv/bin/activate

# Устанавливаем зависимости
echo -e "${GREEN}📥 Устанавливаем зависимости...${NC}"
pip install -r requirements.txt

# Проверяем основные настройки
echo -e "${GREEN}🔍 Проверяем конфигурацию...${NC}"

# Загружаем переменные из .env
if [ -f .env ]; then
    export $(cat .env | grep -v '^#' | xargs)
fi

# Проверяем обязательные переменные
if [ -z "$TELEGRAM_BOT_TOKEN" ]; then
    echo -e "${RED}❌ TELEGRAM_BOT_TOKEN не установлен в .env файле${NC}"
    exit 1
fi

if [ -z "$TELEGRAM_CHANNEL_ID" ]; then
    echo -e "${RED}❌ TELEGRAM_CHANNEL_ID не установлен в .env файле${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Конфигурация проверена${NC}"

# Запускаем бота
echo -e "${GREEN}🤖 Запускаем бота...${NC}"
echo -e "${YELLOW}Для остановки нажмите Ctrl+C${NC}"
echo ""

python main.py