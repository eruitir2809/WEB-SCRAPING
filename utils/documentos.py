import streamlit as st
import time
from PyPDF2 import PdfReader
import docx2txt
from model.parse import parse_with_ollama, delete_thoughts

def load_documents():
    st.subheader("Cargar y Leer Documentos")
    data_file = st.file_uploader("Sube un documento:", type=["pdf", "docx", "txt"])

    def read_pdf(file):
        try:
            pdf_reader = PdfReader(file)
            return "\n".join(page.extract_text() or "" for page in pdf_reader.pages).strip()
        except Exception as e:
            st.error(f"Error al leer PDF: {e}")
            return ""

    def read_docx(file):
        try:
            return docx2txt.process(file)
        except Exception as e:
            st.error(f"Error al leer DOCX: {e}")
            return ""

    def read_txt(file):
        try:
            return file.read().decode("utf-8")
        except Exception as e:
            st.error(f"Error al leer TXT: {e}")
            return ""

    if data_file:
        text = ""
        tipo = data_file.type

        if tipo == "application/pdf":
            text = read_pdf(data_file)
        elif tipo == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
            text = read_docx(data_file)
        elif tipo == "text/plain":
            text = read_txt(data_file)
        else:
            st.error("Formato de archivo no soportado.")
            return

        if text:
            st.subheader("Contenido Extraído (Editable)")
            edited_text = st.text_area("text", value=text, height=300, key="editor")

            if st.button("Guardar y Descargar"):
                current_time = time.strftime("%Y%m%d-%H%M%S")
                new_name = f"documento_editado_{current_time}.txt"
                st.download_button(
                    label="📥 Descargar text",
                    data=edited_text,
                    file_name=new_name,
                    mime="text/plain"
                )
            
            st.session_state.doc_content = edited_text

        if "doc_content" in st.session_state:
            st.subheader("Extraer Información con Modelo")
            parse_description = st.text_area("¿Qué información deseas extraer?")

            if st.button("Parsear Contenido"):
                if parse_description.strip():
                    st.info("Procesando text con el modelo...")

                    try:
                        resultado = parse_with_ollama([st.session_state.doc_content], parse_description)
                        st.info
                        st.subheader("Resultado del Modelo")
                        st.write(delete_thoughts(resultado))

                    except Exception as e:
                        st.error(f"Error al ejecutar el modelo: {e}")
                else:
                    st.warning("Debes ingresar una descripción para extraer información.")
