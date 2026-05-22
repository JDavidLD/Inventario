import os
import uuid
import sqlite3
from flask import Blueprint, render_template, redirect, url_for, request, flash, jsonify, current_app
from werkzeug.utils import secure_filename
from flask_login import login_required
from models.models import Producto, Proveedor
from app import db

productos_bp = Blueprint('productos', __name__, url_prefix='/productos')

ALLOWED_EXT = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
CATEGORIAS = ['Bebidas', 'Alimentos', 'Limpieza', 'Otros']


def ensure_producto_schema():
    database_url = current_app.config.get('SQLALCHEMY_DATABASE_URI', '')
    if not database_url.startswith('sqlite:///'):
        return
    path = database_url.replace('sqlite:///', '', 1)
    if not os.path.isabs(path):
        path = os.path.join(current_app.root_path, path)
    conn = None
    try:
        conn = sqlite3.connect(path)
        cursor = conn.cursor()
        cursor.execute("PRAGMA table_info(productos)")
        columns = {row[1]: row for row in cursor.fetchall()}
        if 'categoria' not in columns:
            cursor.execute("ALTER TABLE productos ADD COLUMN categoria VARCHAR(80)")
            conn.commit()
            cursor.execute("PRAGMA table_info(productos)")
            columns = {row[1]: row for row in cursor.fetchall()}
        if 'codigo_barras' in columns and columns['codigo_barras'][3] == 1:
            cursor.execute("PRAGMA foreign_keys=off")
            cursor.execute("BEGIN TRANSACTION")
            cursor.execute("CREATE TABLE productos_new (\n"
                           "\tid INTEGER NOT NULL, \n"
                           "\tcodigo_barras VARCHAR(50), \n"
                           "\tnombre VARCHAR(150) NOT NULL, \n"
                           "\tdescripcion VARCHAR(300), \n"
                           "\tprecio_compra FLOAT NOT NULL, \n"
                           "\tprecio_venta FLOAT NOT NULL, \n"
                           "\tstock INTEGER NOT NULL, \n"
                           "\tstock_minimo INTEGER NOT NULL, \n"
                           "\tproveedor_id INTEGER, \n"
                           "\tcategoria VARCHAR(80), \n"
                           "\tcreado_en DATETIME, \n"
                           "\timage_filename VARCHAR(200), \n"
                           "\tPRIMARY KEY (id), \n"
                           "\tUNIQUE (codigo_barras), \n"
                           "\tFOREIGN KEY(proveedor_id) REFERENCES proveedores (id)\n"
                           ")")
            cursor.execute("INSERT INTO productos_new (id, codigo_barras, nombre, descripcion, precio_compra, precio_venta, stock, stock_minimo, proveedor_id, categoria, creado_en, image_filename) "
                           "SELECT id, codigo_barras, nombre, descripcion, precio_compra, precio_venta, stock, stock_minimo, proveedor_id, categoria, creado_en, image_filename FROM productos")
            cursor.execute("DROP TABLE productos")
            cursor.execute("ALTER TABLE productos_new RENAME TO productos")
            cursor.execute("PRAGMA foreign_keys=on")
            conn.commit()
    except Exception:
        if conn:
            conn.rollback()
    finally:
        if conn:
            conn.close()

def save_image(file_storage):
    filename = secure_filename(file_storage.filename)
    if not filename:
        return None
    ext = filename.rsplit('.', 1)[-1].lower() if '.' in filename else ''
    if ext not in ALLOWED_EXT:
        return None
    folder = os.path.join(current_app.static_folder, 'img', 'products')
    os.makedirs(folder, exist_ok=True)
    new_name = f"{uuid.uuid4().hex}.{ext}"
    path = os.path.join(folder, new_name)
    file_storage.save(path)
    return new_name

@productos_bp.route('/')
@login_required
def index():
    ensure_producto_schema()
    q = request.args.get('q', '').strip()
    categoria = request.args.get('categoria', '').strip()
    query = Producto.query
    if q:
        query = query.filter(
            (Producto.nombre.ilike(f'%{q}%')) | (Producto.codigo_barras.ilike(f'%{q}%'))
        )
    if categoria:
        query = query.filter(Producto.categoria == categoria)
    productos = query.order_by(Producto.nombre).all()
    return render_template('productos/index.html', productos=productos, q=q, categoria=categoria, categorias=CATEGORIAS)

