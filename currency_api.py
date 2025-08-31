import aiohttp
import asyncio
from typing import Dict, Optional
import config

class CurrencyAPI:
    """Класс для работы с API курсов валют"""
    
    def __init__(self):
        self.api_key = getattr(config, 'CURRENCY_API_KEY', None)
        self.base_url = "https://api.exchangerate-api.com/v4"
        self.fallback_url = "https://api.exchangerate.host"
    
    async def get_exchange_rate(self, from_currency: str, to_currency: str) -> Optional[Dict]:
        """Получить курс обмена валют"""
        # Пробуем основной API
        if self.api_key:
            rate = await self._get_rate_from_primary_api(from_currency, to_currency)
            if rate:
                return rate
        
        # Если основной API не работает, используем fallback
        return await self._get_rate_from_fallback_api(from_currency, to_currency)
    
    async def get_all_rates(self, base_currency: str = "RUB") -> Optional[Dict]:
        """Получить все курсы относительно базовой валюты"""
        url = f"{self.fallback_url}/latest/{base_currency.upper()}"
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if response.status == 200:
                        data = await response.json()
                        return {
                            'base': data['base'],
                            'date': data['date'],
                            'rates': data['rates']
                        }
                    else:
                        return None
        except Exception as e:
            print(f"Ошибка при получении курсов валют: {e}")
            return None
    
    async def convert_currency(self, amount: float, from_currency: str, to_currency: str) -> Optional[Dict]:
        """Конвертировать сумму из одной валюты в другую"""
        rate_data = await self.get_exchange_rate(from_currency, to_currency)
        
        if rate_data:
            converted_amount = amount * rate_data['rate']
            return {
                'from_currency': from_currency.upper(),
                'to_currency': to_currency.upper(),
                'amount': amount,
                'converted_amount': round(converted_amount, 2),
                'rate': rate_data['rate'],
                'date': rate_data['date']
            }
        return None
    
    async def _get_rate_from_primary_api(self, from_currency: str, to_currency: str) -> Optional[Dict]:
        """Получить курс из основного API"""
        try:
            url = f"{self.base_url}/latest/{from_currency.upper()}"
            params = {'apikey': self.api_key}
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        if to_currency.upper() in data['rates']:
                            return {
                                'rate': data['rates'][to_currency.upper()],
                                'date': data['date']
                            }
            return None
        except Exception:
            return None
    
    async def _get_rate_from_fallback_api(self, from_currency: str, to_currency: str) -> Optional[Dict]:
        """Получить курс из fallback API"""
        try:
            url = f"{self.fallback_url}/convert"
            params = {
                'from': from_currency.upper(),
                'to': to_currency.upper(),
                'amount': 1
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        return {
                            'rate': data['result'],
                            'date': data['date']
                        }
            return None
        except Exception as e:
            print(f"Ошибка при получении курса из fallback API: {e}")
            return None
    
    def get_popular_currencies(self) -> Dict[str, str]:
        """Получить популярные валюты с названиями"""
        return {
            'USD': 'Доллар США',
            'EUR': 'Евро',
            'RUB': 'Российский рубль',
            'GBP': 'Фунт стерлингов',
            'JPY': 'Японская иена',
            'CNY': 'Китайский юань',
            'CHF': 'Швейцарский франк',
            'CAD': 'Канадский доллар',
            'AUD': 'Австралийский доллар',
            'TRY': 'Турецкая лира'
        }
    
    def get_currency_symbol(self, currency: str) -> str:
        """Получить символ валюты"""
        symbols = {
            'USD': '$',
            'EUR': '€',
            'RUB': '₽',
            'GBP': '£',
            'JPY': '¥',
            'CNY': '¥',
            'CHF': 'CHF',
            'CAD': 'C$',
            'AUD': 'A$',
            'TRY': '₺'
        }
        return symbols.get(currency.upper(), currency.upper())
