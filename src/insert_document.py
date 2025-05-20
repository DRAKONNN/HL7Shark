import os
import mimetypes
import mysql.connector
from datetime import datetime

# === CONFIGURACIÓN ===
DB_CONFIG = {
    "host": "localhost",  # Cambia esto si no es localhost
    "user": "openemr",    # Usuario de la base de datos
    "password": "openemr",  # Contraseña de la base de datos
    "database": "openemr"  # Nombre de la base de datos
}

# === PARÁMETROS ===
pid = 1004  # ID del paciente
image_path = "../public/images/Chill_Ghibli.jpg"  # Ruta local al archivo
category_id = 2  # ID de la categoría (usa SQL para buscarla si no la sabes)
upload_dir = "sites/default/documents/1004"  # Ruta donde se almacenan archivos
doc_dir = "/var/www/localhost/htdocs/openemr/" + upload_dir

# === FUNCIONES ===

def insert_document():
    # Leer archivo
    with open(image_path, "rb") as f:
        file_data = f.read()

    file_name = os.path.basename(image_path)
    mime_type = mimetypes.guess_type(image_path)[0] or 'application/octet-stream'
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Generar ruta en el sistema de archivos
    document_file_path = os.path.join(doc_dir, file_name)
    relative_path = os.path.join(upload_dir, file_name)

    # Guardar archivo en el filesystem de OpenEMR
    os.makedirs(os.path.dirname(document_file_path), exist_ok=True)
    with open(document_file_path, "wb") as f:
        f.write(file_data)

    # Insertar en tabla 'documents'
    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor()

    insert_doc_sql = """
    INSERT INTO documents (date, url, mimetype, size, name, foreign_id, docdate, owner)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """
    cursor.execute(insert_doc_sql, (
        now,
        relative_path,
        mime_type,
        len(file_data),
        file_name,
        pid,
        now,
        1  # owner (id del usuario que sube el archivo, puede ser 1)
    ))

    document_id = cursor.lastrowid

    # Insertar en tabla 'categories_to_documents'
    insert_ctd_sql = """
    INSERT INTO categories_to_documents (category_id, document_id)
    VALUES (%s, %s)
    """
    cursor.execute(insert_ctd_sql, (category_id, document_id))

    conn.commit()
    cursor.close()
    conn.close()

    print(f"Documento insertado con ID {document_id} y categoría {category_id}")

# === EJECUCIÓN ===
if __name__ == "__main__":
    insert_document()