@productos_bp.route('/nuevo', methods=['GET', 'POST'])
@login_required
def nuevo():
    ensure_producto_schema()
    proveedores = Proveedor.query.order_by(Proveedor.nombre).all()
    if request.method == 'POST':
        codigo = request.form.get('codigo_barras', '').strip() or None
        if codigo and Producto.query.filter_by(codigo_barras=codigo).first():
            flash('Ya existe un producto con ese código de barras.', 'danger')
            return render_template('productos/form.html', proveedores=proveedores, categorias=CATEGORIAS)
        p = Producto(
            codigo_barras=codigo,
            nombre=request.form.get('nombre', '').strip(),
            descripcion=request.form.get('descripcion', '').strip(),
            categoria=request.form.get('categoria') or None,
            precio_compra=float(request.form.get('precio_compra', 0)),
            precio_venta=float(request.form.get('precio_venta', 0)),
            stock=int(request.form.get('stock', 0)),
            stock_minimo=int(request.form.get('stock_minimo', 5)),
            proveedor_id=request.form.get('proveedor_id') or None
        )
        # handle image upload
        img = request.files.get('imagen')
        if img and img.filename:
            saved = save_image(img)
            if saved:
                p.image_filename = saved
        db.session.add(p)
        db.session.commit()
        flash('Producto creado correctamente.', 'success')
        return redirect(url_for('productos.index'))
    return render_template('productos/form.html', proveedores=proveedores, producto=None, categorias=CATEGORIAS)

@productos_bp.route('/editar/<int:id>', methods=['GET', 'POST'])
@login_required
def editar(id):
    ensure_producto_schema()
    p = Producto.query.get_or_404(id)
    proveedores = Proveedor.query.order_by(Proveedor.nombre).all()
    if request.method == 'POST':
        codigo = request.form.get('codigo_barras', '').strip() or None
        existente = None
        if codigo:
            existente = Producto.query.filter_by(codigo_barras=codigo).first()
        if existente and existente.id != p.id:
            flash('Ya existe otro producto con ese código de barras.', 'danger')
            return render_template('productos/form.html', producto=p, proveedores=proveedores, categorias=CATEGORIAS)
        p.codigo_barras = codigo
        p.nombre = request.form.get('nombre', '').strip()
        p.descripcion = request.form.get('descripcion', '').strip()
        p.categoria = request.form.get('categoria') or None
        p.precio_compra = float(request.form.get('precio_compra', 0))
        p.precio_venta = float(request.form.get('precio_venta', 0))
        p.stock = int(request.form.get('stock', 0))
        p.stock_minimo = int(request.form.get('stock_minimo', 5))
        p.proveedor_id = request.form.get('proveedor_id') or None
        # handle image upload/replace
        img = request.files.get('imagen')
        if img and img.filename:
            saved = save_image(img)
            if saved:
                # remove old image
                if p.image_filename:
                    old_path = os.path.join(current_app.static_folder, 'img', 'products', p.image_filename)
                    try:
                        if os.path.exists(old_path):
                            os.remove(old_path)
                    except Exception:
                        pass
                p.image_filename = saved
        db.session.commit()
        flash('Producto actualizado.', 'success')
        return redirect(url_for('productos.index'))
    return render_template('productos/form.html', producto=p, proveedores=proveedores, categorias=CATEGORIAS)

@productos_bp.route('/eliminar/<int:id>', methods=['POST'])
@login_required
def eliminar(id):
    p = Producto.query.get_or_404(id)
    # delete image file if exists
    if p.image_filename:
        try:
            path = os.path.join(current_app.static_folder, 'img', 'products', p.image_filename)
            if os.path.exists(path):
                os.remove(path)
        except Exception:
            pass
    db.session.delete(p)
    db.session.commit()
    flash('Producto eliminado.', 'success')
    return redirect(url_for('productos.index'))

@productos_bp.route('/buscar_codigo')
@login_required
def buscar_codigo():
    codigo = request.args.get('codigo', '').strip()
    p = Producto.query.filter_by(codigo_barras=codigo).first()
    if p:
        return jsonify({'found': True, 'id': p.id, 'nombre': p.nombre,
                        'precio_venta': p.precio_venta, 'precio_compra': p.precio_compra,
                        'stock': p.stock,
                        'image_url': url_for('static', filename='img/products/' + p.image_filename) if p.image_filename else None})
    return jsonify({'found': False})

@productos_bp.route('/buscar_nombre')
@login_required
def buscar_nombre():
    q = request.args.get('q', '').strip()
    if not q:
        return jsonify([])
    resultados = Producto.query.filter(
        Producto.nombre.ilike(f'%{q}%')
    ).order_by(Producto.nombre).limit(12).all()
    return jsonify([{
        'id': p.id,
        'nombre': p.nombre,
        'codigo_barras': p.codigo_barras,
        'precio_venta': p.precio_venta,
        'precio_compra': p.precio_compra,
        'stock': p.stock
        ,
        'image_url': url_for('static', filename='img/products/' + p.image_filename) if p.image_filename else None
    } for p in resultados])


@productos_bp.route('/list_json')
@login_required
def list_json():
    try:
        page = int(request.args.get('page', 1))
    except Exception:
        page = 1
    per = int(request.args.get('per', 32))
    q = Producto.query.order_by(Producto.nombre).offset((page-1)*per).limit(per).all()
    total = Producto.query.count()
    return jsonify({
        'total': total,
        'page': page,
        'per': per,
        'items': [{
            'id': p.id,
            'nombre': p.nombre,
            'codigo_barras': p.codigo_barras,
            'precio_venta': p.precio_venta,
            'stock': p.stock,
            'image_url': url_for('static', filename='img/products/' + p.image_filename) if p.image_filename else None
        } for p in q]
    })
