import streamlit as st
from PIL import Image
from scrape import (
    scrape_website,
    split_dom_content,
    clean_body_content,
    extract_body_content,
)
from parse import parse_with_ollama
import pandas as pd

def web_scraper():
    javascript = st.checkbox("La pagina usa javascript para cargar datos?")
    paginas_web = st.selectbox(
        'Elige de que pagina deseas extraer el contenido',
        ['Otro', 'Wallapop', 'Amazon', 'Ikea', 'Vinted']
        )
    url = st.text_input("Enter a Website URL: ")

    if st.button("Scrape Site"):
        st.write("Scraping the website")
        result = scrape_website(url)  # Scrapea el HTML de la URL
        
        body_content = extract_body_content(result)  # Extrae el contenido dentro de `<body>`
        cleaned_content = clean_body_content(body_content)  # Limpia scripts y estilos
    
        st.session_state.dom_content = cleaned_content  # Guarda el contenido en sesión
    
        with st.expander("View DOM Content"):
            st.text_area("DOM Content", cleaned_content, height=300)  # Muestra contenido procesado

    if "dom_content" in st.session_state:
        parse_description = st.text_area("Descrive what you want to parse?")  # Instrucciones del usuario
        if st.button("Parse Content"):
            if parse_description:
                st.write("Parsing the content")
            
                dom_chunks = split_dom_content(st.session_state.dom_content)  # Divide en bloques
                result = parse_with_ollama(dom_chunks, parse_description)  # Procesa con modelo AI
                st.write(result)  # Muestra el resultado final
            
                    #img = Image.open("imagen.png")
                    #st.image(img, use_column_width=True)
                    #st.image("https://picsum.photos/800")