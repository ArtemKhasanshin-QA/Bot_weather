import asyncio
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes
from weather_api import WeatherAPI
from news_api import NewsAPI
from currency_api import CurrencyAPI
import config

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

class AdvancedWeatherBot:
    """Расширенный телеграм бот с функциями погоды, новостей и валют"""
    
    def __init__(self):
        self.weather_api = WeatherAPI()
        self.news_api = NewsAPI()
        self.currency_api = CurrencyAPI()
        self.application = None
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /start"""
        keyboard = [
            [InlineKeyboardButton("🌤️ Погода", callback_data="weather_menu")],
            [InlineKeyboardButton("📰 Новости", callback_data="news_menu")],
            [InlineKeyboardButton("💱 Курсы валют", callback_data="currency_menu")],
            [InlineKeyboardButton("⚙️ Настройки", callback_data="settings")],
            [InlineKeyboardButton("❓ Помощь", callback_data="help")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        welcome_text = """
🤖 **Добро пожаловать в Advanced Weather Bot!**

Этот бот поможет вам:
• 🌤️ Узнать погоду в любом городе
• 📰 Читать последние новости
• 💱 Следить за курсами валют
• ⚙️ Настраивать параметры

Выберите нужную функцию:
        """.strip()
        
        await update.message.reply_text(welcome_text, reply_markup=reply_markup)
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /help"""
        help_text = """
📚 **Справка по использованию бота:**

**🌤️ Погода:**
• `/weather <город>` - текущая погода
• `/forecast <город>` - прогноз на 5 дней

**📰 Новости:**
• `/news` - топ новости России
• `/news <категория>` - новости по категории
• `/search <запрос>` - поиск новостей

**💱 Валюты:**
• `/currency` - курсы валют
• `/convert <сумма> <из> <в>` - конвертер

**⚙️ Настройки:**
• `/settings` - настройки бота

💡 **Совет:** Просто напишите название города для получения погоды!
        """.strip()
        
        await update.message.reply_text(help_text)
    
    # === ОБРАБОТЧИКИ ПОГОДЫ ===
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
    
    # === ОБРАБОТЧИКИ НОВОСТЕЙ ===
    async def news_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /news"""
        category = context.args[0] if context.args else "general"
        await self._show_news(update, context, category)
    
    async def search_news_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /search <запрос>"""
        if not context.args:
            await update.message.reply_text(
                "❌ Пожалуйста, укажите поисковый запрос!\n"
                "Пример: /search технологии"
            )
            return
        
        query = " ".join(context.args)
        await self._search_news(update, context, query)
    
    # === ОБРАБОТЧИКИ ВАЛЮТ ===
    async def currency_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /currency"""
        await self._show_currency_rates(update, context)
    
    async def convert_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /convert <сумма> <из> <в>"""
        if len(context.args) != 3:
            await update.message.reply_text(
                "❌ Неправильный формат команды!\n"
                "Пример: /convert 100 USD RUB"
            )
            return
        
        try:
            amount = float(context.args[0])
            from_currency = context.args[1].upper()
            to_currency = context.args[2].upper()
            await self._convert_currency(update, context, amount, from_currency, to_currency)
        except ValueError:
            await update.message.reply_text("❌ Сумма должна быть числом!")
    
    # === ОБРАБОТЧИКИ НАСТРОЕК ===
    async def settings_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /settings"""
        await self._show_settings(update, context)
    
    # === ОБРАБОТЧИКИ СООБЩЕНИЙ ===
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик текстовых сообщений"""
        text = update.message.text.strip()
        
        # Если сообщение похоже на название города, показываем погоду
        if len(text) > 1 and text.replace(' ', '').isalpha():
            await self._show_current_weather(update, context, text)
        else:
            await update.message.reply_text(
                "🌤️ Напишите название города, чтобы узнать погоду!\n"
                "Или используйте команды:\n"
                "/weather <город> - погода сейчас\n"
                "/forecast <город> - прогноз на 5 дней\n"
                "/news - последние новости\n"
                "/currency - курсы валют"
            )
    
    # === ОБРАБОТЧИКИ CALLBACK ===
    async def handle_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик callback кнопок"""
        query = update.callback_query
        await query.answer()
        
        if query.data == "weather_menu":
            await self._show_weather_menu(query)
        elif query.data == "news_menu":
            await self._show_news_menu(query)
        elif query.data == "currency_menu":
            await self._show_currency_menu(query)
        elif query.data == "settings":
            await self._show_settings_menu(query)
        elif query.data == "help":
            await self._show_help_menu(query)
        elif query.data == "back_to_main":
            await self._show_main_menu(query)
        elif query.data.startswith("weather_"):
            await self._handle_weather_callback(query, context)
        elif query.data.startswith("news_"):
            await self._handle_news_callback(query, context)
        elif query.data.startswith("currency_"):
            await self._handle_currency_callback(query, context)
        elif query.data.startswith("settings_"):
            await self._handle_settings_callback(query, context)
    
    # === МЕНЮ ПОГОДЫ ===
    async def _show_weather_menu(self, query):
        """Показать меню погоды"""
        keyboard = [
            [InlineKeyboardButton("🌤️ Погода сейчас", callback_data="weather_current")],
            [InlineKeyboardButton("📅 Прогноз на 5 дней", callback_data="weather_forecast")],
            [InlineKeyboardButton("🔙 Назад", callback_data="back_to_main")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            "🌤️ **Меню погоды**\n\n"
            "Выберите, что хотите узнать:",
            reply_markup=reply_markup
        )
    
    # === МЕНЮ НОВОСТЕЙ ===
    async def _show_news_menu(self, query):
        """Показать меню новостей"""
        categories = self.news_api.get_available_categories()
        keyboard = []
        
        # Создаем кнопки для категорий (по 2 в ряд)
        for i in range(0, len(categories), 2):
            row = []
            row.append(InlineKeyboardButton(
                categories[i].title(), 
                callback_data=f"news_category_{categories[i]}"
            ))
            if i + 1 < len(categories):
                row.append(InlineKeyboardButton(
                    categories[i + 1].title(), 
                    callback_data=f"news_category_{categories[i + 1]}"
                ))
            keyboard.append(row)
        
        keyboard.append([InlineKeyboardButton("🔙 Назад", callback_data="back_to_main")])
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            "📰 **Меню новостей**\n\n"
            "Выберите категорию новостей:",
            reply_markup=reply_markup
        )
    
    # === МЕНЮ ВАЛЮТ ===
    async def _show_currency_menu(self, query):
        """Показать меню валют"""
        keyboard = [
            [InlineKeyboardButton("💱 Курсы валют", callback_data="currency_rates")],
            [InlineKeyboardButton("🔄 Конвертер", callback_data="currency_converter")],
            [InlineKeyboardButton("🔙 Назад", callback_data="back_to_main")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            "💱 **Меню валют**\n\n"
            "Выберите функцию:",
            reply_markup=reply_markup
        )
    
    # === МЕНЮ НАСТРОЕК ===
    async def _show_settings_menu(self, query):
        """Показать меню настроек"""
        keyboard = [
            [InlineKeyboardButton("🇷🇺 Русский", callback_data="settings_lang_ru")],
            [InlineKeyboardButton("🇺🇸 English", callback_data="settings_lang_en")],
            [InlineKeyboardButton("🌡️ Цельсий", callback_data="settings_units_metric")],
            [InlineKeyboardButton("🌡️ Фаренгейт", callback_data="settings_units_imperial")],
            [InlineKeyboardButton("🔙 Назад", callback_data="back_to_main")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            "⚙️ **Настройки бота**\n\n"
            "Выберите язык и единицы измерения:",
            reply_markup=reply_markup
        )
    
    # === ГЛАВНОЕ МЕНЮ ===
    async def _show_main_menu(self, query):
        """Показать главное меню"""
        keyboard = [
            [InlineKeyboardButton("🌤️ Погода", callback_data="weather_menu")],
            [InlineKeyboardButton("📰 Новости", callback_data="news_menu")],
            [InlineKeyboardButton("💱 Курсы валют", callback_data="currency_menu")],
            [InlineKeyboardButton("⚙️ Настройки", callback_data="settings")],
            [InlineKeyboardButton("❓ Помощь", callback_data="help")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            "🤖 **Главное меню**\n\n"
            "Выберите нужную функцию:",
            reply_markup=reply_markup
        )
    
    # === ОБРАБОТЧИКИ CALLBACK ПО ФУНКЦИЯМ ===
    async def _handle_weather_callback(self, query, context):
        """Обработка callback для погоды"""
        if query.data == "weather_current":
            await query.edit_message_text(
                "🌤️ Введите название города для получения текущей погоды:"
            )
            context.user_data['waiting_for'] = 'weather_current'
        elif query.data == "weather_forecast":
            await query.edit_message_text(
                "📅 Введите название города для получения прогноза на 5 дней:"
            )
            context.user_data['waiting_for'] = 'weather_forecast'
    
    async def _handle_news_callback(self, query, context):
        """Обработка callback для новостей"""
        if query.data.startswith("news_category_"):
            category = query.data.split("_")[2]
            await self._show_news_by_category(query, context, category)
    
    async def _handle_currency_callback(self, query, context):
        """Обработка callback для валют"""
        if query.data == "currency_rates":
            await self._show_currency_rates_callback(query, context)
        elif query.data == "currency_converter":
            await query.edit_message_text(
                "🔄 **Конвертер валют**\n\n"
                "Используйте команду:\n"
                "`/convert <сумма> <из> <в>`\n\n"
                "Примеры:\n"
                "• `/convert 100 USD RUB`\n"
                "• `/convert 50 EUR USD`\n"
                "• `/convert 1000 RUB EUR`\n\n"
                "🔙 Нажмите кнопку для возврата:",
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("🔙 Назад", callback_data="currency_menu")
                ]])
            )
    
    async def _handle_settings_callback(self, query, context):
        """Обработка callback для настроек"""
        if query.data.startswith("settings_lang_"):
            lang = query.data.split("_")[2]
            self.weather_api.language = lang
            await query.edit_message_text(f"✅ Язык изменен на: {lang.upper()}")
        elif query.data.startswith("settings_units_"):
            units = query.data.split("_")[2]
            self.weather_api.units = units
            await query.edit_message_text(f"✅ Единицы измерения изменены на: {units}")
    
    # === ФУНКЦИИ ПОКАЗА ДАННЫХ ===
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
    
    async def _show_news(self, update: Update, context: ContextTypes.DEFAULT_TYPE, category: str = "general"):
        """Показать новости по категории"""
        await update.message.reply_text(f"📰 Получаю новости категории '{category}'...")
        
        news_data = await self.news_api.get_top_headlines(country="ru", category=category, limit=5)
        
        if news_data:
            message = f"📰 **Топ новости России - {category.title()}**\n\n"
            
            for i, news in enumerate(news_data, 1):
                message += f"**{i}. {news['title']}**\n"
                message += f"📝 {news['description']}\n"
                message += f"📰 Источник: {news['source']}\n"
                if news['url']:
                    message += f"🔗 [Читать далее]({news['url']})\n"
                message += "\n"
            
            await update.message.reply_text(message.strip(), disable_web_page_preview=True)
        else:
            await update.message.reply_text(
                f"❌ Не удалось получить новости категории '{category}'.\n"
                "Возможно, API ключ не настроен или произошла ошибка."
            )
    
    async def _search_news(self, update: Update, context: ContextTypes.DEFAULT_TYPE, query: str):
        """Поиск новостей по запросу"""
        await update.message.reply_text(f"🔍 Ищу новости по запросу '{query}'...")
        
        news_data = await self.news_api.search_news(query, limit=5)
        
        if news_data:
            message = f"🔍 **Результаты поиска: '{query}'**\n\n"
            
            for i, news in enumerate(news_data, 1):
                message += f"**{i}. {news['title']}**\n"
                message += f"📝 {news['description']}\n"
                message += f"📰 Источник: {news['source']}\n"
                if news['url']:
                    message += f"🔗 [Читать далее]({news['url']})\n"
                message += "\n"
            
            await update.message.reply_text(message.strip(), disable_web_page_preview=True)
        else:
            await update.message.reply_text(
                f"❌ Не удалось найти новости по запросу '{query}'.\n"
                "Попробуйте изменить поисковый запрос."
            )
    
    async def _show_news_by_category(self, query, context, category: str):
        """Показать новости по категории через callback"""
        await query.edit_message_text(f"📰 Получаю новости категории '{category}'...")
        
        news_data = await self.news_api.get_top_headlines(country="ru", category=category, limit=5)
        
        if news_data:
            message = f"📰 **Топ новости России - {category.title()}**\n\n"
            
            for i, news in enumerate(news_data, 1):
                message += f"**{i}. {news['title']}**\n"
                message += f"📝 {news['description']}\n"
                message += f"📰 Источник: {news['source']}\n"
                if news['url']:
                    message += f"🔗 [Читать далее]({news['url']})\n"
                message += "\n"
            
            keyboard = [[InlineKeyboardButton("🔙 Назад к категориям", callback_data="news_menu")]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text(
                message.strip(), 
                reply_markup=reply_markup,
                disable_web_page_preview=True
            )
        else:
            await query.edit_message_text(
                f"❌ Не удалось получить новости категории '{category}'.",
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("🔙 Назад", callback_data="news_menu")
                ]])
            )
    
    async def _show_currency_rates(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Показать курсы валют"""
        await update.message.reply_text("💱 Получаю курсы валют...")
        
        rates_data = await self.currency_api.get_all_rates("RUB")
        
        if rates_data:
            popular_currencies = self.currency_api.get_popular_currencies()
            message = f"💱 **Курсы валют относительно {rates_data['base']}**\n"
            message += f"📅 Дата: {rates_data['date']}\n\n"
            
            for currency, name in popular_currencies.items():
                if currency != "RUB" and currency in rates_data['rates']:
                    rate = rates_data['rates'][currency]
                    symbol = self.currency_api.get_currency_symbol(currency)
                    message += f"{symbol} **{currency}**: {rate:.4f}\n"
            
            await update.message.reply_text(message.strip())
        else:
            await update.message.reply_text(
                "❌ Не удалось получить курсы валют.\n"
                "Попробуйте позже."
            )
    
    async def _show_currency_rates_callback(self, query, context):
        """Показать курсы валют через callback"""
        await query.edit_message_text("💱 Получаю курсы валют...")
        
        rates_data = await self.currency_api.get_all_rates("RUB")
        
        if rates_data:
            popular_currencies = self.currency_api.get_popular_currencies()
            message = f"💱 **Курсы валют относительно {rates_data['base']}**\n"
            message += f"📅 Дата: {rates_data['date']}\n\n"
            
            for currency, name in popular_currencies.items():
                if currency != "RUB" and currency in rates_data['rates']:
                    rate = rates_data['rates'][currency]
                    symbol = self.currency_api.get_currency_symbol(currency)
                    message += f"{symbol} **{currency}**: {rate:.4f}\n"
            
            keyboard = [[InlineKeyboardButton("🔙 Назад", callback_data="currency_menu")]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text(
                message.strip(),
                reply_markup=reply_markup
            )
        else:
            await query.edit_message_text(
                "❌ Не удалось получить курсы валют.",
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("🔙 Назад", callback_data="currency_menu")
                ]])
            )
    
    async def _convert_currency(self, update: Update, context: ContextTypes.DEFAULT_TYPE, 
                               amount: float, from_currency: str, to_currency: str):
        """Конвертировать валюту"""
        await update.message.reply_text(
            f"🔄 Конвертирую {amount} {from_currency} в {to_currency}..."
        )
        
        conversion_data = await self.currency_api.convert_currency(amount, from_currency, to_currency)
        
        if conversion_data:
            from_symbol = self.currency_api.get_currency_symbol(from_currency)
            to_symbol = self.currency_api.get_currency_symbol(to_currency)
            
            message = f"""
🔄 **Конвертация валют**

💰 **{amount} {from_symbol}{from_currency}** = **{conversion_data['converted_amount']} {to_symbol}{to_currency}**

📊 Курс: 1 {from_currency} = {conversion_data['rate']:.4f} {to_currency}
📅 Дата: {conversion_data['date']}
            """.strip()
            
            await update.message.reply_text(message)
        else:
            await update.message.reply_text(
                f"❌ Не удалось конвертировать {amount} {from_currency} в {to_currency}.\n"
                "Проверьте правильность кодов валют."
            )
    
    async def _show_settings(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Показать настройки"""
        await self._show_settings_menu(update)
    
    def run(self):
        """Запуск бота"""
        if not config.BOT_TOKEN:
            logger.error("Не указан токен бота! Создайте файл .env с TELEGRAM_BOT_TOKEN")
            return
        
        # Создаем приложение
        self.application = Application.builder().token(config.BOT_TOKEN).build()
        
        # Добавляем обработчики команд
        self.application.add_handler(CommandHandler("start", self.start_command))
        self.application.add_handler(CommandHandler("help", self.help_command))
        self.application.add_handler(CommandHandler("weather", self.weather_command))
        self.application.add_handler(CommandHandler("forecast", self.forecast_command))
        self.application.add_handler(CommandHandler("news", self.news_command))
        self.application.add_handler(CommandHandler("search", self.search_news_command))
        self.application.add_handler(CommandHandler("currency", self.currency_command))
        self.application.add_handler(CommandHandler("convert", self.convert_command))
        self.application.add_handler(CommandHandler("settings", self.settings_command))
        
        # Добавляем обработчики callback и сообщений
        self.application.add_handler(CallbackQueryHandler(self.handle_callback))
        self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))
        
        # Запускаем бота
        logger.info("Расширенный бот запущен!")
        self.application.run_polling()

if __name__ == "__main__":
    bot = AdvancedWeatherBot()
    bot.run()
