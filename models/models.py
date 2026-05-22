from app import db
from datetime import datetime

class Proveedor(db.Model):
    __tablename__ = 'proveedores'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(120), nullable=False)
    telefono = db.Column(db.String(30))
    email = db.Column(db.String(120))
    direccion = db.Column(db.String(200))
    image_filename = db.Column(db.String(200))
    productos = db.relationship('Producto', backref='proveedor', lazy=True)
    compras = db.relationship('Compra', backref='proveedor', lazy=True)

    def __repr__(self):
        return f'<Proveedor {self.nombre}>'

class Producto(db.Model):
    __tablename__ = 'productos'
    id = db.Column(db.Integer, primary_key=True)
    codigo_barras = db.Column(db.String(50), unique=True, nullable=True)
    nombre = db.Column(db.String(150), nullable=False)
    descripcion = db.Column(db.String(300))
    precio_compra = db.Column(db.Float, nullable=False, default=0)
    precio_venta = db.Column(db.Float, nullable=False, default=0)
    stock = db.Column(db.Integer, nullable=False, default=0)
    stock_minimo = db.Column(db.Integer, nullable=False, default=5)
    proveedor_id = db.Column(db.Integer, db.ForeignKey('proveedores.id'), nullable=True)
    categoria = db.Column(db.String(80), nullable=True, default='Otros')
    creado_en = db.Column(db.DateTime, default=datetime.now)
    image_filename = db.Column(db.String(200))
    detalles_compra = db.relationship('DetalleCompra', backref='producto', lazy=True)
    detalles_venta = db.relationship('DetalleVenta', backref='producto', lazy=True)

    @property
    def bajo_stock(self):
        return self.stock <= self.stock_minimo

    @property
    def ganancia_unitaria(self):
        return self.precio_venta - self.precio_compra

    def __repr__(self):
        return f'<Producto {self.nombre}>'

class Compra(db.Model):
    __tablename__ = 'compras'
    id = db.Column(db.Integer, primary_key=True)
    proveedor_id = db.Column(db.Integer, db.ForeignKey('proveedores.id'), nullable=True)
    fecha = db.Column(db.DateTime, default=datetime.now)
    total = db.Column(db.Float, default=0)
    notas = db.Column(db.String(300))
    detalles = db.relationship('DetalleCompra', backref='compra', lazy=True, cascade='all, delete-orphan')

class DetalleCompra(db.Model):
    __tablename__ = 'detalles_compra'
    id = db.Column(db.Integer, primary_key=True)
    compra_id = db.Column(db.Integer, db.ForeignKey('compras.id'), nullable=False)
    producto_id = db.Column(db.Integer, db.ForeignKey('productos.id'), nullable=False)
    cantidad = db.Column(db.Integer, nullable=False)
    precio_unitario = db.Column(db.Float, nullable=False)

    @property
    def subtotal(self):
        return self.cantidad * self.precio_unitario

class Venta(db.Model):
    __tablename__ = 'ventas'
    id = db.Column(db.Integer, primary_key=True)
    fecha = db.Column(db.DateTime, default=datetime.now)
    total = db.Column(db.Float, default=0)
    ganancia = db.Column(db.Float, default=0)
    metodo_pago = db.Column(db.String(50), nullable=False, default='Efectivo')
    notas = db.Column(db.String(300))
    detalles = db.relationship('DetalleVenta', backref='venta', lazy=True, cascade='all, delete-orphan')

class DetalleVenta(db.Model):
    __tablename__ = 'detalles_venta'
    id = db.Column(db.Integer, primary_key=True)
    venta_id = db.Column(db.Integer, db.ForeignKey('ventas.id'), nullable=False)
    producto_id = db.Column(db.Integer, db.ForeignKey('productos.id'), nullable=False)
    cantidad = db.Column(db.Integer, nullable=False)
    precio_unitario = db.Column(db.Float, nullable=False)
    precio_compra = db.Column(db.Float, nullable=False)

    @property
    def subtotal(self):
        return self.cantidad * self.precio_unitario

    @property
    def ganancia(self):
        return self.cantidad * (self.precio_unitario - self.precio_compra)
