from flask import Blueprint, render_template, redirect, url_for, request, flash, current_app
from flask_login import login_required
from sqlalchemy import func
from datetime import datetime
import os
from werkzeug.utils import secure_filename
import uuid
from models.models import Proveedor, Compra
from app import db

proveedores_bp = Blueprint('proveedores', __name__, url_prefix='/proveedores')

@proveedores_bp.route('/')
@login_required
def index():
    proveedores = Proveedor.query.order_by(Proveedor.nombre).all()
    total_proveedores = len(proveedores)
    proveedores_activos = sum(1 for p in proveedores if p.compras)
    mes_actual = datetime.utcnow().strftime('%Y-%m')
    compras_mes = db.session.query(func.coalesce(func.sum(Compra.total), 0)).filter(func.strftime('%Y-%m', Compra.fecha) == mes_actual).scalar() or 0
    pendientes_pago = db.session.query(func.coalesce(func.sum(Compra.total), 0)).filter(Compra.notas.ilike('%pendiente%')).scalar() or 0
    return render_template('proveedores/index.html', proveedores=proveedores,
                           total_proveedores=total_proveedores,
                           proveedores_activos=proveedores_activos,
                           compras_mes=compras_mes,
                           pendientes_pago=pendientes_pago)

@proveedores_bp.route('/nuevo', methods=['GET', 'POST'])
@login_required
def nuevo():
    if request.method == 'POST':
        p = Proveedor(
            nombre=request.form.get('nombre', '').strip(),
            telefono=request.form.get('telefono', '').strip(),
            email=request.form.get('email', '').strip(),
            direccion=request.form.get('direccion', '').strip()
        )

        # handle image upload
        imagen = request.files.get('imagen')
        if imagen and imagen.filename:
            filename = secure_filename(imagen.filename)
            ext = os.path.splitext(filename)[1].lower()
            if ext in ('.jpg', '.jpeg', '.png', '.gif', '.webp'):
                unique = f"{uuid.uuid4().hex}{ext}"
                dest = os.path.join(current_app.root_path, 'static', 'img', 'proveedores', unique)
                imagen.save(dest)
                p.image_filename = unique
        db.session.add(p)
        db.session.commit()
        flash('Proveedor creado correctamente.', 'success')
        return redirect(url_for('proveedores.index'))
    return render_template('proveedores/form.html', proveedor=None)

@proveedores_bp.route('/editar/<int:id>', methods=['GET', 'POST'])
@login_required
def editar(id):
    p = Proveedor.query.get_or_404(id)
    if request.method == 'POST':
        p.nombre = request.form.get('nombre', '').strip()
        p.telefono = request.form.get('telefono', '').strip()
        p.email = request.form.get('email', '').strip()
        p.direccion = request.form.get('direccion', '').strip()

        # handle image upload (replace existing)
        imagen = request.files.get('imagen')
        if imagen and imagen.filename:
            filename = secure_filename(imagen.filename)
            ext = os.path.splitext(filename)[1].lower()
            if ext in ('.jpg', '.jpeg', '.png', '.gif', '.webp'):
                unique = f"{uuid.uuid4().hex}{ext}"
                dest = os.path.join(current_app.root_path, 'static', 'img', 'proveedores', unique)
                imagen.save(dest)
                # remove old image if exists
                if p.image_filename:
                    try:
                        old = os.path.join(current_app.root_path, 'static', 'img', 'proveedores', p.image_filename)
                        if os.path.exists(old): os.remove(old)
                    except Exception:
                        pass
                p.image_filename = unique
        db.session.commit()
        flash('Proveedor actualizado.', 'success')
        return redirect(url_for('proveedores.index'))
    return render_template('proveedores/form.html', proveedor=p)

@proveedores_bp.route('/eliminar/<int:id>', methods=['POST'])
@login_required
def eliminar(id):
    p = Proveedor.query.get_or_404(id)
    db.session.delete(p)
    db.session.commit()
    flash('Proveedor eliminado.', 'success')
    return redirect(url_for('proveedores.index'))
