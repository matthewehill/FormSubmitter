"""
Proxy rotation manager for enhanced stealth
Fetches and validates proxies for distributed testing
"""
import asyncio
import aiohttp
import logging
import random
from typing import Optional, List, Dict
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class ProxyManager:
    """Manages proxy rotation for enhanced stealth and distribution"""

    def __init__(self, enable_proxies: bool = False):
        self.enable_proxies = enable_proxies
        self.proxies: List[Dict] = []
        self.proxy_index = 0
        self.last_refresh = None
        self.refresh_interval = 300  # 5 minutes
        self.validated_proxies: List[Dict] = []

    async def refresh_proxies(self):
        """Fetch fresh proxies from multiple sources"""
        if not self.enable_proxies:
            logger.info("Proxy rotation disabled")
            return

        logger.info("Fetching fresh proxies...")

        all_proxies = []

        # Source 1: ProxyScrape
        proxies_1 = await self._fetch_from_proxyscrape()
        if proxies_1:
            all_proxies.extend(proxies_1)

        # Source 2: Free Proxy List
        proxies_2 = await self._fetch_from_free_proxy_list()
        if proxies_2:
            all_proxies.extend(proxies_2)

        if all_proxies:
            # Remove duplicates
            unique_proxies = list({p['proxy']: p for p in all_proxies}.values())
            self.proxies = unique_proxies
            self.last_refresh = datetime.now()
            logger.info(f"Loaded {len(self.proxies)} unique proxies")

            # Validate proxies in background
            asyncio.create_task(self._validate_proxies())
        else:
            logger.warning("No proxies fetched, will operate without proxies")

    async def _fetch_from_proxyscrape(self) -> List[Dict]:
        """Fetch proxies from ProxyScrape API"""
        try:
            url = "https://api.proxyscrape.com/v2/?request=displayproxies&protocol=http&timeout=10000&country=all&ssl=all&anonymity=elite"

            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=30)) as response:
                    if response.status == 200:
                        text = await response.text()
                        proxy_list = text.strip().split('\n')

                        proxies = []
                        for proxy in proxy_list:
                            if proxy and ':' in proxy:
                                proxies.append({
                                    'proxy': proxy.strip(),
                                    'source': 'proxyscrape'
                                })

                        logger.info(f"Fetched {len(proxies)} proxies from ProxyScrape")
                        return proxies
        except Exception as e:
            logger.error(f"Error fetching from ProxyScrape: {e}")

        return []

    async def _fetch_from_free_proxy_list(self) -> List[Dict]:
        """Fetch proxies from alternative source"""
        try:
            url = "https://www.proxy-list.download/api/v1/get?type=http"

            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=30)) as response:
                    if response.status == 200:
                        text = await response.text()
                        proxy_list = text.strip().split('\n')

                        proxies = []
                        for proxy in proxy_list:
                            if proxy and ':' in proxy:
                                proxies.append({
                                    'proxy': proxy.strip(),
                                    'source': 'proxy-list'
                                })

                        logger.info(f"Fetched {len(proxies)} proxies from proxy-list")
                        return proxies
        except Exception as e:
            logger.error(f"Error fetching from proxy-list: {e}")

        return []

    async def _validate_proxies(self):
        """Validate proxies by testing them"""
        logger.info(f"Validating {len(self.proxies)} proxies...")

        validated = []
        test_url = "http://httpbin.org/ip"

        # Test up to 50 proxies (to save time)
        sample = self.proxies[:50] if len(self.proxies) > 50 else self.proxies

        tasks = []
        for proxy_info in sample:
            tasks.append(self._test_proxy(proxy_info, test_url))

        results = await asyncio.gather(*tasks, return_exceptions=True)

        for i, result in enumerate(results):
            if result and not isinstance(result, Exception):
                validated.append(sample[i])

        self.validated_proxies = validated
        logger.info(f"Validated {len(validated)} working proxies")

    async def _test_proxy(self, proxy_info: Dict, test_url: str, timeout: int = 10) -> bool:
        """Test if a proxy is working"""
        try:
            proxy = f"http://{proxy_info['proxy']}"

            async with aiohttp.ClientSession() as session:
                async with session.get(
                    test_url,
                    proxy=proxy,
                    timeout=aiohttp.ClientTimeout(total=timeout)
                ) as response:
                    if response.status == 200:
                        return True
        except:
            pass

        return False

    async def get_proxy(self) -> Optional[Dict]:
        """Get next proxy in rotation"""
        if not self.enable_proxies:
            return None

        # Refresh if needed
        if not self.last_refresh or datetime.now() - self.last_refresh > timedelta(seconds=self.refresh_interval):
            await self.refresh_proxies()

        # Use validated proxies if available, otherwise use all
        proxy_pool = self.validated_proxies if self.validated_proxies else self.proxies

        if not proxy_pool:
            logger.warning("No proxies available")
            return None

        # Round-robin selection
        proxy_info = proxy_pool[self.proxy_index % len(proxy_pool)]
        self.proxy_index += 1

        return {
            'server': f"http://{proxy_info['proxy']}"
        }

    def get_random_proxy(self) -> Optional[Dict]:
        """Get a random proxy instead of round-robin"""
        if not self.enable_proxies:
            return None

        proxy_pool = self.validated_proxies if self.validated_proxies else self.proxies

        if not proxy_pool:
            return None

        proxy_info = random.choice(proxy_pool)
        return {
            'server': f"http://{proxy_info['proxy']}"
        }
