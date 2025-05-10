from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import requests

"""
def scrape_website(website):
    options = Options()
    options.add_argument("--headless")  # Opcional, si no querés que se abra el navegador
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36")

    driver = webdriver.Chrome(service=Service(), options=options)
    driver.get(website)
    html = driver.page_source
    driver.quit()
    return html"""
def scrape_website(url):
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/123.0.0.0 Safari/537.36"
        ),
        "Accept-Language": "es-ES,es;q=0.9,en;q=0.8",
    }

    response = requests.get(url, headers=headers, timeout=10)
    response.raise_for_status()  # Lanza error si no es 200 OK

    soup = BeautifulSoup(response.text, "html.parser")
    return soup.prettify()  # Devuelve todo el HTML con buena indentación

def extract_body_content(html_content):
    soup = BeautifulSoup(html_content, "html.parser")
    body_content = soup.body
    return str(body_content) if body_content else ""

def clean_body_content(body_content):
    soup = BeautifulSoup(body_content, "html.parser")
    for script_or_style in soup(["script", "style"]):
        script_or_style.extract()
    cleaned_content = soup.get_text(separator="\n")
    return "\n".join(line.strip() for line in cleaned_content.splitlines() if line.strip())

def split_dom_content(dom_content, max_length=6000):
    return [dom_content[i:i + max_length] for i in range(0, len(dom_content), max_length)]

