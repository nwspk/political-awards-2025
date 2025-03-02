import asyncio
import aiohttp
import pandas as pd
import whois
from bs4 import BeautifulSoup
from typing import Dict, Any, Tuple
from datetime import datetime
from urllib.parse import urlparse
import logging
from concurrent.futures import ThreadPoolExecutor

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"

class WebsiteEnricher:
    def __init__(self, max_concurrent: int = 10):
        self.max_concurrent = max_concurrent
        self.session = None
        self.total_processed = 0
        self.successful_fetches = 0
        self.failed_fetches = 0

    async def __aenter__(self):
        timeout = aiohttp.ClientTimeout(total=30)
        self.session = aiohttp.ClientSession(timeout=timeout)
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()

    def is_github_url(self, url: str) -> bool:
        parsed = urlparse(url)
        return parsed.netloc.lower() in ['github.com', 'www.github.com']

    async def get_page_data(self, url: str) -> Tuple[Dict[str, Any], str]:
        try:
            logger.info(f"Fetching URL: {url}")
            async with self.session.get(url) as response:
                data = {
                    'status_code': response.status,
                    'content_type': response.headers.get('content-type'),
                    'server': response.headers.get('server')
                }
                
                if response.status == 200:
                    self.successful_fetches += 1
                    html = await response.text()
                    soup = BeautifulSoup(html, 'html.parser')
                    logger.info(f"Successfully fetched {url} - Status: {response.status}")
                    
                    data.update({
                        'title': soup.title.string.strip() if soup.title else None,
                        'description': (soup.find('meta', {'name': 'description'}) or {}).get('content'),
                        'og_title': (soup.find('meta', {'property': 'og:title'}) or {}).get('content'),
                    })
                    return data, html
                else:
                    self.failed_fetches += 1
                    logger.warning(f"Failed to fetch {url} - Status: {response.status}")
                return data, ""
        except Exception as e:
            self.failed_fetches += 1
            logger.error(f"Error fetching {url}: {str(e)}")
            return {'status_code': None, 'error': str(e)}, ""

    def get_domain_info(self, url: str) -> Dict[str, Any]:
        try:
            domain = urlparse(url).netloc
            logger.info(f"Getting WHOIS info for domain: {domain}")
            w = whois.whois(domain)
            return {
                'creation_date': w.creation_date[0] if isinstance(w.creation_date, list) else w.creation_date,
                'registrar': w.registrar
            }
        except Exception as e:
            logger.error(f"WHOIS error for {url}: {str(e)}")
            return {}

    async def process_url(self, url: str) -> Dict[str, Any]:
        self.total_processed += 1
        if self.is_github_url(url):
            logger.info(f"Skipping GitHub URL: {url}")
            return {'url': url, 'type': 'github', 'skipped': True}

        data = {'url': url, 'type': 'website', 'skipped': False}
        
        metadata, html = await self.get_page_data(url)
        data.update(metadata)
        data['html_content'] = html
        
        with ThreadPoolExecutor() as executor:
            domain_info = await asyncio.get_event_loop().run_in_executor(
                executor, self.get_domain_info, url
            )
            data.update(domain_info)
            
        return data

    async def process_urls(self, csv_path: str) -> pd.DataFrame:
        df = pd.read_csv(csv_path)
        urls = df['url'].tolist()
        
        logger.info(f"Starting processing of {len(urls)} URLs...")
        
        results = []
        for i in range(0, len(urls), self.max_concurrent):
            chunk = urls[i:i + self.max_concurrent]
            chunk_results = await asyncio.gather(
                *[self.process_url(url) for url in chunk]
            )
            results.extend(chunk_results)
            
            processed = min(i + self.max_concurrent, len(urls))
            non_github = sum(1 for r in results if not r.get('skipped', False))
            logger.info(f"Progress: {processed}/{len(urls)} URLs ({non_github} websites)")
            logger.info(f"Success rate: {self.successful_fetches}/{self.total_processed} ({self.successful_fetches/self.total_processed*100:.1f}%)")
        
        enriched_df = pd.DataFrame(results)
        output_path = f'enriched_websites_{datetime.now():%Y%m%d_%H%M%S}.csv'
        enriched_df.to_csv(output_path, index=False)
        logger.info(f"Results saved to {output_path}")
        
        return enriched_df

async def main():
    async with WebsiteEnricher() as enricher:
        df = await enricher.process_urls('data/projects.csv')
        logger.info("\nFinal Summary:")
        logger.info(f"Total URLs processed: {len(df)}")
        logger.info(f"GitHub repositories skipped: {df['skipped'].sum()}")
        logger.info(f"Websites processed: {(~df['skipped']).sum()}")
        logger.info(f"Successful fetches: {enricher.successful_fetches}")
        logger.info(f"Failed fetches: {enricher.failed_fetches}")
        logger.info(f"Success rate: {enricher.successful_fetches/enricher.total_processed*100:.1f}%")

if __name__ == "__main__":
    asyncio.run(main())