import logging
from proxy_sources import collect_all_proxies
from proxy_utils import save_proxies, send_proxies_to_channel
import asyncio

# Configure logging to both file and console
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bot.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

def main():
    proxies = collect_all_proxies()
    save_proxies(proxies)
    asyncio.run(send_proxies_to_channel(proxies))

if __name__ == "__main__":
    main()
