import streamlit as st
import pandas as pd
from parse import parse_with_ollama
from scrape import split_dom_content

def cargar_excel():
    st.subheader("Leer Excel")
    archivo_datos = st.file_uploader("Subir CSV o Excel", type=["csv", "xlsx"])
    if st.button("Procesar"):
        if archivo_datos.type == "text/csv":
            df = pd.read_csv(archivo_datos)
            st.session_state.excel_content = df  # Guarda el contenido en sesión
            
        elif archivo_datos.type == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet":
            df = pd.read_excel(archivo_datos)
            st.session_state.excel_content = df  # Guarda el contenido en sesión

        else:
            df = pd.DataFrame()
        st.dataframe(df)
        
    if "excel_content" in st.session_state:
        parse_description = st.text_area("Quieres sacar información?")  # Instrucciones del usuario
        if st.button("Parse Content"):
            if parse_description:
                st.write("Parsing the content")
            
                dom_chunks = split_dom_content(st.session_state.excel_content)  # Divide en bloques
                st.write("Chunks creados para el modelo:")
                st.write(dom_chunks)

                try:
                    result = parse_with_ollama(dom_chunks, parse_description)
                    st.write(result)
                except Exception as e:
                    st.error(f"Error al ejecutar el modelo: {e}")

                st.write(result)  # Muestra el resultado final