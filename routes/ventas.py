from flask import Blueprint, render_template, redirect, url_for, request, flash, jsonify
from flask_login import login_required
from models.models import Venta, DetalleVenta, Producto
from app import db
from datetime import datetime
from datetime import timedelta

ventas_bp = Blueprint('ventas', __name__, url_prefix='/ventas')

@ventas_bp.route('/')
@login_required
def index():
    # Filtrar por fecha (parámetro ?date=YYYY-MM-DD). Por defecto muestra ventas del día actual.
    date_str = request.args.get('date')
    if date_str:
        try:
            selected_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        except Exception:
            selected_date = datetime.now().date()
    else:
        selected_date = datetime.now().date()

    start_dt = datetime.combine(selected_date, datetime.min.time())
    end_dt = start_dt + timedelta(days=1)
    ventas = Venta.query.filter(Venta.fecha >= start_dt, Venta.fecha < end_dt).order_by(Venta.fecha.desc()).all()

    # Estadísticas del mes (para la tarjeta de resumen)
    month_start = datetime(selected_date.year, selected_date.month, 1)
    if selected_date.month == 12:
        month_end = datetime(selected_date.year + 1, 1, 1)
    else:
        month_end = datetime(selected_date.year, selected_date.month + 1, 1)
    month_ventas = Venta.query.filter(Venta.fecha >= month_start, Venta.fecha < month_end).all()
    month_total = sum((v.total or 0) for v in month_ventas)
    month_gan = sum((v.ganancia or 0) for v in month_ventas)

    return render_template('ventas/index.html', ventas=ventas, now=datetime.now(), selected_date=selected_date,
                           month_total=month_total, month_gan=month_gan)

@ventas_bp.route('/nueva', methods=['GET', 'POST'])
@login_required
def nueva():
    productos = Producto.query.order_by(Producto.nombre).all()
    if request.method == 'POST':
        notas = request.form.get('notas', '').strip()
        metodo_pago = request.form.get('metodo_pago', 'Efectivo').strip() or 'Efectivo'
        producto_ids = request.form.getlist('producto_id[]')
        cantidades = request.form.getlist('cantidad[]')
        precios = request.form.getlist('precio_unitario[]')

        es_cajero = request.form.get('cajero') == '1'

        if not producto_ids:
            if es_cajero:
                return jsonify(ok=False, error='Agrega al menos un producto.')
            flash('Agrega al menos un producto.', 'danger')
            return render_template('ventas/form.html', productos=productos)

        venta = Venta(notas=notas, metodo_pago=metodo_pago)
        db.session.add(venta)
        total = 0
        ganancia_total = 0
        errores = []
        for pid, cant, precio in zip(producto_ids, cantidades, precios):
            cant = int(cant)
            precio = float(precio)
            prod = Producto.query.get(int(pid))
            if prod.stock < cant:
                errores.append(f'Stock insuficiente para "{prod.nombre}" (disponible: {prod.stock})')
                continue
            detalle = DetalleVenta(venta=venta, producto_id=int(pid),
                                   cantidad=cant, precio_unitario=precio,
                                   precio_compra=prod.precio_compra)
            db.session.add(detalle)
            prod.stock -= cant
            subtotal = cant * precio
            ganancia = cant * (precio - prod.precio_compra)
            total += subtotal
            ganancia_total += ganancia

        if errores:
            db.session.rollback()
            if es_cajero:
                return jsonify(ok=False, error=' | '.join(errores))
            for e in errores:
                flash(e, 'danger')
            return render_template('ventas/form.html', productos=productos)

        venta.total = round(total, 2)
        venta.ganancia = round(ganancia_total, 2)
        db.session.commit()
        if es_cajero:
            return jsonify(ok=True)
        flash('Venta registrada correctamente.', 'success')
        return redirect(url_for('ventas.index'))
    return render_template('ventas/form.html', productos=productos)

@ventas_bp.route('/detalle/<int:id>')
@login_required
def detalle(id):
    venta = Venta.query.get_or_404(id)
    return render_template('ventas/detalle.html', venta=venta)

@ventas_bp.route('/cajero')
@login_required
def cajero():
    productos = Producto.query.filter(Producto.stock > 0).order_by(Producto.nombre).all()
    return render_template('ventas/cajero.html', productos=productos)
