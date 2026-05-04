# Guía de Despliegue - MonitorHub USB

## Requisitos Previos
- Python 3.11+
- MySQL
- Redis

## Instalación Local
1. Clonar el repositorio.
2. Crear un entorno virtual: `python -m venv venv`.
3. Activar el entorno virtual.
4. Instalar dependencias: `pip install -r requirements.txt`.
5. Configurar el archivo `.env`.
6. Aplicar migraciones: `python manage.py migrate`.
7. Iniciar el servidor: `python manage.py runserver`.

## Producción
- Usar **Daphne** como servidor ASGI.
- Configurar **Nginx** como proxy inverso.
- Habilitar **HTTPS** para la integración con Azure AD.
