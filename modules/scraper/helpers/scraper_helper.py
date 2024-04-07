import httpx
import asyncio
import json

from typing import Callable, Union
from bs4 import BeautifulSoup
from urllib.parse import urljoin

from ..models.dental_stall import DentalStallProdpuctCatalogue
from modules.records.models.records import Records
from utils import utils

async def scrape_website(data: dict[str, any]):
    url = data.get("url")
    start_page = data.get("start_page")
    end_page = data.get("end_page")
    proxy_string = data.get("proxy_string")
    scraper = scraper_factory(data.get('url'))()
    # not considering dynamic loading for new page
    scraped_data = []
    for i in range(start_page, end_page+1):
        if i > 1:
            page_url = urljoin(url, scraper.pagination_path.replace('page_no', str(i)))
        else:
            page_url = url
        response = await fetch_data(page_url, proxy_string, data.get('retries'))
        if response.status_code == 404: #all pages scraped
            break
        if not response.is_success:
            continue # if response is not sucessful after all retries moving to the next page
        html_content = response.text
        soup = BeautifulSoup(html_content, "html.parser")
        scraped_data += await scraper.scrape(soup)
    
    await scraper.save(scraped_data)
    record = Records()
    record.scraped_count = scraper.scraped_data_count
    record.updated_count = scraper.updated_data_count
    record.save()

async def fetch_data(url: str, proxy: Union[str, None] = None, retry_options: dict[str, any] = {}) -> str: #move to utils
        status_code = 500
        retries = retry_options.get('count', 1)
        delay = retry_options.get('interval', 1)
        
        proxy_options = {"https://": proxy} if proxy else None

        # httpx does not provide ready-made retry options so doing a simple implementation
        async with httpx.AsyncClient(proxies=proxy_options) as client:
            while status_code in [i for i in range(500, 600)]:
                if retries < retry_options.get('count', 1): # not delaying for 1st attempt
                    await asyncio.sleep(delay)
                response = await client.get(url)
                status_code = response.status_code
                retries -= 1
                if retries == 0:
                    break

            return response
    
def scraper_factory(arg: str) -> Callable:
    if arg[-1] != '/':
        arg += '/'
    switch = {
        "https://dentalstall.com/shop/": DentalStall,
    }
    if switch.get(arg, False) == False:
        raise Exception("Unknown website url")
    return switch.get(arg)

class DentalStall():
    pagination_path = "page/page_no/"

    def __init__(self):
        self.model = DentalStallProdpuctCatalogue
        self.scraped_data_count = 0
        self.updated_data_count = 0

    async def scrape(self, soup: BeautifulSoup):
        product_elements = soup.find_all("li", class_="product")
        scraped_data = []
        for product_element in product_elements:
            name = product_element.find("h2", class_="woo-loop-product__title").text.strip()
    
            price_element = product_element.find("span", class_="woocommerce-Price-amount amount")
            price = price_element.text.strip() if price_element else "N/A"
    
            image_element = product_element.find("img", class_="attachment-woocommerce_thumbnail size-woocommerce_thumbnail")
            image_url = image_element["data-lazy-src"] if image_element else "N/A"
    
            entry = self.model()
            entry.product_title = name
            entry.product_price = float(price.replace('\u20b9', '')) #removing rupee symbol
            entry.path_to_image = image_url
            scraped_data.append(entry)
            self.scraped_data_count += 1
        return scraped_data

    async def save(self, scraped_data: list[DentalStallProdpuctCatalogue]):
        for product in scraped_data:
            cache = await utils.fetch_cache(product.path_to_image)
            if not utils.compare_dicts(cache, product.model_dump()):
                await utils.upsert_cache(product.path_to_image, product.model_dump())
                await product.upsert()
                self.updated_data_count += 1