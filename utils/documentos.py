import streamlit as st
import time
from PyPDF2 import PdfReader
import docx2txt
from model.parse import parse_with_ollama

def cargar_documentos():
    st.subheader("Cargar y Leer Documentos")
    archivo_datos = st.file_uploader("Sube un documento:", type=["pdf", "docx", "txt"])

    def leer_pdf(file):
        try:
            pdf_reader = PdfReader(file)
            return "\n".join(page.extract_text() or "" for page in pdf_reader.pages).strip()
        except Exception as e:
            st.error(f"Error al leer PDF: {e}")
            return ""

    def leer_docx(file):
        try:
            return docx2txt.process(file)
        except Exception as e:
            st.error(f"Error al leer DOCX: {e}")
            return ""

    def leer_txt(file):
        try:
            return file.read().decode("utf-8")
        except Exception as e:
            st.error(f"Error al leer TXT: {e}")
            return ""

    if archivo_datos:
        texto = ""
        tipo = archivo_datos.type

        if tipo == "application/pdf":
            texto = leer_pdf(archivo_datos)
        elif tipo == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
            texto = leer_docx(archivo_datos)
        elif tipo == "text/plain":
            texto = leer_txt(archivo_datos)
        else:
            st.error("Formato de archivo no soportado.")
            return

        if texto:
            st.session_state.excel_content = texto
            st.subheader("Contenido Extraído (Editable)")
            texto_editado = st.text_area("Texto", value=texto, height=300, key="editor")

            if st.button("Guardar y Descargar"):
                tiempo_actual = time.strftime("%Y%m%d-%H%M%S")
                nuevo_nombre = f"documento_editado_{tiempo_actual}.txt"
                st.download_button(
                    label="📥 Descargar Texto",
                    data=texto_editado,
                    file_name=nuevo_nombre,
                    mime="text/plain"
                )

        if "excel_content" in st.session_state:
            st.subheader("Extraer Información con Modelo")
            parse_description = st.text_area("¿Qué información deseas extraer?")

            if st.button("Parsear Contenido"):
                if parse_description.strip():
                    st.info("Procesando texto con el modelo...")

                    try:
                        resultado = parse_with_ollama([st.session_state.excel_content], parse_description)
                        st.subheader("Resultado del Modelo")
                        st.write(resultado)

                    except Exception as e:
                        st.error(f"Error al ejecutar el modelo: {e}")
                else:
                    st.warning("Debes ingresar una descripción para extraer información.")
