from flask import Blueprint, render_template
from flask_login import login_required
from models.models import Producto, Venta, Compra
from app import db
from sqlalchemy import func
from datetime import datetime, timedelta

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/')
@login_required
def index():
    total_productos = Producto.query.count()
    productos_bajo_stock = Producto.query.filter(Producto.stock <= Producto.stock_minimo).all()

    hoy = datetime.now().date()

    # ── Hoy ──────────────────────────────────────────────────────
    ingresos_hoy = db.session.query(func.sum(Venta.total)).filter(
        func.date(Venta.fecha) == hoy
    ).scalar() or 0

    gastos_hoy = db.session.query(func.sum(Compra.total)).filter(
        func.date(Compra.fecha) == hoy
    ).scalar() or 0

    balance_hoy = ingresos_hoy - gastos_hoy

    # ── Totales históricos ────────────────────────────────────────
    total_ingresos = db.session.query(func.sum(Venta.total)).scalar() or 0
    total_gastos   = db.session.query(func.sum(Compra.total)).scalar() or 0
    balance_total  = total_ingresos - total_gastos

    # ── Gráfico últimos 7 días: ingresos vs gastos vs balance ────
    grafico = []
    for i in range(6, -1, -1):
        dia = hoy - timedelta(days=i)
        ing = db.session.query(func.sum(Venta.total)).filter(
            func.date(Venta.fecha) == dia
        ).scalar() or 0
        gas = db.session.query(func.sum(Compra.total)).filter(
            func.date(Compra.fecha) == dia
        ).scalar() or 0
        grafico.append({
            'dia':      dia.strftime('%d/%m'),
            'ingresos': round(ing, 2),
            'gastos':   round(gas, 2),
            'balance':  round(ing - gas, 2),
        })

    ultimas_ventas  = Venta.query.order_by(Venta.fecha.desc()).limit(5).all()
    ultimas_compras = Compra.query.order_by(Compra.fecha.desc()).limit(5).all()

    return render_template('dashboard.html',
        total_productos=total_productos,
        productos_bajo_stock=productos_bajo_stock,
        ingresos_hoy=round(ingresos_hoy, 2),
        gastos_hoy=round(gastos_hoy, 2),
        balance_hoy=round(balance_hoy, 2),
        total_ingresos=round(total_ingresos, 2),
        total_gastos=round(total_gastos, 2),
        balance_total=round(balance_total, 2),
        grafico=grafico,
        ultimas_ventas=ultimas_ventas,
        ultimas_compras=ultimas_compras,
    )
