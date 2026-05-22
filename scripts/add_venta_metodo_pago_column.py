import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parents[1] / 'instance' / 'inventario.db'

if not DB_PATH.exists():
    raise SystemExit(f"Base de datos no encontrada: {DB_PATH}")

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

try:
    cursor.execute("ALTER TABLE venta ADD COLUMN metodo_pago TEXT DEFAULT 'Efectivo';")
    conn.commit()
    print('Columna metodo_pago agregada correctamente.')
except sqlite3.OperationalError as exc:
    if 'duplicate column name' in str(exc).lower():
        print('La columna metodo_pago ya existe en la tabla venta.')
    else:
        raise
finally:
    conn.close()
