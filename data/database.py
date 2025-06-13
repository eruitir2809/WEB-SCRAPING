import sqlite3
import streamlit as st
import pandas as pd

def create_database():
    # Conexión a la base de datos (o creación si no existe)
    conex = sqlite3.connect('tfg.db')
    return conex

def create_cursor(conex):
    cursor = conex.cursor()
    return cursor

def create_table(cursor):
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS producto_scrapeado (
            pagina_web TEXT NOT NULL,
            url_producto TEXT PRIMARY KEY,
            fecha_consulta TIMESTAMP NOT NULL,
            titulo VARCHAR(255) NOT NULL,
            precio DECIMAL(10,2) NOT NULL,
            url_imagen TEXT
        );
    """)

def insert_products(cursor, conex, datos):
    cursor.execute("""
        INSERT OR IGNORE INTO producto_scrapeado 
        (pagina_web, url_producto, fecha_consulta, titulo, precio, url_imagen) 
        VALUES (?, ?, ?, ?, ?, ?)
    """, datos)
    conex.commit()


def read_products(cursor):
    cursor.execute("SELECT pagina_web, url_producto, fecha_consulta, titulo, precio, url_imagen FROM productos")
    return cursor.fetchall()

def close_conexion(conex):
    conex.close()
    
def load_datos_sql():
    st.subheader("📂 Productos almacenados en la base de datos")
    conex = create_database()
    cursor = create_cursor(conex)

    try:
        cursor.execute("SELECT pagina_web, url_producto, fecha_consulta, titulo, precio, url_imagen FROM producto_scrapeado")
        rows = cursor.fetchall()
        
        if rows:
            df = pd.DataFrame(rows, columns=["Pagina Web", "URL Producto", "Fecha", "Titulo", "Precio", "URL Imagen"])

            styled_df = df.style.set_properties(**{'text-align': 'left'}).set_table_styles([
                {'selector': 'th', 'props': [('text-align', 'left')]}
            ])
            st.dataframe(styled_df)
        else:
            st.warning("No hay productos en la base de datos.")
    except Exception as e:
        st.error(f"Error al leer la base de datos: {e}")
    finally:
        close_conexion(conex)