# API de Kalendas - Backend del Proyecto de Calendarios

Este repositorio contiene el backend para el proyecto de gestión de calendarios y eventos, desarrollado con FastAPI y MongoDB.

## 📜 Descripción General

La API proporciona una interfaz RESTful para realizar operaciones CRUD (Crear, Leer, Actualizar, Eliminar) sobre dos recursos principales: **Calendarios** y **Eventos**. Está diseñada para ser robusta, escalable y fácil de usar, aprovechando la validación de datos de Pydantic y la flexibilidad de una base de datos NoSQL.

## Guía de Instalación y Puesta en Marcha

Sigue estos pasos para configurar y ejecutar el proyecto en tu máquina local.

### 1. Prerrequisitos

Asegúrate de tener instalado **Python 3.9** o una versión superior.

### 2. Clonar el Repositorio

```bash
git clone <URL_DEL_REPOSITORIO>
cd Backend
```

### 3. Configurar el Entorno Virtual

Es una buena práctica trabajar dentro de un entorno virtual para aislar las dependencias del proyecto.

```bash
# Crear el entorno virtual
python3 -m venv venv

# Activar el entorno (en macOS/Linux)
source venv/bin/activate
```

### 4. Instalar Dependencias

Instala todas las librerías necesarias que se encuentran en `requirements.txt`.

```bash
pip install -r requirements.txt
```

### 5. Configurar las Variables de Entorno

Crea un archivo llamado `.env` en la raíz del proyecto (`/Backend`). Este archivo **no debe ser subido a Git**.

Dentro del archivo `.env`, añade la URI de conexión a MongoDB que se compartió por el grupo de Whatsapp:

```env
# Contenido para el archivo .env
MONGODB_URI="mongodb+srv://<usuario>:<password>@<cluster>..."
```

### 6. Poblar la Base de Datos (Paso Inicial)

Para tener datos de ejemplo con los que trabajar, ejecuta el script `seed_database.py`. Este script limpiará las colecciones existentes y las llenará con datos nuevos.

```bash
python app/seed_database.py
```

Deberías ver un mensaje indicando que la base de datos se ha poblado con éxito.

### 7. Ejecutar la Aplicación

Finalmente, inicia el servidor de desarrollo con Uvicorn.

```bash
uvicorn app.main:app --reload
```

- `app.main:app`: Le dice a Uvicorn dónde encontrar la instancia de la aplicación FastAPI.
- `--reload`: Reinicia el servidor automáticamente cada vez que detecta un cambio en el código.

¡Listo! La API estará funcionando en `http://127.0.0.1:8000`.

## ✅ Ejecución de Tests

El proyecto incluye una suite de tests automatizados para garantizar la fiabilidad de la API. Utilizamos `pytest` para la ejecución de los tests.

Para ejecutar la suite completa de tests, asegúrate de estar en el directorio raíz del proyecto (`/Backend`) y ejecuta el siguiente comando:

```bash
python -m pytest
```

Los tests se conectarán automáticamente a una base de datos de prueba separada (`KalendasDB_Test`), ejecutarán las pruebas contra todos los endpoints y luego limpiarán la base de datos de prueba. Esto asegura que los datos de desarrollo no se vean afectados. Para ver más detalles durante la ejecución (como la salida de `print`), puedes usar el flag `-s`:

```bash
python -m pytest -s
```
