import streamlit as st
from PIL import Image
from scraping.scrapeAmazon import (
    create_driver,
    get_product_info,
    get_search_results,
    save_image,
    save_to_excel,
    ProductInfo
)
from model.parse import parse_with_ollama
import pandas as pd
from datetime import datetime

# Función principal de la app
def web_scraper():
    pagina_web = st.selectbox(
        'Elige de qué página deseas extraer el contenido',
        ['Amazon', 'Wallapop', 'Amazon', 'Ikea', 'Vinted']
    )

    if pagina_web == 'Otro':
        """
        # Scraping general de otras páginas
        url = st.text_input("Introduce la URL de un sitio web:")

        if st.button("Scrapear sitio"):
            st.write("Extrayendo información del sitio web...")
            result = scrape_website(url)

            body_content = extract_body_content(result)
            cleaned_content = clean_body_content(body_content)

            st.session_state.dom_content = cleaned_content

            with st.expander("Ver contenido del DOM"):
                st.text_area("DOM Content", cleaned_content, height=300)

        if "dom_content" in st.session_state:
            parse_description = st.text_area("¿Qué deseas extraer del contenido?")
            if st.button("Procesar contenido"):
                if parse_description:
                    st.write("Procesando el contenido con IA...")
                    dom_chunks = split_dom_content(st.session_state.dom_content)
                    result = parse_with_ollama(dom_chunks, parse_description)
                    st.write(result)

                    # Opcional: mostrar una imagen decorativa
                    # img = Image.open("imagen.png")
                    # st.image(img, use_column_width=True)
                    # st.image("https://picsum.photos/800")"""
    else:
        # -------------------- STREAMLIT APP --------------------
        st.title(f"{pagina_web} Producto Scraper")

        search_query = st.text_input(f"Introduce tu búsqueda de {pagina_web}:")

        if search_query:
            st.write(f"Resultados para: {search_query}")
            driver = create_driver()
            product_urls = get_search_results(pagina_web.lower(), driver, search_query)

            if product_urls:
                all_data = []
                for url in product_urls[:30]:
                    try:
                        info = get_product_info(driver, url, pagina_web.lower())
                        if isinstance(info, ProductInfo):
                            title, image_url, price, availability = info.title, info.image_url, info.price, info.availability

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

                    file_name = save_to_excel(all_data, pagina_web.lower())
                    st.success(f"Datos guardados en {file_name}")
                else:
                    st.error("No se encontraron productos válidos.")
            else:
                st.error("No se encontraron productos para tu búsqueda.")

