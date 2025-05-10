import streamlit as st
from PIL import Image
from documentos import cargar_documentos
from excel import cargar_excel
from web_scraper import web_scraper

img = Image.open('logo.png')
st.set_page_config(page_title='Proyecto TFG', page_icon=img)

def main():
    st.title("AI Web Scraper")
    menu = ["AI Web Scraper", "Leer Documentos", "Leer Excel"]
    eleccion = st.sidebar.selectbox("Menú", menu)

    if eleccion == "AI Web Scraper":
        web_scraper()
                    
    elif eleccion == "Leer Documentos":
        cargar_documentos()
                
    elif eleccion == "Leer Excel":
        cargar_excel()

if __name__ == '__main__':
    main()