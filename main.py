import streamlit as st
from PIL import Image
from utils.documentos import load_documents
from utils.excel import load_excel
from scraping.web_scraper import web_scraper
from data.database import (
    create_database,
    create_cursor,
    create_table,
    close_conexion,
    load_datos_sql
   )


img = Image.open('assets/logo.png')
st.set_page_config(page_title='Proyecto TFG', page_icon=img)

def main():
    st.title("Web Scraper")
    menu = ["Web Scraper", "Leer Documentos", "Leer Excel", "Ver Base de Datos"]
    choice = st.sidebar.selectbox("Menú", menu)

    if choice == "Web Scraper":
        web_scraper()
                    
    elif choice == "Leer Documentos":
        load_documents()
                
    elif choice == "Leer Excel":
        load_excel()
        
    elif choice == "Ver Base de Datos":
        load_datos_sql()

if __name__ == '__main__':
    conex = create_database()
    cursor = create_cursor(conex)
    create_table(cursor)
    close_conexion(conex)
    main()
