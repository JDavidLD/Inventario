# TiendaStock – Sistema de Gestión de Inventario

Aplicación web construida con Flask + SQLite (compatible con PostgreSQL para producción).

## Estructura del proyecto

```
inventario/
├── app.py              # Fábrica de la app y configuración
├── run.py              # Punto de entrada
├── requirements.txt
├── models/
│   ├── user.py         # Modelo de usuario (login)
│   └── models.py       # Producto, Proveedor, Compra, Venta y sus detalles
├── routes/
│   ├── auth.py         # Login / logout
│   ├── dashboard.py    # Panel principal con estadísticas
│   ├── productos.py    # CRUD productos + búsqueda por código
│   ├── proveedores.py  # CRUD proveedores
│   ├── compras.py      # Registro de compras (entrada de stock)
│   └── ventas.py       # Registro de ventas (salida de stock)
├── templates/          # Jinja2 HTML templates
└── static/             # CSS y JS propios
```

## Instalación local

```bash
# 1. Clonar y entrar al proyecto
cd inventario

# 2. Crear entorno virtual
python -m venv venv
source venv/bin/activate        # Linux/Mac
venv\Scripts\activate           # Windows

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Configurar variables (opcional, hay valores por defecto)
cp .env.example .env

# 5. Ejecutar
python run.py
```

Abre http://localhost:5000  
Usuario: **admin** | Contraseña: **admin123**

## Despliegue en Render

### Preparación

1. **Sube el proyecto a GitHub** (si aún no lo has hecho):
   ```bash
   git init
   git add .
   git commit -m "Initial commit - Inventario app"
   git remote add origin https://github.com/tu-usuario/tu-repo.git
   git branch -M main
   git push -u origin main
   ```

2. **En Render.com**:
   - Regístrate / Inicia sesión en [render.com](https://render.com)
   - Conecta tu cuenta de GitHub
   - Crea un nuevo **Web Service**
   - Selecciona este repositorio

3. **Configuración automática**:
   - Render detectará `render.yaml` y usará esa configuración
   - O puedes usar el `Procfile` si lo prefieres

4. **Variables de entorno en Render**:
   - Ve a **Environment** en tu servicio
   - Añade estas variables:
     - `SECRET_KEY` → Genera una clave segura (ej: `openssl rand -hex 32`)
     - `FLASK_ENV` → `production`
     - `FLASK_DEBUG` → `0`
   - La `DATABASE_URL` se crea automáticamente si usas PostgreSQL en Render

### Opciones de deploy

**Opción A: Con render.yaml (recomendado)**
- Render lee automáticamente `render.yaml`
- Crea la base de datos PostgreSQL automáticamente
- Más fácil de mantener

**Opción B: Configuración manual con Procfile**
- Usa el botón "New +" → "Web Service"
- Selecciona tu repositorio
- Configura manualmente el comando de inicio y variables

### Después del deploy

- La primera vez, Render ejecutará las migraciones automáticamente
- Se creará un usuario admin: `admin` / `admin123`
- URL de tu app: `https://tu-servicio.onrender.com`

### Solución de problemas

- **Error de base de datos**: Verifica que la `DATABASE_URL` esté configurada
- **Error 500**: Revisa los logs en el panel de Render
- **Archivos no encontrados**: Asegúrate de que `static/` y `templates/` estén en el repositorio

---

## Características principales

- ✅ Gestión de inventario (productos, stock)
- ✅ Categorización de productos
- ✅ Código de barras (escaneable, opcional)
- ✅ Registro de compras y ventas
- ✅ Gestión de proveedores con imágenes
- ✅ Dashboard con gráficos (últimos 7 días)
- ✅ Modo Cajero (punto de venta)
- ✅ Autenticación de usuarios
- ✅ Diseño responsivo

## Tecnología

- **Backend**: Flask 3.0 + SQLAlchemy 2.0
- **Base de datos**: SQLite (dev) / PostgreSQL (prod)
- **Frontend**: Bootstrap 5 + Chart.js
- **Autenticación**: Flask-Login
- **Deploy**: Render.com (sin costo inicial)


1. Sube el proyecto a GitHub.
2. En Render crea un **Web Service** apuntando al repo.
3. Build command: `pip install -r requirements.txt`
4. Start command: `gunicorn run:app`
5. Agrega las variables de entorno: `SECRET_KEY` y `DATABASE_URL` (PostgreSQL de Render).

Instalar gunicorn:
```
gunicorn==21.2.0
psycopg2-binary==2.9.9
```
(agregar al requirements.txt para producción)

## Funcionalidades

- **Dashboard** con estadísticas, gráfico de ventas semanales y alertas de stock bajo
- **Productos**: CRUD completo con escaneo por cámara o lector físico (tipo teclado)
- **Proveedores**: registro y gestión
- **Compras**: ingreso de mercancía con actualización automática de stock
- **Ventas**: registro de ventas con cálculo automático de ganancia
- Búsqueda de productos por nombre o código de barras
- Alertas visuales de stock mínimo
