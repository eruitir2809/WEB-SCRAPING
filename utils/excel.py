import streamlit as st
import pandas as pd
import time
import io
from model.parse import parse_with_ollama
from scraping.scrape import split_dom_content

def cargar_excel():
    st.subheader("Cargar archivo CSV o Excel")
    archivo_datos = st.file_uploader("Sube tu archivo:", type=["csv", "xlsx"])

    if archivo_datos:
        filename = archivo_datos.name
        file_extension = filename.split(".")[-1].lower()

        try:
            if file_extension == "csv":
                df = pd.read_csv(archivo_datos)
            elif file_extension == "xlsx":
                df = pd.read_excel(archivo_datos)
            else:
                st.error("Formato de archivo no soportado.")
                return
        except Exception as e:
            st.error(f"Error al leer el archivo: {e}")
            return

        st.session_state.excel_content = df
        st.subheader("Editar Datos")
        df_editado = st.data_editor(df, num_rows="dynamic")

        if st.button("Guardar y Descargar"):
            tiempo_actual = time.strftime("%Y%m%d-%H%M%S")
            base_nombre = filename.rsplit(".", 1)[0]

            if file_extension == "csv":
                nuevo_nombre = f"{base_nombre}_{tiempo_actual}.csv"
                csv_data = df_editado.to_csv(index=False, encoding="utf-8")
                st.download_button(
                    label="📥 Descargar CSV",
                    data=csv_data,
                    file_name=nuevo_nombre,
                    mime="text/csv"
                )

            elif file_extension == "xlsx":
                nuevo_nombre = f"{base_nombre}_{tiempo_actual}.xlsx"
                output = io.BytesIO()
                with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                    df_editado.to_excel(writer, index=False, sheet_name='Datos')
                st.download_button(
                    label="📥 Descargar Excel",
                    data=output.getvalue(),
                    file_name=nuevo_nombre,
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )

    if "excel_content" in st.session_state:
        st.subheader("Extraer Información con Modelo")
        parse_description = st.text_area("¿Qué información deseas extraer?")

        if st.button("Parsear Contenido"):
            if parse_description.strip():
                st.info("Dividiendo contenido en bloques para el modelo...")

                try:
                    dom_chunks = split_dom_content(st.session_state.excel_content)
                    st.write("Chunks creados:")
                    st.write(dom_chunks)

                    result = parse_with_ollama(dom_chunks, parse_description)
                    st.subheader("Resultado del Modelo")
                    st.write(result)

                except Exception as e:
                    st.error(f"Error al ejecutar el modelo: {e}")
            else:
                st.warning("Debes ingresar una descripción para extraer información.")
