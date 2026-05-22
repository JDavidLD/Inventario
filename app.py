import os
import sqlite3
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

db = SQLAlchemy()
login_manager = LoginManager()

def create_app():
    app = Flask(__name__, instance_relative_config=True)
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-prod')
    os.makedirs(app.instance_path, exist_ok=True)
    
    database_url = os.environ.get('DATABASE_URL')
    if not database_url:
        database_url = 'sqlite:///' + os.path.join(app.instance_path, 'inventario.db')
    # Fix for Render PostgreSQL URL format
    if database_url.startswith('postgres://'):
        database_url = database_url.replace('postgres://', 'postgresql://', 1)
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Inicia sesión para acceder.'
    login_manager.login_message_category = 'warning'

    from routes.auth import auth_bp
    from routes.dashboard import dashboard_bp
    from routes.productos import productos_bp
    from routes.proveedores import proveedores_bp
    from routes.compras import compras_bp
    from routes.ventas import ventas_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(productos_bp)
    app.register_blueprint(proveedores_bp)
    app.register_blueprint(compras_bp)
    app.register_blueprint(ventas_bp)

    with app.app_context():
        db.create_all()
        _ensure_sqlite_schema(app)
        _seed_admin()

    return app


def _ensure_sqlite_schema(app):
    database_url = app.config.get('SQLALCHEMY_DATABASE_URI', '')
    if not database_url.startswith('sqlite:///'):
        return
    path = database_url.replace('sqlite:///', '', 1)
    if not os.path.isabs(path):
        path = os.path.join(app.root_path, path)
    try:
        conn = sqlite3.connect(path)
        cursor = conn.cursor()
        cursor.execute("PRAGMA table_info(productos)")
        columns = [row[1] for row in cursor.fetchall()]
        if 'categoria' not in columns:
            cursor.execute("ALTER TABLE productos ADD COLUMN categoria VARCHAR(80) DEFAULT 'Otros';")
            conn.commit()
    except Exception:
        pass
    finally:
        try:
            conn.close()
        except Exception:
            pass
def _seed_admin():
    from models.user import User
    from werkzeug.security import generate_password_hash
    if not User.query.filter_by(username='admin').first():
        admin = User(username='admin', password_hash=generate_password_hash('admin123'))
        db.session.add(admin)
        db.session.commit()
