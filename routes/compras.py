from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required
from models.models import Compra, DetalleCompra, Producto, Proveedor
from app import db
from datetime import datetime

compras_bp = Blueprint('compras', __name__, url_prefix='/compras')

@compras_bp.route('/')
@login_required
def index():
    compras = Compra.query.order_by(Compra.fecha.desc()).all()
    return render_template('compras/index.html', compras=compras, now=datetime.utcnow())

@compras_bp.route('/nueva', methods=['GET', 'POST'])
@login_required
def nueva():
    proveedores = Proveedor.query.order_by(Proveedor.nombre).all()
    productos = Producto.query.order_by(Producto.nombre).all()
    if request.method == 'POST':
        proveedor_id = request.form.get('proveedor_id') or None
        notas = request.form.get('notas', '').strip()
        producto_ids = request.form.getlist('producto_id[]')
        cantidades = request.form.getlist('cantidad[]')
        precios = request.form.getlist('precio_unitario[]')

        if not producto_ids:
            flash('Agrega al menos un producto.', 'danger')
            return render_template('compras/form.html', proveedores=proveedores, productos=productos)

        compra = Compra(proveedor_id=proveedor_id, notas=notas)
        db.session.add(compra)
        total = 0
        for pid, cant, precio in zip(producto_ids, cantidades, precios):
            cant = int(cant)
            precio = float(precio)
            detalle = DetalleCompra(compra=compra, producto_id=int(pid),
                                    cantidad=cant, precio_unitario=precio)
            db.session.add(detalle)
            # Update stock and purchase price
            prod = Producto.query.get(int(pid))
            prod.stock += cant
            prod.precio_compra = precio
            total += cant * precio
        compra.total = round(total, 2)
        db.session.commit()
        flash('Compra registrada y stock actualizado.', 'success')
        return redirect(url_for('compras.index'))
    return render_template('compras/form.html', proveedores=proveedores, productos=productos)

@compras_bp.route('/detalle/<int:id>')
@login_required
def detalle(id):
    compra = Compra.query.get_or_404(id)
    return render_template('compras/detalle.html', compra=compra)
