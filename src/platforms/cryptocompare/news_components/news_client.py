"""
CryptoCompare News API Client
Handles direct API interactions with the CryptoCompare news service.
"""
import asyncio
from typing import Dict, List, Any, Optional

import aiohttp

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.config.protocol import ConfigProtocol
from src.logger.logger import Logger
from src.utils.decorators import retry_api_call


class CryptoCompareNewsClient:
    """Handles direct API communication with CryptoCompare news service."""
    
    def __init__(self, logger: Logger, config: "ConfigProtocol"):
        self.logger = logger
        self.config = config
    
    @retry_api_call(max_retries=3)
    async def fetch_news(
        self,
        session: Optional[aiohttp.ClientSession] = None,
        api_categories: Optional[List[Dict[str, Any]]] = None,
        target_coin: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Fetch crypto news from CryptoCompare API

        Args:
            session: Optional aiohttp session to reuse
            api_categories: Optional list of API categories
            target_coin: Optional coin being analyzed (e.g., "PEPE", "BTC") to prioritize in categories
        """
        articles = []

        # Add optional query parameters based on categories
        categories_param = ""
        if api_categories:
            # 🔥 DYNAMIC: Get important categories and add target coin if provided
            important_categories = self._get_important_categories(target_coin)

            important_cats = [cat['categoryName'] for cat in api_categories
                              if cat.get('categoryName', '') in important_categories]
            if important_cats:
                categories_param = f"&categories={','.join(important_cats[:5])}"
                self.logger.debug(f"Fetching news with priority categories: {important_cats[:5]}")
                
        url = f"{self.config.RAG_NEWS_API_URL}{categories_param}"
        
        # Use provided session if available, otherwise create temporary one
        session_to_use = session or aiohttp.ClientSession()
        use_temp_session = session is None
        
        try:
            # Use ClientTimeout for aiohttp requests
            client_timeout = aiohttp.ClientTimeout(total=45)
            async with session_to_use.get(url, timeout=client_timeout) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    if data and "Data" in data:
                        articles = data["Data"]
                        self.logger.debug(f"Fetched {len(articles)} news articles from CryptoCompare")
                else:
                    self.logger.error(f"News API request failed with status {resp.status}")
        except asyncio.TimeoutError:
            self.logger.error("Timeout fetching news from CryptoCompare")
        except Exception as e:
            self.logger.error(f"Error fetching CryptoCompare news: {e}")
        finally:
            # Only close if we created a temporary session
            if use_temp_session:
                await session_to_use.close()
        
        return articles
    
    @staticmethod
    def _get_important_categories(target_coin: Optional[str] = None) -> List[str]:
        """Get list of important categories to prioritize in API requests

        Args:
            target_coin: Optional coin ticker (e.g., "PEPE", "SOL") to add to priority categories

        Returns:
            List of category names to prioritize
        """
        # Base important categories
        base_categories = ["BTC", "ETH", "DeFi", "NFT", "Layer 2", "Stablecoin", "Altcoin"]

        # 🔥 DYNAMIC COIN CATEGORY: Add target coin if provided and not already in list
        if target_coin:
            target_coin_upper = target_coin.upper()
            if target_coin_upper not in base_categories:
                # Insert target coin at the beginning for highest priority
                return [target_coin_upper] + base_categories

        return base_categories
