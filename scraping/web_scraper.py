import streamlit as st
from scraping.scrapeAmazon import (
    scrape_website,
    create_driver,
    clean_body_content,
    split_dom_content,
    extract_body_content,
    get_product_info,
    get_search_results,
    save_image,
    save_to_excel,
    ProductInfo
)
from model.parse import parse_with_ollama, eliminar_pensamientos
import pandas as pd
from datetime import datetime
import io


def web_scraper():
    pagina_web = st.selectbox(
        'Elige de qué página deseas extraer el contenido',
        ['Otro', 'Wallapop', 'Amazon', 'Ikea']
    )

    if pagina_web == 'Otro':
        url = st.text_input("Introduce la URL de un sitio web:")
        if st.button("Scrapear sitio"):
            st.write("Extrayendo información del sitio web con Selenium...")
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
                    st.subheader("Resultado del Modelo")
                    st.write(eliminar_pensamientos(result))

    else:
        st.title(f"{pagina_web} Producto Scraper")

        search_query = st.text_input(f"Introduce tu búsqueda de {pagina_web}:")

        if search_query:
            st.write(f"Resultados para: {search_query}")
            driver = create_driver()
            product_urls = get_search_results(pagina_web.lower(), driver, search_query)

            all_data = []
            if product_urls:
                for url in product_urls[:15]:
                    try:
                        info = get_product_info(driver, url, pagina_web.lower())
                        if isinstance(info, ProductInfo) and info.title:
                            data = {
                                'Fecha': datetime.now().strftime('%Y-%m-%d'),
                                'Titulo': info.title,
                                'Precio': info.price,
                                'URL Imagen': info.image_url,
                                'URL Producto': url,
                            }
                            all_data.append(data)
                            if info.image_url:
                                save_image(info.image_url, info.title, pagina_web.lower())
                    except Exception as e:
                        st.warning(f"Error al procesar {url}: {e}")
                driver.quit()

            if all_data:
                df = pd.DataFrame(all_data)
                st.session_state.product_df = df  # Guardar en sesión

                if "product_df" in st.session_state:
                    df = st.session_state.product_df
                    st.write('### Información de los productos')

                    vista = st.selectbox(
                        '¿Cómo quieres visualizar los productos?',
                        ['Tabla', 'Cascada']
                    )

                    if vista == 'Tabla':
                        styled_df = df.style.set_properties(**{'text-align': 'left'}).set_table_styles([
                            {'selector': 'th', 'props': [('text-align', 'left')]}
                        ])
                        st.dataframe(styled_df)
                    else:
                        for _, row in df.iterrows():
                            with st.container():
                                cols = st.columns([1, 4])
                                with cols[0]:
                                    st.image(row['URL Imagen'], width=120)
                                with cols[1]:
                                    st.markdown(f"### 📦 {row['Titulo']}")
                                    st.markdown(f"🗓️ **Fecha:** {row['Fecha']}")
                                    st.markdown(f"💰 **Precio:** {row['Precio']}")
                                    st.markdown(f"🔗 [Ver producto]({row['URL Producto']})")
                            st.markdown("---")

                    if st.button("Descargar"):
                        nombre_excel = f"{search_query}.xlsx"
                        output = io.BytesIO()

                        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                            df.to_excel(writer, index=False, sheet_name='Datos')

                        st.download_button(
                            label="📥 Descargar Excel",
                            data=output.getvalue(),
                            file_name=nombre_excel,
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                        )
            else:
                st.error("⚠️ No se encontraron productos válidos.")
                
            file_name = save_to_excel(all_data, pagina_web.lower())
            st.success(f"✅ Datos guardados correctamente en: `{file_name}`")        

