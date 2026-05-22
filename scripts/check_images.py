import sqlite3, os

db='instance/inventario.db'
if not os.path.exists(db):
    print('DB not found:', db)
    raise SystemExit(1)
conn=sqlite3.connect(db)
cur=conn.cursor()
cur.execute('SELECT id, nombre, image_filename, codigo_barras, stock, precio_venta FROM productos')
rows=cur.fetchall()
print('Encontrados', len(rows), 'productos')
for r in rows:
    id,nombre,img,codigo,stock,precio = r
    exists = None
    if img:
        path = os.path.join('static','img','products', img)
        exists = os.path.exists(path)
    print(id, nombre, '-> image:', img, 'file_exists:', exists)
conn.close()
