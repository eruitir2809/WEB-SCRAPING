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
def get_amazon_product_info(driver, url):
    driver.get(url)
    wait = WebDriverWait(driver, 10)

    def safe_get(by, value):
        try:
            element = wait.until(EC.presence_of_element_located((by, value)))
            return element.text.strip()
        except TimeoutException:
            return None

    def get_price():
        possible_classes = ["a-price-whole", "a-price", "a-offscreen"]
        for class_name in possible_classes:
            try:
                el = driver.find_element(By.CLASS_NAME, class_name)
                price = el.text.strip()
                if price:
                    return price
            except NoSuchElementException:
                continue
        return "Precio no disponible"

    title = safe_get(By.ID, "productTitle")

    try:
        image_element = wait.until(EC.presence_of_element_located((By.ID, "landingImage")))
        image_url = image_element.get_attribute("src")
    except TimeoutException:
        image_url = None

    price = get_price()
    availability = safe_get(By.ID, "availability")

    return title, image_url, price, availability

# -------------------- GET SEARCH RESULTS --------------------
def get_search_results(driver, query):
    search_url = f"https://www.amazon.es/s?k={query}"
    driver.get(search_url)
    wait = WebDriverWait(driver, 10)

    try:
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "s-result-item")))
    except TimeoutException:
        return []

    links = []
    elements = driver.find_elements(By.CSS_SELECTOR, "a.a-link-normal.s-no-outline")
    for el in elements:
        href = el.get_attribute("href")
        if href and "/dp/" in href:
            links.append(href.split("?")[0])
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
def save_to_excel(data):
    df = pd.DataFrame(data)
    file_name = "busquedas.xlsx"

    if os.path.exists(file_name):
        existing_df = pd.read_excel(file_name)
        df = pd.concat([existing_df, df], ignore_index=True)

    df.to_excel(file_name, index=False)
    return file_name

# -------------------- STREAMLIT APP --------------------
st.title("Amazon Producto Scraper")

search_query = st.text_input("Introduce tu búsqueda de Amazon:")

if search_query:
    st.write(f"Resultados para: {search_query}")
    driver = create_driver()
    product_urls = get_search_results(driver, search_query)

    if product_urls:
        all_data = []
        for url in product_urls[:30]:
            try:
                title, image_url, price, availability = get_amazon_product_info(driver, url)

                if title:
                    data = {
                        'Fecha': datetime.now().strftime('%Y-%m-%d'),
                        'Titulo': title,
                        'Precio': price,
                        'Disponibilidad': availability,
                        'URL Imagen': image_url,
                        'URL Producto': url
                    }
                    all_data.append(data)

                    if image_url:
                        save_image(image_url, title)
            except Exception as e:
                st.warning(f"Error al procesar {url}: {e}")

        driver.quit()

        if all_data:
            df = pd.DataFrame(all_data)
            st.write('### Información de los productos')
            st.dataframe(df.style.set_properties(**{'text-align': 'left'}).set_table_styles(
                [{'selector': 'th', 'props': [('text-align', 'left')]}]
            ))

            file_name = save_to_excel(all_data)
            st.success(f"Datos guardados en {file_name}")
        else:
            st.error("No se encontraron productos válidos.")
    else:
        st.error("No se encontraron productos para tu búsqueda.")
