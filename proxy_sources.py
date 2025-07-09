import json
import requests
import logging
from bs4 import BeautifulSoup
import os
import re

REQUEST_TIMEOUT = int(os.getenv('REQUEST_TIMEOUT', 30))

logger = logging.getLogger(__name__)

def load_sources():
    with open('sources.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    json_urls = data.get('json_urls', [])
    telegram_channels = data.get('telegram_channels', [])
    return json_urls, telegram_channels

def fetch_proxies_from_json_urls(urls):
    all_links = []
    for url in urls:
        try:
            # Skip SSL verification only for mtpro.xyz
            if 'mtpro.xyz' in url:
                response = requests.get(url, timeout=REQUEST_TIMEOUT, verify=False)
                logger.warning(f"Skipping SSL verification for {url} (insecure)")
            else:
                response = requests.get(url, timeout=REQUEST_TIMEOUT)
            if response.status_code == 200:
                try:
                    data = response.json()
                    count = 0
                    if isinstance(data, list):
                        for entry in data:
                            if all(k in entry for k in ('host', 'port', 'secret')):
                                link = f"tg://proxy?server={entry['host']}&port={entry['port']}&secret={entry['secret']}"
                                all_links.append(link)
                                count += 1
                            else:
                                link = entry.get('link') or entry.get('url') or entry.get('proxy')
                                if link:
                                    all_links.append(link)
                                    count += 1
                        logger.info(f"Fetched {count} proxies from mtpro.xyz or similar: {url}")
                    elif isinstance(data, dict):
                        proxies = data.get('proxies', [])
                        for proxy in proxies:
                            link = proxy.get('link') or proxy.get('url') or proxy.get('proxy')
                            if link:
                                all_links.append(link)
                                count += 1
                        logger.info(f"Fetched {count} proxies from dict-based source: {url}")
                except Exception as e:
                    logger.error(f'JSON parsing failed for {url}: {e}. Falling back to regex extraction.')
                    # Fallback: extract proxy links from text using regex
                    text = response.text
                    # Regex for tg://proxy and https://t.me/proxy links
                    pattern = r'(tg://proxy\?[^\s"\']+|https://t\.me/proxy\?[^\s"\']+)'
                    found_links = re.findall(pattern, text)
                    all_links.extend(found_links)
                    logger.info(f"Extracted {len(found_links)} proxy links from text fallback: {url}")
            else:
                logger.error(f'Failed to fetch data from URL: {url}')
        except Exception as e:
            logger.error(f'Error fetching/parsing JSON from {url}: {e}')
    return all_links

def fetch_proxies_from_telegram_channel(url):
    proxies = []
    try:
        response = requests.get(url, timeout=REQUEST_TIMEOUT)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            proxy_elements = soup.find_all('a', string='پروکسی')
            proxies = [element.get('href') for element in proxy_elements]
            logger.info(f"Fetched {len(proxies)} proxies from Telegram channel: {url}")
        else:
            logger.error(f"Failed to fetch data from URL: {url}")
    except Exception as e:
        logger.error(f"Error fetching/parsing Telegram channel {url}: {e}")
    return proxies

def clean_proxy_link(link):
    """
    Normalize proxy links by:
    - Removing leading '@'
    - Replacing '&amp;' with '&'
    - Stripping whitespace
    """
    if not isinstance(link, str):
        return link
    link = link.strip()
    if link.startswith('@'):
        link = link[1:]
    link = link.replace('&amp;', '&')
    return link

def collect_all_proxies():
    json_urls, telegram_channels = load_sources()
    proxies = []
    # Add proxies from Telegram channels first
    for url in telegram_channels:
        proxies.extend(fetch_proxies_from_telegram_channel(url))
    # Then add proxies from JSON URLs
    proxies.extend(fetch_proxies_from_json_urls(json_urls))
    # Remove duplicates while preserving order and clean links
    seen = set()
    unique_proxies = []
    for proxy in proxies:
        cleaned = clean_proxy_link(proxy)
        if cleaned and cleaned not in seen:
            seen.add(cleaned)
            unique_proxies.append(cleaned)
    return unique_proxies 