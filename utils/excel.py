import streamlit as st
import pandas as pd
import time
import io
from model.parse import parse_with_ollama, delete_thoughts

def load_excel():
    st.subheader("Cargar archivo CSV o Excel")
    uploaded_file = st.file_uploader("Sube tu archivo:", type=["csv", "xlsx"])

    if uploaded_file:
        filename = uploaded_file.name
        file_extension = filename.split(".")[-1].lower()

        try:
            if file_extension == "csv":
                df = pd.read_csv(uploaded_file)
            elif file_extension == "xlsx":
                df = pd.read_excel(uploaded_file)
            else:
                st.error("Formato de archivo no soportado.")
                return
        except Exception as e:
            st.error(f"Error al leer el archivo: {e}")
            return

        st.subheader("Editar Datos")
        edited_df = st.data_editor(df, num_rows="dynamic")

        if st.button("Guardar y Descargar"):
            current_time = time.strftime("%Y%m%d-%H%M%S")
            base_name = filename.rsplit(".", 1)[0]

            if file_extension == "csv":
                new_file_name= f"{base_name}_{current_time}.csv"
                csv_data = edited_df.to_csv(index=False, encoding="utf-8")
                st.download_button(
                    label="📥 Descargar CSV",
                    data=csv_data,
                    file_name=new_file_name,
                    mime="text/csv"
                )

            elif file_extension == "xlsx":
                new_file_name= f"{base_name}_{current_time}.xlsx"
                output = io.BytesIO()
                with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                    edited_df.to_excel(writer, index=False, sheet_name='Datos')
                st.download_button(
                    label="📥 Descargar Excel",
                    data=output.getvalue(),
                    file_name=new_file_name,
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
       
        st.session_state.excel_content = edited_df


    if "excel_content" in st.session_state:
        st.subheader("Extraer Información con Modelo")
        parse_description = st.text_area("¿Qué información deseas extraer?")

        if st.button("Parsear Contenido"):
            if parse_description.strip():
                st.info("Dividiendo contenido en bloques para el modelo...")

                try:
  
                    result = parse_with_ollama([st.session_state.excel_content], parse_description)
                    st.subheader("Resultado del Modelo")
                    st.write(delete_thoughts(result))

                except Exception as e:
                    st.error(f"Error al ejecutar el modelo: {e}")
            else:
                st.warning("Debes ingresar una descripción para extraer información.")
