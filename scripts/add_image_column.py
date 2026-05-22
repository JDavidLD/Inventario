#!/usr/bin/env python3
"""Añade la columna image_filename a la tabla productos en inventario.db si no existe.
Uso: desde la raíz del proyecto:
    python scripts/add_image_column.py
"""
import os
import sqlite3
import sys

DB_FILE = os.environ.get('DATABASE_FILE', 'inventario.db')

if not os.path.exists(DB_FILE):
    print(f"ERROR: No se encontró la base de datos '{DB_FILE}'. Asegúrate de ejecutar esto desde la carpeta del proyecto o establece DATABASE_FILE.")
    sys.exit(1)

conn = sqlite3.connect(DB_FILE)
cur = conn.cursor()

cur.execute("PRAGMA table_info(productos);")
cols = [r[1] for r in cur.fetchall()]
if 'image_filename' in cols:
    print('La columna image_filename ya existe en la tabla productos. No se realizaron cambios.')
    conn.close()
    sys.exit(0)

try:
    cur.execute("ALTER TABLE productos ADD COLUMN image_filename VARCHAR(200);")
    conn.commit()
    print('Columna image_filename añadida correctamente.')
except sqlite3.OperationalError as e:
    print('Error al añadir la columna:', e)
    print('Si la tabla tiene restricciones complejas, considera hacer un dump y recrear la tabla con la nueva columna.')
finally:
    conn.close()
