from flask import Blueprint, render_template, redirect, url_for, request, flash, current_app
from flask_login import login_user, logout_user, login_required
from werkzeug.security import check_password_hash, generate_password_hash
from models.user import User
import os
from werkzeug.utils import secure_filename
import uuid

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            return redirect(url_for('dashboard.index'))
        flash('Usuario o contraseña incorrectos.', 'danger')
    return render_template('login.html')


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        if not username or not password:
            flash('Usuario y contraseña son requeridos.', 'danger')
            return render_template('register.html')
        if User.query.filter_by(username=username).first():
            flash('El nombre de usuario ya existe.', 'danger')
            return render_template('register.html')
        user = User(username=username, password_hash=generate_password_hash(password))
        try:
            # import db lazily to avoid circular imports
            from app import db as _db
            _db.session.add(user)
            _db.session.commit()
        except Exception as e:
            flash('Error al crear usuario: ' + str(e), 'danger')
            return render_template('register.html')
        flash('Usuario creado correctamente. Ya puedes iniciar sesión.', 'success')
        return redirect(url_for('auth.login'))
    return render_template('register.html')

@auth_bp.route('/reset-db', methods=['POST'])
@login_required
def reset_db():
    from app import db, _seed_admin

    db.session.remove()
    db.engine.dispose()
    database_url = current_app.config.get('SQLALCHEMY_DATABASE_URI', '')
    if not database_url.startswith('sqlite:///'):
        flash('Reset solo disponible para SQLite.', 'danger')
        return redirect(url_for('dashboard.index'))

    try:
        db.drop_all()
        db.create_all()
        _seed_admin()
    except Exception as e:
        flash('No se pudo resetear la base de datos: ' + str(e), 'danger')
        return redirect(url_for('dashboard.index'))

    flash('Base de datos reiniciada. Inicia sesión nuevamente.', 'success')
    return redirect(url_for('auth.login'))


@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))
