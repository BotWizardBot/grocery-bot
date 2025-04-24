import requests
from bs4 import BeautifulSoup
from typing import List, Dict
import re
import logging
from functools import lru_cache

logging.basicConfig(level=logging.INFO)

SYNONYMS = {
    "courgette": "zucchini",
    "aubergine": "eggplant",
    "mince": "ground beef",
    "biscuits": "cookies"
}

def normalize_query(query: str) -> str:
    for word, synonym in SYNONYMS.items():
        if word in query.lower():
            query = query.lower().replace(word, synonym)
    return query

def filter_products(products: List[Dict], include_tags: List[str] = [], exclude_brands: List[str] = []) -> List[Dict]:
    return [
        p for p in products
        if all(tag.lower() in p['name'].lower() for tag in include_tags)
        and not any(brand.lower() in p['name'].lower() for brand in exclude_brands)
    ]

def safe_request(url: str, headers: Dict[str, str]) -> str:
    try:
        response = requests.get(url, headers=headers, timeout=5)
        response.raise_for_status()
        return response.text
    except Exception as e:
        logging.warning(f"Failed to fetch {url}: {e}")
        return ""

@lru_cache(maxsize=128)
def scrape_tesco(item_name: str, tags: List[str] = [], exclude_brands: List[str] = []) -> List[Dict[str, float]]:
    item_name = normalize_query(item_name)
    headers = {"User-Agent": "Mozilla/5.0"}
    query = item_name.replace(" ", "+")
    url = f"https://www.tesco.com/groceries/en-GB/search?query={query}"
    html = safe_request(url, headers)
    soup = BeautifulSoup(html, "html.parser")
    results = []
    products = soup.select(".product-list--list-item")
    for product in products:
        title_tag = product.select_one(".styled__Text-sc-1xbujuz-0")
        price_tag = product.select_one(".value")
        if title_tag and price_tag:
            name = title_tag.text.strip()
            price_str = price_tag.text.strip()
            try:
                price = float(re.findall(r"\d+\.\d+", price_str)[0])
                results.append({"name": name, "price": price})
            except (IndexError, ValueError):
                continue
    return filter_products(results, tags, exclude_brands)

@lru_cache(maxsize=128)
def scrape_sainsburys(item_name: str, tags: List[str] = [], exclude_brands: List[str] = []) -> List[Dict[str, float]]:
    item_name = normalize_query(item_name)
    headers = {"User-Agent": "Mozilla/5.0"}
    query = item_name.replace(" ", "%20")
    url = f"https://www.sainsburys.co.uk/gol-ui/SearchResults/{query}"
    html = safe_request(url, headers)
    soup = BeautifulSoup(html, "html.parser")
    results = []
    products = soup.select(".productNameAndPromotions")
    for product in products:
        name_tag = product.select_one("h3 a")
        price_tag = product.find_next("p", class_="pricePerUnit")
        if name_tag and price_tag:
            name = name_tag.text.strip()
            price_match = re.search(r"\£(\d+\.\d+)", price_tag.text)
            if price_match:
                price = float(price_match.group(1))
                results.append({"name": name, "price": price})
    return filter_products(results, tags, exclude_brands)

@lru_cache(maxsize=128)
def scrape_asda(item_name: str, tags: List[str] = [], exclude_brands: List[str] = []) -> List[Dict[str, float]]:
    item_name = normalize_query(item_name)
    headers = {"User-Agent": "Mozilla/5.0"}
    query = item_name.replace(" ", "%20")
    url = f"https://groceries.asda.com/search/{query}"
    html = safe_request(url, headers)
    soup = BeautifulSoup(html, "html.parser")
    results = []
    products = soup.select(".co-product")
    for product in products:
        name_tag = product.select_one(".co-product__title")
        price_tag = product.select_one(".co-product__price .co-product__price--pence")
        if name_tag and price_tag:
            name = name_tag.text.strip()
            price_match = re.search(r"\d+\.\d+", price_tag.text)
            if price_match:
                price = float(price_match.group())
                results.append({"name": name, "price": price})
    return filter_products(results, tags, exclude_brands)

def scrape_all_stores(item_names: List[str], tags: List[str] = [], exclude_brands: List[str] = []) -> Dict[str, List[Dict]]:
    all_results = {"tesco": [], "sainsburys": [], "asda": []}
    for item in item_names:
        all_results["tesco"].extend(scrape_tesco(item, tags, exclude_brands))
        all_results["sainsburys"].extend(scrape_sainsburys(item, tags, exclude_brands))
        all_results["asda"].extend(scrape_asda(item, tags, exclude_brands))
    return all_results