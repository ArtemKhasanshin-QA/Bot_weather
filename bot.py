import asyncio
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes
from weather_api import WeatherAPI
import config

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

class WeatherBot:
    """Основной класс телеграм бота для погоды"""
    
    def __init__(self):
        self.weather_api = WeatherAPI()
        self.application = None
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /start"""
        keyboard = [
            [InlineKeyboardButton("🌤️ Погода сейчас", callback_data="weather_now")],
            [InlineKeyboardButton("📅 Прогноз на 5 дней", callback_data="weather_forecast")],
            [InlineKeyboardButton("⚙️ Настройки", callback_data="settings")],
            [InlineKeyboardButton("❓ Помощь", callback_data="help")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            config.WELCOME_MESSAGE,
            reply_markup=reply_markup
        )
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /help"""
        await update.message.reply_text(config.HELP_MESSAGE)
    
    async def weather_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /weather <город>"""
        if not context.args:
            await update.message.reply_text(
                "❌ Пожалуйста, укажите город!\n"
                "Пример: /weather Москва"
            )
            return
        
        city = " ".join(context.args)
        await self._show_current_weather(update, context, city)
    
    async def forecast_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /forecast <город>"""
        if not context.args:
            await update.message.reply_text(
                "❌ Пожалуйста, укажите город!\n"
                "Пример: /forecast Москва"
            )
            return
        
        city = " ".join(context.args)
        await self._show_forecast(update, context, city)
    
    async def settings_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /settings"""
        keyboard = [
            [InlineKeyboardButton("🇷🇺 Русский", callback_data="lang_ru")],
            [InlineKeyboardButton("🇺🇸 English", callback_data="lang_en")],
            [InlineKeyboardButton("🌡️ Цельсий", callback_data="units_metric")],
            [InlineKeyboardButton("🌡️ Фаренгейт", callback_data="units_imperial")],
            [InlineKeyboardButton("🔙 Назад", callback_data="back_to_main")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            "⚙️ Настройки бота:\n\n"
            "Выберите язык и единицы измерения:",
            reply_markup=reply_markup
        )
    
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик текстовых сообщений (названия городов)"""
        text = update.message.text.strip()
        
        # Если сообщение похоже на название города, показываем погоду
        if len(text) > 1 and text.isalpha():
            await self._show_current_weather(update, context, text)
        else:
            await update.message.reply_text(
                "🌤️ Напишите название города, чтобы узнать погоду!\n"
                "Или используйте команды:\n"
                "/weather <город> - погода сейчас\n"
                "/forecast <город> - прогноз на 5 дней"
            )
    
    async def handle_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик callback кнопок"""
        query = update.callback_query
        await query.answer()
        
        if query.data == "weather_now":
            await query.edit_message_text(
                "🌤️ Введите название города для получения текущей погоды:"
            )
            context.user_data['waiting_for'] = 'weather'
            
        elif query.data == "weather_forecast":
            await query.edit_message_text(
                "📅 Введите название города для получения прогноза на 5 дней:"
            )
            context.user_data['waiting_for'] = 'forecast'
            
        elif query.data == "settings":
            await self._show_settings(query)
            
        elif query.data == "help":
            await query.edit_message_text(config.HELP_MESSAGE)
            
        elif query.data == "back_to_main":
            await self._show_main_menu(query)
            
        elif query.data.startswith("lang_"):
            lang = query.data.split("_")[1]
            self.weather_api.language = lang
            await query.edit_message_text(f"✅ Язык изменен на: {lang.upper()}")
            
        elif query.data.startswith("units_"):
            units = query.data.split("_")[1]
            self.weather_api.units = units
            await query.edit_message_text(f"✅ Единицы измерения изменены на: {units}")
    
    async def _show_current_weather(self, update: Update, context: ContextTypes.DEFAULT_TYPE, city: str):
        """Показать текущую погоду"""
        await update.message.reply_text(f"🌤️ Получаю погоду для города {city}...")
        
        weather_data = await self.weather_api.get_current_weather(city)
        
        if weather_data:
            emoji = self.weather_api.get_weather_emoji(weather_data['icon'])
            temp_unit = "°C" if self.weather_api.units == "metric" else "°F"
            wind_unit = "м/с" if self.weather_api.units == "metric" else "миль/ч"
            
            message = f"""
{emoji} **Погода в {weather_data['city']}, {weather_data['country']}**

