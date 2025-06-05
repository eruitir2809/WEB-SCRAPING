import os
import re
import json
import pandas as pd
import requests
import streamlit as st
from datetime import datetime
from bs4 import BeautifulSoup

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from dataclasses import dataclass
from typing import Optional, List

# -------------------- SELENIUM SETUP --------------------
def create_driver():
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--window-size=1920,1080")
    options.add_argument('--lang=es-ES')
    return webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

# -------------------- GET PRODUCT INFO --------------------

@dataclass
class ProductInfo:
    title: Optional[str]
    image_url: Optional[str]
    price: str
    availability: Optional[str]

def safe_get(driver, wait, by, value) -> Optional[str]:
    try:
        element = wait.until(EC.presence_of_element_located((by, value)))
        return element.text.strip()
    except TimeoutException:
        return None

def extract_price(driver, class_names: List[str]) -> str:
    for class_name in class_names:
        try:
            el = driver.find_element(By.CLASS_NAME, class_name)
            price = el.text.strip()
            if price:
                return price
        except NoSuchElementException:
            continue
    return "Precio no disponible"

def get_product_info_amazon(driver, url: str) -> ProductInfo:
    driver.get(url)
    wait = WebDriverWait(driver, 5)

    title = safe_get(driver, wait, By.ID, "productTitle")
    price = extract_price(driver, ["a-price-whole", "a-price", "a-offscreen"])
    availability = safe_get(driver, wait, By.ID, "availability")

    try:
        image_element = wait.until(EC.presence_of_element_located((By.ID, "landingImage")))
        image_url = image_element.get_attribute("src")
    except TimeoutException:
        image_url = None

    return ProductInfo(title, image_url, price, availability)

def get_product_info_ikea(driver, url: str) -> ProductInfo:
    driver.get(url)
    wait = WebDriverWait(driver, 5)

    title = safe_get(driver, wait, By.CLASS_NAME, "pip-header-section__title--big")
    price = extract_price(driver, ["pip-price__integer", "pip-price__separator", "pip-price__decimal"])
    availability = safe_get(driver, wait, By.CLASS_NAME, "pip-status__label")

    try:
        image_element = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "pip-image")))
        image_url = image_element.get_attribute("src")
    except TimeoutException:
        image_url = None
    return ProductInfo(title, image_url, price, availability)

def get_product_info_vinted(driver, url):
    driver.get(url)
    wait = WebDriverWait(driver, 5)

    title = safe_get(driver, wait, By.ID, "productTitle")
    price = extract_price(driver, ["a-price-whole", "a-price", "a-offscreen"])
    availability = safe_get(driver, wait, By.ID, "availability")

    try:
        image_element = wait.until(EC.presence_of_element_located((By.ID, "landingImage")))
        image_url = image_element.get_attribute("src")
    except TimeoutException:
        image_url = None

    return ProductInfo(title, image_url, price, availability)

def get_product_info_wallapop(driver, url):
    driver.get(url)
    wait = WebDriverWait(driver, 5)

    title = safe_get(driver, wait, By.ID, "productTitle")
    price = extract_price(driver, ["a-price-whole", "a-price", "a-offscreen"])
    availability = safe_get(driver, wait, By.ID, "availability")

    try:
        image_element = wait.until(EC.presence_of_element_located((By.ID, "landingImage")))
        image_url = image_element.get_attribute("src")
    except TimeoutException:
        image_url = None

    return ProductInfo(title, image_url, price, availability)
    
def get_product_info(driver, url, site):
    if site == "amazon":
        return get_product_info_amazon(driver, url)
    elif site == "ikea":
        return get_product_info_ikea(driver, url)
    elif site == "vinted":
        return get_product_info_vinted(driver, url)
    elif site == "wallapop":
        return get_product_info_wallapop(driver, url)
    else:
        return "Sitio no soportado"

# -------------------- GET SEARCH RESULTS --------------------
def get_search_results(pagina_web, driver, query):
    urls = {
        "amazon": f"https://www.amazon.es/s?k={query}",
        "ikea": f"https://www.ikea.com/es/es/search/?q={query}",
        "vinted": f"https://www.vinted.es/catalog?search_text={query}",
        "wallapop": f"https://es.wallapop.com/search?source=search_box&keywords={query}",
    }

    if pagina_web not in urls:
        raise ValueError(f"No se reconoce la página web: {pagina_web}")

    url = urls[pagina_web]
    driver.get(url)
    wait = WebDriverWait(driver, 10)

    links = []

    if pagina_web == "amazon":
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "s-result-item")))
        elements = driver.find_elements(By.CSS_SELECTOR, "a.a-link-normal.s-no-outline")
        links = [el.get_attribute("href").split("?")[0] for el in elements if el.get_attribute("href") and "/dp/" in el.get_attribute("href")]

    elif pagina_web == "ikea":
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'plp-fragment-wrapper')))
        elements = driver.find_elements(By.CLASS_NAME, 'plp-product__image-link')
        links = [el.get_attribute("href").split("?")[0] for el in elements if el.get_attribute("href")]
        
        print(f"Buscando en IKEA con URL: {url}")
        print(f"Se encontraron {len(links)} productos")


    elif pagina_web == "vinted":
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'a[href^="/items/"]')))
        elements = driver.find_elements(By.CSS_SELECTOR, 'a[href^="/items/"]')
        links = ["https://www.vinted.es" + el.get_attribute("href").split("?")[0] for el in elements if el.get_attribute("href")]

    elif pagina_web == "wallapop":
        # Ya abriste driver.get arriba con URL corregida
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'a[href*="/item/"]')))
        elements = driver.find_elements(By.CSS_SELECTOR, 'a[href*="/item/"]')
        links = [el.get_attribute("href").split("?")[0] for el in elements if el.get_attribute("href")]

    return list(set(links))  # quitar duplicados


# -------------------- SAVE IMAGE --------------------
def save_image(image_url, product_name):
    folder = "imagenes"
    os.makedirs(folder, exist_ok=True)

    valid_filename = re.sub(r'[<>:"/\\|?*]', "", product_name)[:10]
    filepath = os.path.join(folder, valid_filename + '.jpg')

    base, ext = os.path.splitext(filepath)
    counter = 1
    while os.path.exists(filepath):
        filepath = f"{base}_{counter}{ext}"
        counter += 1

    response = requests.get(image_url, stream=True)
    if response.status_code == 200:
        with open(filepath, 'wb') as file:
            for chunk in response.iter_content(1024):
                file.write(chunk)
        return filepath
    return None

# -------------------- SAVE TO EXCEL --------------------
def save_to_excel(data, pagina_web):
    df = pd.DataFrame(data)
    file_name = f"busquedas_{pagina_web}.xlsx"

    if os.path.exists(file_name):
        existing_df = pd.read_excel(file_name)
        df = pd.concat([existing_df, df], ignore_index=True)

    df.to_excel(file_name, index=False)
    return file_name