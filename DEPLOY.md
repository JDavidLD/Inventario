# Guía de Deploy en Render

## Paso 1: Preparar GitHub

Si aún no has subido el código a GitHub:

```bash
# Desde la carpeta del proyecto
git init
git add .
git commit -m "Initial commit - Inventario app"
git remote add origin https://github.com/TU_USUARIO/TU_REPO.git
git branch -M main
git push -u origin main
```

> Reemplaza `TU_USUARIO` y `TU_REPO` con tu usuario y nombre del repositorio.

## Paso 2: Crear cuenta en Render

1. Abre [render.com](https://render.com)
2. Haz clic en **Sign Up**
3. Usa GitHub para registrarte (más fácil)

## Paso 3: Conectar GitHub a Render

1. Ve a **Account Settings** → **Connected Services**
2. Haz clic en **Connect GitHub**
3. Autoriza Render a acceder a tus repositorios

## Paso 4: Crear un Web Service

### Opción A: Deploy automático (recomendado)

1. En el dashboard, haz clic en **New +**
2. Selecciona **Web Service**
3. Busca tu repositorio `inventario` y selecciónalo
4. Render detectará automáticamente `render.yaml` y usará esa configuración
5. Haz clic en **Create Web Service**
6. Espera a que se despliegue (2-5 minutos)

### Opción B: Deploy manual

Si la opción automática no funciona:

1. En **Web Service**:
   - **Runtime**: Python 3.11
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn run:app`
   - **Plan**: Free (o superior si lo deseas)

## Paso 5: Configurar variables de entorno

En el panel de tu servicio:

1. Ve a **Environment** (lado izquierdo)
2. Haz clic en **Add Environment Variable**
3. Añade estas variables:

| Variable | Valor | Ejemplo |
|----------|-------|---------|
| `SECRET_KEY` | Una clave segura (mínimo 32 caracteres) | `abc123def456...` |
| `FLASK_ENV` | `production` | `production` |
| `FLASK_DEBUG` | `0` | `0` |
| `DATABASE_URL` | La proporciona Render automáticamente si usas PostgreSQL | (automático) |

Para generar una `SECRET_KEY` segura, usa:
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

O en Windows:
```powershell
python -c "import secrets; print(secrets.token_hex(32))"
```

## Paso 6: Crear base de datos (si usas render.yaml)

Si configuraste `render.yaml`, Render **crea automáticamente** una base de datos PostgreSQL.

Si hiciste deploy manual:

1. En tu servicio de Render, ve a **Databases**
2. Haz clic en **Create Database**
3. Nombre: `inventra_db` (o lo que prefieras)
4. Plan: Free
5. Copia la `DATABASE_URL` que aparece
6. Añádela a tus **Environment Variables**

## Paso 7: Deploy y test

1. Render debería estar ejecutándose. Verifica el estado en **Logs**
2. Tu URL será algo como: `https://inventra.onrender.com`
3. Login:
   - **Usuario**: `admin`
   - **Contraseña**: `admin123`

## Verificar que todo funciona

- ✅ Puedo acceder a la URL de Render
- ✅ Puedo hacer login con admin/admin123
- ✅ Puedo crear productos y ventas
- ✅ El dashboard muestra datos

## Solucionar problemas

### Error 502 Bad Gateway
```
Revisar Logs:
- Ve a Logs en el panel de Render
- Busca mensajes de error
- Probablemente falta la DATABASE_URL
```

### Import Error (módulo no encontrado)
```
Solución:
- Asegúrate de que requirements.txt está actualizado
- Haz `git push` nuevamente
- Render redesplegará automáticamente
```

### Base de datos vacía después del deploy
```
Solución:
- Es normal, se crea en el primer inicio
- Los datos se guardarán en la DB de Render
- Si quieres resetear: ve a Databases y elimina la BD
```

### Cambios locales no se reflejan
```
Solución:
1. Haz cambios locales
2. git add .
3. git commit -m "Descripción"
4. git push
5. Render redesplegará automáticamente (ver Logs)
```

## Actualizar la aplicación

Cada vez que hagas `git push` a `main`, Render **automáticamente** redesplegará.

```bash
# Hacer cambios locales
git add .
git commit -m "Nueva funcionalidad"
git push origin main

# Espera a que Render lo despliegue (ver en Logs)
```

## Cambiar de Base de Datos (SQLite → PostgreSQL)

En producción usa **PostgreSQL** (Render proporciona una gratis con plan Free).

Si ya tienes datos en SQLite local y quieres migrarlos:

1. Exporta datos desde SQLite local
2. Importa a PostgreSQL en Render

Pero si es un nuevo deploy, PostgreSQL se crea automáticamente.

## Soporte

- Documentación de Render: https://render.com/docs
- Dashboard: https://dashboard.render.com
- Estado de servicios: https://status.render.com
