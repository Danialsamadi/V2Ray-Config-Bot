#!/usr/bin/env python3
import os
import re
import json
import requests
import logging
import pycountry_convert as pc
from bs4 import BeautifulSoup
from datetime import datetime, timezone, timedelta
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=getattr(logging, os.getenv('LOG_LEVEL', 'INFO'))
)
logger = logging.getLogger(__name__)

# Configuration from environment variables
PROXY_SOURCES = os.getenv('PROXY_SOURCES', 'github,freeproxylist').split(',')
MAX_PROXIES_PER_SOURCE = int(os.getenv('MAX_PROXIES_PER_SOURCE', 20))
ENABLE_COUNTRY_CATEGORIZATION = os.getenv('ENABLE_COUNTRY_CATEGORIZATION', 'true').lower() == 'true'
IPAPI_ENDPOINT = os.getenv('IPAPI_ENDPOINT', 'https://ipapi.co/{ip}/json/')

def fetch_proxies_from_sources():
    """Fetch proxies from multiple sources."""
    proxies = []
    
    # Source 1: Telegram Proxies Collector (GitHub)
    if 'github' in PROXY_SOURCES:
        try:
            github_url = "https://raw.githubusercontent.com/soroushmirzaei/telegram-proxies-collector/main/proxies"
            response = requests.get(github_url)
            if response.status_code == 200:
                proxies.extend(response.text.splitlines()[:MAX_PROXIES_PER_SOURCE])
        except Exception as e:
            logger.error(f"Error fetching from GitHub source: {e}")
    
    # Source 2: Free Proxy Lists
    if 'freeproxylist' in PROXY_SOURCES:
        try:
            free_proxy_url = "https://free-proxy-list.net/"
            response = requests.get(free_proxy_url)
            soup = BeautifulSoup(response.text, 'html.parser')
            proxy_table = soup.find('table', {'id': 'proxylisttable'})
            
            if proxy_table:
                for row in proxy_table.find_all('tr')[1:MAX_PROXIES_PER_SOURCE+1]:
                    cols = row.find_all('td')
                    if len(cols) >= 2:
                        ip = cols[0].text.strip()
                        port = cols[1].text.strip()
                        proxy = f"{ip}:{port}"
                        proxies.append(proxy)
        except Exception as e:
            logger.error(f"Error fetching from free proxy list: {e}")
    
    return list(set(proxies))  # Remove duplicates

def categorize_proxies_by_country(proxies):
    """Categorize proxies by country using IP geolocation."""
    if not ENABLE_COUNTRY_CATEGORIZATION:
        logger.info("Country categorization is disabled")
        return
    
    countries_dir = './countries'
    os.makedirs(countries_dir, exist_ok=True)
    
    for proxy in proxies:
        try:
            # Basic IP extraction (assumes IPv4)
            match = re.match(r'(\d+\.\d+\.\d+\.\d+)', proxy)
            if not match:
                continue
            
            ip = match.group(1)
            
            # Use requests to get geolocation
            geo_response = requests.get(IPAPI_ENDPOINT.format(ip=ip))
            if geo_response.status_code == 200:
                geo_data = geo_response.json()
                country_code = geo_data.get('country_code', 'UNKNOWN')
                
                # Create country directory
                country_dir = os.path.join(countries_dir, country_code)
                os.makedirs(country_dir, exist_ok=True)
                
                # Write proxy to country-specific file
                country_proxy_file = os.path.join(country_dir, 'proxies')
                with open(country_proxy_file, 'a') as f:
                    f.write(f"{proxy}\n")
        except Exception as e:
            logger.error(f"Error categorizing proxy {proxy}: {e}")

def save_proxies(proxies):
    """Save proxies to a file with timestamp."""
    current_datetime = datetime.now(tz=timezone(timedelta(hours=3, minutes=30)))
    
    # Main proxies file
    with open('./proxies', 'w') as f:
        f.write(f"# Proxy List Generated: {current_datetime.strftime('%Y-%m-%d %H:%M:%S %Z')}\n")
        f.write(f"# Total Proxies: {len(proxies)}\n")
        for proxy in proxies:
            f.write(f"{proxy}\n")
    
    # IPv4 Proxies
    ipv4_proxies = [p for p in proxies if re.match(r'\d+\.\d+\.\d+\.\d+', p)]
    with open('./layers/ipv4', 'w') as f:
        f.write(f"# IPv4 Proxy List Generated: {current_datetime.strftime('%Y-%m-%d %H:%M:%S %Z')}\n")
        f.write(f"# Total IPv4 Proxies: {len(ipv4_proxies)}\n")
        for proxy in ipv4_proxies:
            f.write(f"{proxy}\n")
    
    # IPv6 Proxies
    ipv6_proxies = [p for p in proxies if ':' in p and not re.match(r'\d+\.\d+\.\d+\.\d+', p)]
    with open('./layers/ipv6', 'w') as f:
        f.write(f"# IPv6 Proxy List Generated: {current_datetime.strftime('%Y-%m-%d %H:%M:%S %Z')}\n")
        f.write(f"# Total IPv6 Proxies: {len(ipv6_proxies)}\n")
        for proxy in ipv6_proxies:
            f.write(f"{proxy}\n")

def main():
    """Main function to collect and save proxies."""
    # Ensure layers directory exists
    os.makedirs('./layers', exist_ok=True)
    
    # Fetch proxies
    proxies = fetch_proxies_from_sources()
    
    # Categorize proxies by country
    categorize_proxies_by_country(proxies)
    
    # Save proxies
    save_proxies(proxies)
    
    logger.info(f"Successfully collected {len(proxies)} proxies")

if __name__ == "__main__":
    main() 