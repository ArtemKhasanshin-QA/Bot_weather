import aiohttp
import asyncio
from typing import Dict, Optional, List
import config

class WeatherAPI:
    """Класс для работы с OpenWeatherMap API"""
    
    def __init__(self):
        self.api_key = config.OPENWEATHER_API_KEY
        self.base_url = config.OPENWEATHER_BASE_URL
        self.language = config.DEFAULT_LANGUAGE
        self.units = config.DEFAULT_UNITS
    
    async def get_current_weather(self, city: str) -> Optional[Dict]:
        """Получить текущую погоду в городе"""
        if not self.api_key:
            return None
            
        url = f"{self.base_url}{config.WEATHER_ENDPOINT}"
        params = {
            'q': city,
            'appid': self.api_key,
            'lang': self.language,
            'units': self.units
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        return self._format_current_weather(data)
                    else:
                        return None
        except Exception as e:
            print(f"Ошибка при получении погоды: {e}")
            return None
    
    async def get_forecast(self, city: str) -> Optional[Dict]:
        """Получить прогноз погоды на 5 дней"""
        if not self.api_key:
            return None
            
        url = f"{self.base_url}{config.FORECAST_ENDPOINT}"
        params = {
            'q': city,
            'appid': self.api_key,
            'lang': self.language,
            'units': self.units
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        return self._format_forecast(data)
                    else:
                        return None
        except Exception as e:
            print(f"Ошибка при получении прогноза: {e}")
            return None
    
    def _format_current_weather(self, data: Dict) -> Dict:
        """Форматирование данных о текущей погоде"""
        try:
            weather = data['weather'][0]
            main = data['main']
            wind = data.get('wind', {})
            
            return {
                'city': data['name'],
                'country': data['sys']['country'],
                'description': weather['description'].capitalize(),
                'temperature': round(main['temp']),
                'feels_like': round(main['feels_like']),
                'humidity': main['humidity'],
                'pressure': main['pressure'],
                'wind_speed': wind.get('speed', 0),
                'icon': weather['icon']
            }
        except KeyError as e:
            print(f"Ошибка форматирования погоды: {e}")
            return None
    
    def _format_forecast(self, data: Dict) -> Dict:
        """Форматирование данных прогноза погоды"""
        try:
            city = data['city']['name']
            country = data['city']['country']
            forecasts = []
            
            # Группируем прогнозы по дням (берем прогноз на 12:00 каждого дня)
            daily_forecasts = {}
            
            for item in data['list']:
                date = item['dt_txt'].split(' ')[0]
                time = item['dt_txt'].split(' ')[1]
                
                # Берем прогноз на полдень (12:00)
                if time == "12:00:00" and len(daily_forecasts) < 5:
                    weather = item['weather'][0]
                    main = item['main']
                    
                    daily_forecasts[date] = {
                        'date': date,
                        'description': weather['description'].capitalize(),
                        'temperature': round(main['temp']),
                        'humidity': main['humidity'],
                        'icon': weather['icon']
                    }
            
            return {
                'city': city,
                'country': country,
                'forecasts': list(daily_forecasts.values())
            }
        except KeyError as e:
            print(f"Ошибка форматирования прогноза: {e}")
            return None
    
    def get_weather_emoji(self, icon: str) -> str:
        """Получить эмодзи для погоды по коду иконки"""
        emoji_map = {
            '01d': '☀️',  # ясно днем
            '01n': '🌙',  # ясно ночью
            '02d': '⛅',  # малооблачно днем
            '02n': '☁️',  # малооблачно ночью
            '03d': '☁️',  # облачно
            '03n': '☁️',
            '04d': '☁️',  # пасмурно
            '04n': '☁️',
            '09d': '🌧️',  # дождь
            '09n': '🌧️',
            '10d': '🌦️',  # дождь с солнцем
            '10n': '🌧️',
            '11d': '⛈️',  # гроза
            '11n': '⛈️',
            '13d': '❄️',  # снег
            '13n': '❄️',
            '50d': '🌫️',  # туман
            '50n': '🌫️'
        }
        return emoji_map.get(icon, '🌤️')
