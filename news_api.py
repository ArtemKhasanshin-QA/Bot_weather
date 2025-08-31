import aiohttp
import asyncio
from typing import Dict, Optional, List
import config

class NewsAPI:
    """Класс для работы с News API"""
    
    def __init__(self):
        self.api_key = getattr(config, 'NEWS_API_KEY', None)
        self.base_url = "https://newsapi.org/v2"
    
    async def get_top_headlines(self, country: str = "ru", category: str = "general", limit: int = 5) -> Optional[List[Dict]]:
        """Получить топ новостей по стране и категории"""
        if not self.api_key:
            return None
            
        url = f"{self.base_url}/top-headlines"
        params = {
            'country': country,
            'category': category,
            'apiKey': self.api_key,
            'pageSize': limit
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        return self._format_news(data.get('articles', []))
                    else:
                        return None
        except Exception as e:
            print(f"Ошибка при получении новостей: {e}")
            return None
    
    async def search_news(self, query: str, limit: int = 5) -> Optional[List[Dict]]:
        """Поиск новостей по запросу"""
        if not self.api_key:
            return None
            
        url = f"{self.base_url}/everything"
        params = {
            'q': query,
            'apiKey': self.api_key,
            'pageSize': limit,
            'sortBy': 'publishedAt',
            'language': 'ru'
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        return self._format_news(data.get('articles', []))
                    else:
                        return None
        except Exception as e:
            print(f"Ошибка при поиске новостей: {e}")
            return None
    
    def _format_news(self, articles: List[Dict]) -> List[Dict]:
        """Форматирование новостей"""
        formatted_news = []
        
        for article in articles:
            if article.get('title') and article.get('description'):
                formatted_news.append({
                    'title': article['title'],
                    'description': article['description'][:200] + "..." if len(article['description']) > 200 else article['description'],
                    'url': article.get('url', ''),
                    'published_at': article.get('publishedAt', ''),
                    'source': article.get('source', {}).get('name', 'Неизвестно')
                })
        
        return formatted_news
    
    def get_available_categories(self) -> List[str]:
        """Получить доступные категории новостей"""
        return [
            'general', 'business', 'technology', 'sports', 
            'entertainment', 'health', 'science'
        ]
    
    def get_available_countries(self) -> List[str]:
        """Получить доступные страны"""
        return ['ru', 'us', 'gb', 'de', 'fr', 'it', 'es', 'cn', 'jp']
