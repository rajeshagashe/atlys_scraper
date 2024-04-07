import httpx
import asyncio
import re

from typing import Callable, Union
from bs4 import BeautifulSoup
from urllib.parse import urljoin

from ..models.dental_stall import DentalStallProdpuctCatalogue

async def scrape_website(data: dict[str, any]):
    url = data.get("url")
    start_page = data.get("start_page")
    end_page = data.get("end_page")
    proxy_string = data.get("proxy_string")
    scraper = scraper_factory(data.get('url'))()
    # not considering dynamic loading for new page
    scrapped_data = []
    for i in range(start_page, end_page+1):
        if i > 1:
            page_url = urljoin(url, scraper.pagination_path.replace('page_no', str(i)))
        else:
            page_url = url
        response = await fetch_data(page_url, proxy_string, data.get('retries'))
        if response.status_code == 404: #all pages scrapped
            break
        if not response.is_success:
            continue # if response is not sucessful after all retries moving to the next page
        html_content = response.text
        soup = BeautifulSoup(html_content, "html.parser")
        await scraper.scrape(soup)
        scrapped_data += await scraper.scrape(soup)
    
    await scraper.save(scrapped_data)

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
        self.scrapped_data_count = 0
        self.updated_data_count = 0

    async def scrape(self, soup: BeautifulSoup):
        product_elements = soup.find_all("li", class_="product")
        scrapped_data = []
    
        for product_element in product_elements:
            name = product_element.find("h2", class_="woo-loop-product__title").text.strip()
    
            price_element = product_element.find("span", class_="woocommerce-Price-amount amount")
            price = price_element.text.strip() if price_element else "N/A"
    
            image_element = product_element.find("img", class_="attachment-woocommerce_thumbnail size-woocommerce_thumbnail")
            image_url = image_element["data-lazy-src"] if image_element else "N/A"
    
            self.scrapped_data_count += 1

            entry = self.model()
            entry.product_title = name
            entry.product_price = float(price.replace('\u20b9', '')) #removing rupee symbol
            entry.path_to_image = image_url
            scrapped_data.append(entry)
        return scrapped_data

    async def save(self, scrapped_data: list[DentalStallProdpuctCatalogue]):
        for product in scrapped_data:
            if not compare_dicts(fetch_cache(product.product_title), product.model_dump()):
                upsert_cache()
                await product.upsert()
                self.updated_data_count += 1


def compare_dicts(dict1, dict2): #move to utils
    if set(dict1.keys()) != set(dict2.keys()):
        return False
    
    for key in dict1:
        if dict1[key] != dict2[key]:
            return False
    
    return True

def fetch_cache(id): #move to utils
    return {}

def upsert_cache(): #move to utils
    pass