# Checklist Final - Antes de Deploy

## Archivos para Deploy ✅

- [x] **Procfile** - Define cómo Render ejecuta la app
- [x] **runtime.txt** - Especifica versión de Python (3.11.9)
- [x] **render.yaml** - Configuración completa de Render (recomendado)
- [x] **requirements.txt** - Incluye gunicorn y psycopg2
- [x] **.gitignore** - Ignora archivos innecesarios
- [x] **.env.example** - Variables de entorno necesarias
- [x] **run.py** - Actualizado para producción (port 0.0.0.0)
- [x] **README.md** - Instrucciones de deploy
- [x] **DEPLOY.md** - Guía paso a paso

## Configuración del código ✅

- [x] `app.py` soporta PostgreSQL y SQLite
- [x] Conversión automática de postgres:// a postgresql://
- [x] SECRET_KEY desde variables de entorno
- [x] db.create_all() automático
- [x] Usuario admin creado automáticamente

## Base de datos ✅

- [x] SQLAlchemy configurado para producción
- [x] Compatible con PostgreSQL (Render)
- [x] Compatible con SQLite (local)
- [x] Migraciones automáticas de schema

## Seguridad ✅

- [x] SECRET_KEY debe ser generado antes de producción
- [x] FLASK_DEBUG = 0 en producción
- [x] FLASK_ENV = production
- [x] Requirements pinned a versiones específicas

## Próximos pasos

### 1. Sube a GitHub
```bash
git init
git add .
git commit -m "Preparado para deploy en Render"
git remote add origin https://github.com/tu-usuario/inventario.git
git push -u origin main
```

### 2. En Render.com
```
1. Crea Web Service desde tu repositorio GitHub
2. Render detectará render.yaml automáticamente
3. Configura SECRET_KEY (genera con: python -c "import secrets; print(secrets.token_hex(32))")
4. Deploy automático
```

### 3. Verifica
```
- Abre https://tu-servicio.onrender.com
- Login: admin / admin123
- Prueba crear un producto
```

## Notas importantes

- ⚠️ El plan FREE de Render tiene limitaciones (no ideal para producción real)
- ℹ️ La DB se resetea si cambias planes o la reinicias
- 💾 Considera backups regulares si tienes datos importantes
- 🚀 Para producción real, considera un plan de pago

## Archivos clave

```
inventario/
├── Procfile          ← Le dice a Render cómo ejecutar
├── runtime.txt       ← Versión de Python
├── render.yaml       ← Config completa (opcional pero recomendado)
├── requirements.txt  ← Dependencias incluye gunicorn
├── .gitignore        ← Qué ignorar en Git
├── .env.example      ← Variables de entorno
├── DEPLOY.md         ← Esta guía
├── README.md         ← Documentación general
├── app.py            ← Soporta PostgreSQL/SQLite
├── run.py            ← Entry point (actualizado)
└── [resto del proyecto...]
```

## Comandos útiles (local)

```bash
# Instalar deps
pip install -r requirements.txt

# Correr localmente
python run.py

# Generar SECRET_KEY
python -c "import secrets; print(secrets.token_hex(32))"

# Compilar Python files para errores
python -m py_compile app.py run.py models/*.py routes/*.py
```

---

✅ **Proyecto listo para deploy en Render**
