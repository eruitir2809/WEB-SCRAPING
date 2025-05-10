import streamlit as st
from PyPDF2 import PdfReader
import docx2txt

def cargar_documentos():
    st.subheader("Leer Documentos")
    archivo_doc = st.file_uploader("Subir documento", type=["pdf", "docx", "txt"])
    if st.button("Procesar"):
        if archivo_doc.type == "text/plain":
            texto = str(archivo_doc.read(), "utf-8")
            st.text(texto)
                
        elif archivo_doc.type == "application/pdf":
            texto = leer_pdf(archivo_doc)
            st.text(texto)
                
        elif archivo_doc.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
            texto = docx2txt.process(archivo_doc)
            st.text(texto)
                

def leer_pdf(file):
    pdfReader = PdfReader(file)
    count = len(pdfReader.pages)
    todo_el_texto = ""
    for i in range(count):
        pagina = pdfReader.pages[i]
        todo_el_texto += pagina.extract_text()
    return todo_el_texto
