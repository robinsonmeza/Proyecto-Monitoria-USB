# MonitorHub USB

Plataforma web para la gestión integral de monitorias académicas y tutorías docentes en la Universidad Simón Bolívar — Cúcuta. Desarrollada como proyecto integrador de **Ingeniería de Software** bajo la dirección de la Ing. María Carlota Bernal.

🔗 **Demo en vivo:** [proyecto-monitoria-usb.vercel.app](https://proyecto-monitoria-usb.vercel.app)

---

## Características Principales

- **Autenticación institucional** — Login con correo `@unisimon.edu.co`. Microsoft OAuth 2.0 previsto para la versión final de producción.
- **Monitorias académicas** — Ciclo completo: búsqueda → solicitud → mensajes → calificación. El monitor es un estudiante de alto rendimiento aprobado por el administrador.
- **Tutorías con docentes** — Los docentes publican su disponibilidad horaria; los estudiantes solicitan sesiones directas de tutoría.
- **Sistema de ranking Hake** — Evaluación basada en la *Ganancia Normalizada de Hake* (g) + estrellas + volumen de sesiones.
- **Buzón de mensajes** — Comunicación asíncrona por solicitud entre estudiante y monitor.
- **Notificaciones** — Toasts en tiempo real y notificaciones internas; correo institucional vía Microsoft Graph API (versión final).
- **Panel de administración** — Aprobación de monitores, estadísticas globales, acceso al panel Django `/admin/`.

---

## Roles del Sistema

| Rol | Descripción |
|-----|-------------|
| **Estudiante** | Busca monitores y docentes, solicita monitorias/tutorías, califica |
| **Monitor** | Recibe solicitudes de monitoria, gestiona disponibilidad, ve su ranking |
| **Docente** | Publica horarios de tutoría, supervisa monitores de sus materias, recibe solicitudes |
| **Administrador** | Control total: aprueba monitores, gestiona usuarios y materias |

> Un **Monitor** tiene doble perfil: como monitor recibe solicitudes; como estudiante puede solicitar monitorias de otras materias.

---

## Stack Tecnológico

| Capa | Tecnología |
|------|-----------|
| Backend | Django 4.2+ |
| Frontend | Bootstrap 5.3 + Bootstrap Icons |
| Base de datos (desarrollo) | SQLite |
| Base de datos (Vercel) | PostgreSQL — Neon (serverless, free tier) |
| Base de datos (producción USB) | MySQL — servidor universitario |
| Tiempo real | Django Channels + Redis + Daphne (ASGI) |
| Deploy | Vercel (serverless) |
| Auth (producción) | Microsoft OAuth 2.0 — Azure AD |
| Integraciones | Microsoft Graph API (Teams, correo) |

---

## Estructura del Proyecto

```
monitorhub/
├── apps/
│   ├── usuarios/        # AbstractUser, PerfilEstudiante, PerfilDocente
│   ├── monitores/       # PerfilMonitor, Materia, DisponibilidadMonitor
│   ├── solicitudes/     # SolicitudMonitoria, SolicitudTutoria
│   ├── sesiones/        # Sesion, DisponibilidadDocente
│   ├── calificaciones/  # Calificacion (Hake)
│   ├── mensajes/        # Mensaje (buzón asíncrono)
│   └── notificaciones/  # Notificacion
├── monitorhub/          # settings.py, urls.py, asgi.py, wsgi.py
├── templates/
│   ├── base.html
│   ├── usuarios/        # login, dashboard_*
│   ├── monitores/       # lista, detalle
│   ├── solicitudes/     # mis_solicitudes, nueva_tutoria
│   ├── mensajes/        # bandeja
│   └── calificaciones/  # calificar, mis_calificaciones
├── static/
│   └── img/             # Logos USB, diagramas VP
├── pyproject.toml       # Definición del proyecto para uv/Vercel
├── uv.lock              # Lock de dependencias (Vercel lo usa con uv sync --locked)
├── requirements.txt
└── .env                 # No incluir en git
```

---

## Instalación (Desarrollo Local)

### Requisitos
- Python 3.11+
- Redis (para Django Channels en producción; en desarrollo puede omitirse)

### Pasos

```bash
# 1. Crear y activar entorno virtual
python -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate     # Linux/Mac

# 2. Instalar dependencias
pip install -r requirements.txt

# 3. Crear archivo .env en la raíz
SECRET_KEY=django-insecure-clave-local
DEBUG=True
REDIS_URL=redis://localhost:6379

# 4. Aplicar migraciones (SQLite local — no requiere configuración extra)
python manage.py migrate

# 5. Cargar datos de prueba
python manage.py cargar_datos_prueba

# 6. Iniciar servidor
python manage.py runserver 8001
```

Accede en: `http://127.0.0.1:8001/login/`

---

## Credenciales de Prueba

| Correo | Contraseña | Rol |
|--------|-----------|-----|
| `admin@unisimon.edu.co` | `admin123` | Administrador |
| `c_perez@unisimon.edu.co` | `estudiante123` | Estudiante |
| `p_martinez@unisimon.edu.co` | `monitor123` | Monitor |
| `r_rodriguez@unisimon.edu.co` | `docente123` | Docente |

---

## Variables de Entorno (.env)

```env
SECRET_KEY=tu_secret_key_aqui
DEBUG=True

# Base de datos — dejar vacío para usar SQLite en desarrollo
# DATABASE_URL=postgresql://usuario:password@host/db?sslmode=require  # Neon
# DATABASE_URL=mysql://usuario:password@localhost/monitorhub           # MySQL (producción USB)

# Redis — requerido para Django Channels
REDIS_URL=redis://localhost:6379

# Microsoft Azure AD — versión final de producción
AZURE_CLIENT_ID=tu_client_id
AZURE_CLIENT_SECRET=tu_client_secret
AZURE_TENANT_ID=tu_tenant_id
```

---

## Deploy en Vercel

El proyecto está configurado para desplegarse en Vercel con base de datos [Neon](https://neon.tech) (PostgreSQL serverless, free tier).

### Variables de entorno requeridas en Vercel

| Variable | Descripción |
|----------|-------------|
| `SECRET_KEY` | Clave secreta Django (larga y aleatoria) |
| `DEBUG` | `False` en producción |
| `DATABASE_URL` | URL de conexión Neon (`postgresql://...?sslmode=require`) |
| `ALLOWED_HOSTS` | Dominios permitidos (ej: `proyecto-monitoria-usb.vercel.app,.vercel.app`) |

### Primer deploy

```bash
# 1. Instalar Vercel CLI
npm install -g vercel

# 2. Autenticarse
vercel login

# 3. Vincular proyecto existente
vercel link --project proyecto-monitoria-usb

# 4. Correr migraciones contra Neon (una sola vez)
DATABASE_URL=postgresql://... python manage.py migrate
DATABASE_URL=postgresql://... python manage.py cargar_datos_prueba

# 5. Deploy a producción
vercel --prod
```

---

## Documentación Técnica

Diagramas UML (Casos de Uso, Clases, Secuencia), Business Model Canvas y arquitectura detallada:

👉 [`documentacion_monitorhub.html`](./documentacion_monitorhub.html)

---

## Licencia

Proyecto académico desarrollado para la materia Ingenieria de Software en la Universidad Simón Bolívar — Cúcuta.  
© 2026 — Todos los derechos reservados.