🌡️ Температура: {weather_data['temperature']}{temp_unit}
🌡️ Ощущается как: {weather_data['feels_like']}{temp_unit}
☁️ Описание: {weather_data['description']}
💧 Влажность: {weather_data['humidity']}%
🌪️ Ветер: {weather_data['wind_speed']} {wind_unit}
📊 Давление: {weather_data['pressure']} гПа
            """.strip()
            
            await update.message.reply_text(message)
        else:
            await update.message.reply_text(
                f"❌ Не удалось получить погоду для города {city}.\n"
                "Проверьте правильность названия города."
            )
    
    async def _show_forecast(self, update: Update, context: ContextTypes.DEFAULT_TYPE, city: str):
        """Показать прогноз погоды"""
        await update.message.reply_text(f"📅 Получаю прогноз погоды для города {city}...")
        
        forecast_data = await self.weather_api.get_forecast(city)
        
        if forecast_data:
            temp_unit = "°C" if self.weather_api.units == "metric" else "°F"
            
            message = f"📅 **Прогноз погоды в {forecast_data['city']}, {forecast_data['country']}**\n\n"
            
            for forecast in forecast_data['forecasts']:
                emoji = self.weather_api.get_weather_emoji(forecast['icon'])
                date = forecast['date']
                message += f"{emoji} **{date}**\n"
                message += f"🌡️ {forecast['temperature']}{temp_unit} | 💧 {forecast['humidity']}%\n"
                message += f"☁️ {forecast['description']}\n\n"
            
            await update.message.reply_text(message.strip())
        else:
            await update.message.reply_text(
                f"❌ Не удалось получить прогноз для города {city}.\n"
                "Проверьте правильность названия города."
            )
    
    async def _show_settings(self, query):
        """Показать настройки"""
        keyboard = [
            [InlineKeyboardButton("🇷🇺 Русский", callback_data="lang_ru")],
            [InlineKeyboardButton("🇺🇸 English", callback_data="lang_en")],
            [InlineKeyboardButton("🌡️ Цельсий", callback_data="units_metric")],
            [InlineKeyboardButton("🌡️ Фаренгейт", callback_data="units_imperial")],
            [InlineKeyboardButton("🔙 Назад", callback_data="back_to_main")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            "⚙️ Настройки бота:\n\n"
            "Выберите язык и единицы измерения:",
            reply_markup=reply_markup
        )
    
    async def _show_main_menu(self, query):
        """Показать главное меню"""
        keyboard = [
            [InlineKeyboardButton("🌤️ Погода сейчас", callback_data="weather_now")],
            [InlineKeyboardButton("📅 Прогноз на 5 дней", callback_data="weather_forecast")],
            [InlineKeyboardButton("⚙️ Настройки", callback_data="settings")],
            [InlineKeyboardButton("❓ Помощь", callback_data="help")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            config.WELCOME_MESSAGE,
            reply_markup=reply_markup
        )
    
    def run(self):
        """Запуск бота"""
        if not config.BOT_TOKEN:
            logger.error("Не указан токен бота! Создайте файл .env с TELEGRAM_BOT_TOKEN")
            return
        
        # Создаем приложение
        self.application = Application.builder().token(config.BOT_TOKEN).build()
        
        # Добавляем обработчики
        self.application.add_handler(CommandHandler("start", self.start_command))
        self.application.add_handler(CommandHandler("help", self.help_command))
        self.application.add_handler(CommandHandler("weather", self.weather_command))
        self.application.add_handler(CommandHandler("forecast", self.forecast_command))
        self.application.add_handler(CommandHandler("settings", self.settings_command))
        self.application.add_handler(CallbackQueryHandler(self.handle_callback))
        self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))
        
        # Запускаем бота
        logger.info("Бот запущен!")
        self.application.run_polling()

if __name__ == "__main__":
    bot = WeatherBot()
    bot.run()
