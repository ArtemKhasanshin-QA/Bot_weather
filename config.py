import os
from dotenv import load_dotenv

# Загружаем переменные окружения из .env файла
load_dotenv()

# Конфигурация бота
BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
OPENWEATHER_API_KEY = os.getenv('OPENWEATHER_API_KEY')

# API endpoints
OPENWEATHER_BASE_URL = "http://api.openweathermap.org/data/2.5"
WEATHER_ENDPOINT = "/weather"
FORECAST_ENDPOINT = "/forecast"

# Настройки по умолчанию
DEFAULT_LANGUAGE = "ru"
DEFAULT_UNITS = "metric"  # metric для Цельсия, imperial для Фаренгейта

# Сообщения бота
WELCOME_MESSAGE = """
🌤️ Добро пожаловать в Weather Bot!

Доступные команды:
/start - Начать работу с ботом
/weather <город> - Узнать погоду в городе
/forecast <город> - Прогноз погоды на 5 дней
/help - Показать справку
/settings - Настройки бота

Примеры:
/weather Москва
/forecast Санкт-Петербург
"""

HELP_MESSAGE = """
📚 Справка по использованию бота:

1. **Погода сейчас**: `/weather <город>`
   Показывает текущую погоду в указанном городе

2. **Прогноз на 5 дней**: `/forecast <город>`
   Показывает прогноз погоды на ближайшие 5 дней

3. **Настройки**: `/settings`
   Изменение языка и единиц измерения

4. **Справка**: `/help`
   Показать это сообщение

💡 Совет: Просто напишите название города, и бот покажет погоду!
"""
