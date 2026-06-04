# MonitorHub USB

<p align="center">
  <img src="static/img/logo_usb_emblema.png" alt="Logo USB" width="120">
</p>

Plataforma web para la gestión integral de monitorías académicas y tutorías docentes en la **Universidad Simón Bolívar — Sede Cúcuta**. Desarrollada como proyecto integrador de la asignatura de **Ingeniería de Software** bajo la dirección de la Ing. María Carlota Bernal.

El sistema permite a los estudiantes buscar monitores, solicitar sesiones de monitoría y tutoría, comunicarse mediante un buzón de mensajes, y calificar la calidad de las sesiones recibidas. Los monitores gestionan su disponibilidad y reciben solicitudes, los docentes publican horarios de tutoría y supervisan las monitorías de sus materias, y los administradores controlan la aprobación de monitores y la gestión general de la plataforma.

**Demo en vivo:** [proyecto-monitoria-usb.vercel.app](https://proyecto-monitoria-usb.vercel.app)

---

## Tabla de Contenidos

- [Características Principales](#características-principales)
- [Roles del Sistema](#roles-del-sistema)
- [Stack Tecnológico](#stack-tecnológico)
- [Modelo de Datos](#modelo-de-datos)
- [Estructura del Proyecto](#estructura-del-proyecto)
- [Rutas de la Aplicación](#rutas-de-la-aplicación)
- [Instalación (Desarrollo Local)](#instalación-desarrollo-local)
- [Credenciales de Prueba](#credenciales-de-prueba)
- [Variables de Entorno](#variables-de-entorno)
- [Deploy en Vercel](#deploy-en-vercel)
- [Guía de Uso por Rol](#guía-de-uso-por-rol)
- [Sistema de Ranking Hake](#sistema-de-ranking-hake)
- [Documentación Técnica](#documentación-técnica)
- [Comandos de Gestión Personalizados](#comandos-de-gestión-personalizados)
- [Licencia](#licencia)

---

## Características Principales

### Autenticación y Roles
- **Login institucional** con correo `@unisimon.edu.co` y contraseña. El sistema utiliza un modelo de usuario personalizado (`AbstractUser`) donde el campo principal de autenticación es el correo electrónico en lugar del nombre de usuario.
- **Microsoft OAuth 2.0** previsto para la versión final de producción mediante Azure AD y la librería MSAL, lo que permitirá inicio de sesión único (SSO) con cuentas institucionales de Microsoft 365.
- **Dashboard personalizado por rol**: cada tipo de usuario (estudiante, monitor, docente, administrador) accede a un panel de control diferente con funcionalidades específicas para su perfil.

### Monitorías Académicas
- Ciclo completo de monitoría: **búsqueda de monitores → solicitud → mensajes → sesiones → calificación**. El monitor es un estudiante de alto rendimiento que ha sido aprobado previamente por un administrador.
- Los monitores pueden gestionar su disponibilidad horaria indicando día, hora de inicio y fin, modalidad (presencial o virtual) y ubicación.
- Las solicitudes de monitoría incluyen la nota inicial del estudiante y la nota del corte actual, lo que permite medir la ganancia académica tras las sesiones.

### Tutorías con Docentes
- Los docentes publican su **disponibilidad horaria** para tutorías, especificando materia, día, horario, modalidad y ubicación.
- Los estudiantes pueden solicitar tutorías directamente con los docentes que tengan horarios disponibles, creando un flujo de comunicación directo sin intermediarios.
- Las solicitudes de tutoría siguen el mismo ciclo de estados que las monitorías: pendiente, activo, completado, cancelado.

### Sistema de Ranking Hake
- Evaluación basada en la **Ganancia Normalizada de Hake** (g), una métrica científica que mide la mejora real del estudiante en relación con su punto de partida. La fórmula utilizada es: `g = (nota_final - nota_inicial) / (nota_maxima - nota_inicial)`.
- El ranking compuesto de cada monitor se calcula con la fórmula: **40% estrellas + 40% Hake + 20% volumen de sesiones**, proporcionando una evaluación equilibrada entre calidad percibida, efectividad académica y experiencia.
- Niveles de ganancia Hake: alta (g >= 0.7), media (0.3 <= g < 0.7), baja (0 <= g < 0.3), retroceso (g < 0).

### Buzón de Mensajes
- Comunicación asíncrona vinculada a cada solicitud de monitoría entre estudiante y monitor. Los mensajes se organizan por solicitud, lo que mantiene el contexto de cada conversación.
- Marca automática de lectura cuando el destinatario abre la conversación, y notificación al otro participante sobre nuevos mensajes.
- Soporte preparado para tiempo real mediante Django Channels y WebSockets para la versión con chat en vivo.

### Notificaciones
- Sistema de notificaciones internas con 7 tipos: nueva solicitud, solicitud aceptada, nueva sesión, sesión cancelada, nueva calificación, nuevo mensaje y monitor aprobado.
- Toasts en la interfaz que muestran alertas en tiempo real al usuario sobre eventos relevantes.
- Correo institucional vía Microsoft Graph API previsto para la versión final de producción, lo que permitirá enviar notificaciones por email de forma automática.

### Panel de Administración
- Aprobación y rechazo de monitores desde el dashboard del administrador, con registro de quién aprobó cada monitor y la fecha de aprobación.
- Estadísticas globales: cantidad de estudiantes, monitores activos, solicitudes activas y materias registradas.
- Acceso completo al panel de administración de Django (`/admin/`) para gestión avanzada de todos los modelos del sistema.

---

## Roles del Sistema

| Rol | Perfil | Funcionalidades |
|-----|--------|-----------------|
| **Estudiante** | `PerfilEstudiante` (código, programa, semestre) | Buscar monitores, solicitar monitorías y tutorías, enviar mensajes, calificar monitorías, ver sus calificaciones |
| **Monitor** | `PerfilMonitor` (biografía, materias, ranking) + hereda perfil de estudiante | Recibir solicitudes de monitoría, gestionar disponibilidad horaria, ver su ranking y calificaciones recibidas, comunicarse con estudiantes |
| **Docente** | `PerfilDocente` (departamento, materias) | Publicar horarios de tutoría, supervisar monitores de sus materias, recibir solicitudes de tutoría, ver solicitudes de monitoría vinculadas |
| **Administrador** | Usuario con `is_staff=True` y rol `ADMINISTRADOR` | Aprobar/rechazar monitores, ver estadísticas globales, gestionar usuarios y materias, acceso a `/admin/` |

> **Nota importante:** Un Monitor tiene doble perfil. Como monitor recibe solicitudes de otros estudiantes; como estudiante puede solicitar monitorías de otras materias. El modelo `PerfilMonitor` tiene una relación `OneToOne` con `PerfilEstudiante`, lo que garantiza que todo monitor también es un estudiante registrado.

---

## Stack Tecnológico

| Capa | Tecnología | Descripción |
|------|-----------|-------------|
| **Backend** | Django 4.2+ | Framework web Python con patrón MVT, modelo de usuario personalizado |
| **Frontend** | Bootstrap 5.3 + Bootstrap Icons | Diseño responsivo con componentes UI preconstruidos |
| **Base de datos (desarrollo)** | SQLite | Base de datos local sin configuración adicional |
| **Base de datos (Vercel)** | PostgreSQL — Neon | Serverless, free tier, conexión con SSL |
| **Base de datos (producción USB)** | MySQL | Servidor universitario con configuración propia |
| **Tiempo real** | Django Channels + Redis + Daphne | Soporte ASGI para WebSockets y chat en vivo |
| **Deploy** | Vercel (serverless) | Despliegue automático desde GitHub |
| **Auth (producción)** | Microsoft OAuth 2.0 — Azure AD | Inicio de sesión único con cuentas institucionales |
| **Integraciones** | Microsoft Graph API | Teams (reuniones virtuales), correo institucional |
| **Imágenes** | Pillow | Procesamiento de logos y avatares |
| **Gestión de env** | django-environ | Manejo seguro de variables de entorno |

---

## Modelo de Datos

### App `usuarios`
| Modelo | Campos principales | Relaciones |
|--------|-------------------|------------|
| `Usuario` | email (login), id_microsoft, rol, activo, fecha_creacion | Hereda de `AbstractUser`, USERNAME_FIELD = email |
| `PerfilEstudiante` | codigo_estudiante, programa, semestre | OneToOne → Usuario |
| `PerfilDocente` | departamento | OneToOne → Usuario, M2M → Materia |

### App `monitores`
| Modelo | Campos principales | Relaciones |
|--------|-------------------|------------|
| `Materia` | codigo, nombre, departamento | M2M desde PerfilDocente y PerfilMonitor |
| `PerfilMonitor` | aprobado, aprobado_por, biografia, promedio_estrellas, promedio_hake, total_sesiones | OneToOne → Usuario, OneToOne → PerfilEstudiante, M2M → Materia |
| `DisponibilidadMonitor` | dia_semana, hora_inicio, hora_fin, modalidad, ubicacion, activo | FK → PerfilMonitor |

### App `solicitudes`
| Modelo | Campos principales | Relaciones |
|--------|-------------------|------------|
| `SolicitudMonitoria` | nota_inicial, nota_corte_actual, estado (PENDIENTE/ACTIVO/COMPLETADO/CANCELADO), notas | FK → PerfilEstudiante, PerfilMonitor, Materia, PerfilDocente |
| `SolicitudTutoria` | nota_inicial, nota_corte_actual, estado, notas | FK → PerfilEstudiante, PerfilDocente, Materia |

### App `sesiones`
| Modelo | Campos principales | Relaciones |
|--------|-------------------|------------|
| `Sesion` | fecha_hora, duracion_minutos, modalidad, url_teams, ubicacion, estado | FK → SolicitudMonitoria |
| `DisponibilidadDocente` | dia_semana, hora_inicio, hora_fin, modalidad, ubicacion, activo | FK → PerfilDocente, FK → Materia |

### App `calificaciones`
| Modelo | Campos principales | Relaciones |
|--------|-------------------|------------|
| `Calificacion` | estrellas (1-5), comentario_privado, nota_final (0-5), puntaje_hake, nivel_hake | OneToOne → SolicitudMonitoria, FK → PerfilEstudiante, FK → PerfilMonitor |

### App `mensajes`
| Modelo | Campos principales | Relaciones |
|--------|-------------------|------------|
| `Mensaje` | contenido, fecha_envio, fecha_lectura, es_tiempo_real | FK → Usuario (remitente, destinatario), FK → SolicitudMonitoria |

### App `notificaciones`
| Modelo | Campos principales | Relaciones |
|--------|-------------------|------------|
| `Notificacion` | tipo (7 tipos), mensaje, fecha_envio, enviado_por_correo, leida | FK → Usuario |

---

## Estructura del Proyecto

```
Proyecto-Monitoria-USB/
│
├── 📄 manage.py                          # Punto de entrada de Django
├── 📄 requirements.txt                   # Dependencias del proyecto
├── 📄 pyproject.toml                     # Configuración del proyecto (uv/Vercel)
├── 📄 uv.lock                            # Lock de dependencias
├── 📄 .env.example                       # Plantilla de variables de entorno
├── 📄 .gitignore                         # Archivos ignorados por Git
├── 📄 README.md                          # Este archivo
├── 📄 Matriz_Riesgos_MonitorHub_USB.xlsx # Matriz de riesgos del proyecto
├── 📄 documentacion_monitorhub.html      # Documentación técnica completa
│
├── 📁 monitorhub/                        # Configuración principal de Django
│   ├── __init__.py
│   ├── settings.py                       # Settings (DB, auth, channels, static)
│   ├── urls.py                           # URLs raíz (incluye apps)
│   ├── asgi.py                           # Configuración ASGI (Channels/Daphne)
│   └── wsgi.py                           # Configuración WSGI (deploy tradicional)
│
├── 📁 apps/                              # Aplicaciones de Django
│   ├── 📁 usuarios/                      # Autenticación, perfiles, dashboards
│   │   ├── models.py                     # Usuario, PerfilEstudiante, PerfilDocente
│   │   ├── views.py                      # Login, Logout, Dashboard por rol
│   │   ├── urls.py                       # Rutas de autenticación y dashboard
│   │   ├── admin.py                      # Registro en admin de Django
│   │   ├── management/commands/
│   │   │   ├── cargar_datos_prueba.py    # Comando: datos de prueba
│   │   │   └── configurar_grupos.py      # Comando: grupos de permisos
│   │   └── migrations/
│   │
│   ├── 📁 monitores/                     # Gestión de monitores y materias
│   │   ├── models.py                     # Materia, PerfilMonitor, DisponibilidadMonitor
│   │   ├── views.py                      # Lista, detalle, aprobar/rechazar
│   │   ├── urls.py
│   │   ├── admin.py
│   │   └── migrations/
│   │
│   ├── 📁 solicitudes/                   # Solicitudes de monitoría y tutoría
│   │   ├── models.py                     # SolicitudMonitoria, SolicitudTutoria
│   │   ├── views.py                      # Nueva solicitud, mis solicitudes, nueva tutoría
│   │   ├── urls.py
│   │   ├── admin.py
│   │   └── migrations/
│   │
│   ├── 📁 sesiones/                      # Sesiones y disponibilidad docente
│   │   ├── models.py                     # Sesion, DisponibilidadDocente
│   │   ├── views.py                      # Gestión de sesiones
│   │   ├── urls.py
│   │   ├── admin.py
│   │   └── migrations/
│   │
│   ├── 📁 calificaciones/                # Calificaciones y ranking Hake
│   │   ├── models.py                     # Calificacion (con cálculo Hake automático)
│   │   ├── views.py                      # Calificar, mis calificaciones
│   │   ├── urls.py
│   │   ├── admin.py
│   │   └── migrations/
│   │
│   ├── 📁 mensajes/                      # Buzón de mensajes
│   │   ├── models.py                     # Mensaje
│   │   ├── views.py                      # Bandeja, enviar mensaje
│   │   ├── urls.py
│   │   ├── admin.py
│   │   └── migrations/
│   │
│   └── 📁 notificaciones/                # Sistema de notificaciones
│       ├── models.py                     # Notificacion (7 tipos)
│       ├── urls.py
│       ├── admin.py
│       └── migrations/
│
├── 📁 templates/                         # Plantillas HTML (Django Templates)
│   ├── base.html                         # Template base con navbar y footer
│   ├── 📁 usuarios/
│   │   ├── login.html                    # Página de inicio de sesión
│   │   ├── dashboard_admin.html          # Panel del administrador
│   │   ├── dashboard_docente.html        # Panel del docente
│   │   ├── dashboard_estudiante.html     # Panel del estudiante
│   │   └── dashboard_monitor.html        # Panel del monitor
│   ├── 📁 monitores/
│   │   ├── lista.html                    # Lista de monitores con filtros
│   │   └── detalle.html                  # Perfil detallado del monitor
│   ├── 📁 solicitudes/
│   │   ├── mis_solicitudes.html          # Historial de solicitudes
│   │   └── nueva_tutoria.html            # Formulario de nueva tutoría
│   ├── 📁 mensajes/
│   │   └── bandeja.html                  # Buzón de mensajes por solicitud
│   └── 📁 calificaciones/
│       ├── calificar.html                # Formulario de calificación
│       └── mis_calificaciones.html       # Historial de calificaciones
│
├── 📁 static/img/                        # Recursos estáticos
│   ├── logo_usb_emblema.png              # Logo emblema USB
│   ├── logo_usb_login.png                # Logo para página de login
│   ├── 📁 Diagramas/                     # Diagramas UML del proyecto
│   │   ├── Diagrama casos de uso/
│   │   ├── Diagrama de actividades/
│   │   ├── Diagrama de clases/
│   │   └── Diagramas de secuencia/       # 14 diagramas de secuencia
│   ├── 📁 Documentacion casos de uso/
│   │   └── Documentacion_Casos_de_Uso_MonitorHub.docx
│   └── 📁 WIREFRAMES_MONITORHUB/
│       └── wireframes_monitorhub_usb.pdf
│
└── 📁 docs/
    └── guia_despliegue.md                # Guía de despliegue en producción
```

---

## Rutas de la Aplicación

| URL | Vista | Descripción |
|-----|-------|-------------|
| `/login/` | `LoginView` | Página de inicio de sesión |
| `/logout/` | `LogoutView` | Cerrar sesión |
| `/` | `DashboardView` | Dashboard redirigido según rol del usuario |
| `/monitores/` | `ListaMonitoresView` | Lista de monitores aprobados con filtros (materia, nombre, modalidad) |
| `/monitores/<pk>/` | `DetalleMonitorView` | Perfil detallado del monitor con disponibilidad |
| `/monitores/<pk>/aprobar/` | `AprobarMonitorView` | Aprobar o rechazar monitor (solo admin) |
| `/solicitudes/` | `MisSolicitudesView` | Historial de solicitudes del usuario |
| `/solicitudes/nueva/<monitor_pk>/` | `NuevaSolicitudView` | Crear solicitud de monitoría |
| `/solicitudes/tutoria/<docente_pk>/` | `NuevaTutoriaView` | Crear solicitud de tutoría |
| `/calificaciones/calificar/<solicitud_pk>/` | `CalificarView` | Calificar una monitoría completada |
| `/calificaciones/mis-calificaciones/` | `MisCalificacionesView` | Ver calificaciones dadas/recibidas |
| `/mensajes/` | `BandejaView` | Buzón de mensajes por solicitud |
| `/mensajes/enviar/<solicitud_pk>/` | `EnviarMensajeView` | Enviar mensaje en una solicitud |
| `/admin/` | Django Admin | Panel de administración nativo de Django |

---

## Instalación (Desarrollo Local)

### Requisitos

- **Python 3.11+** — El proyecto requiere Python 3.11 o superior.
- **Redis** (opcional en desarrollo) — Necesario para Django Channels y funcionalidades en tiempo real. En desarrollo básico puede omitirse sin afectar el funcionamiento principal.
- **Git** — Para clonar el repositorio.

### Pasos

```bash
# 1. Clonar el repositorio
git clone https://github.com/robinsonmeza/Proyecto-Monitoria-USB.git
cd Proyecto-Monitoria-USB

# 2. Crear y activar entorno virtual
python -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate     # Linux/Mac

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Crear archivo .env en la raíz del proyecto
# Copia .env.example y renómbralo a .env, o crea uno nuevo con:
echo "SECRET_KEY=django-insecure-clave-local" > .env
echo "DEBUG=True" >> .env
echo "REDIS_URL=redis://localhost:6379" >> .env

# 5. Aplicar migraciones (SQLite local — no requiere configuración extra)
python manage.py migrate

# 6. Cargar datos de prueba (usuarios, materias, monitores, disponibilidades)
python manage.py cargar_datos_prueba

# 7. Crear superusuario (opcional, los datos de prueba ya incluyen un admin)
python manage.py createsuperuser

# 8. Iniciar servidor de desarrollo
python manage.py runserver 8001
```

Accede a la aplicación en: **http://127.0.0.1:8001/login/**

---

## Credenciales de Prueba

Los datos de prueba se cargan con el comando `python manage.py cargar_datos_prueba` e incluyen:

| Correo | Contraseña | Rol | Nombre |
|--------|-----------|-----|--------|
| `admin@unisimon.edu.co` | `admin123` | Administrador | Admin MonitorHub |
| `c_perez@unisimon.edu.co` | `estudiante123` | Estudiante | Carlos Perez |
| `a_gomez@unisimon.edu.co` | `estudiante123` | Estudiante | Ana Gomez |
| `l_torres@unisimon.edu.co` | `estudiante123` | Estudiante | Luis Torres |
| `p_martinez@unisimon.edu.co` | `monitor123` | Monitor | Pedro Martinez |
| `s_vargas@unisimon.edu.co` | `monitor123` | Monitor | Sofia Vargas |
| `r_rodriguez@unisimon.edu.co` | `docente123` | Docente | Maria Rodriguez |

### Materias de prueba

| Código | Materia | Departamento |
|--------|---------|-------------|
| CAL-101 | Cálculo I | Matemáticas |
| BD-201 | Bases de Datos | Ingeniería de Sistemas |
| PROG-101 | Programación I | Ingeniería de Sistemas |
| ALG-102 | Álgebra Lineal | Matemáticas |
| FIS-101 | Física I | Ciencias Básicas |

---

## Variables de Entorno

El archivo `.env` se configura en la raíz del proyecto. En Vercel, las variables se configuran desde el dashboard del proyecto. A continuación se detallan todas las variables disponibles:

```env
# ── Obligatorias ────────────────────────────────────────────────────────────
SECRET_KEY=tu_secret_key_aqui              # Clave secreta de Django (larga y aleatoria en producción)
DEBUG=True                                  # True en desarrollo, False en producción

# ── Base de datos ───────────────────────────────────────────────────────────
# Dejar vacío o comentar para usar SQLite en desarrollo local
# DATABASE_URL=postgresql://usuario:password@host/db?sslmode=require  # Neon (Vercel)
# DATABASE_URL=mysql://usuario:password@localhost/monitorhub           # MySQL (producción USB)

# ── Redis ───────────────────────────────────────────────────────────────────
REDIS_URL=redis://localhost:6379            # Requerido para Django Channels

# ── Hosts permitidos ───────────────────────────────────────────────────────
ALLOWED_HOSTS=localhost,127.0.0.1           # En Vercel: proyecto-monitoria-usb.vercel.app,.vercel.app

# ── CSRF ────────────────────────────────────────────────────────────────────
CSRF_TRUSTED_ORIGINS=https://*.vercel.app,http://localhost:8001

# ── Microsoft Azure AD (versión final de producción) ────────────────────────
AZURE_CLIENT_ID=tu_client_id_aqui
AZURE_CLIENT_SECRET=tu_client_secret_aqui
AZURE_TENANT_ID=tu_tenant_id_aqui
```

---

## Deploy en Vercel

El proyecto está configurado para desplegarse en Vercel con base de datos **Neon** (PostgreSQL serverless, free tier). El archivo `pyproject.toml` define las dependencias que Vercel instala automáticamente con `uv sync --locked`.

### Variables de entorno requeridas en Vercel

| Variable | Descripción | Ejemplo |
|----------|-------------|---------|
| `SECRET_KEY` | Clave secreta Django (larga y aleatoria) | `django-insecure-...` |
| `DEBUG` | Modo debug | `False` |
| `DATABASE_URL` | URL de conexión Neon | `postgresql://user:pass@ep-xxx.neon.tech/dbname?sslmode=require` |
| `ALLOWED_HOSTS` | Dominios permitidos | `proyecto-monitoria-usb.vercel.app,.vercel.app` |
| `CSRF_TRUSTED_ORIGINS` | Orígenes de confianza para CSRF | `https://proyecto-monitoria-usb.vercel.app,https://*.vercel.app` |

### Primer deploy

```bash
# 1. Instalar Vercel CLI
npm install -g vercel

# 2. Autenticarse en Vercel
vercel login

# 3. Vincular proyecto existente
vercel link --project proyecto-monitoria-usb

# 4. Correr migraciones contra Neon (una sola vez, desde local)
DATABASE_URL=postgresql://usuario:password@host/db?sslmode=require python manage.py migrate
DATABASE_URL=postgresql://usuario:password@host/db?sslmode=require python manage.py cargar_datos_prueba

# 5. Deploy a producción
vercel --prod
```

### Despliegue en producción USB (servidor propio)

Para el despliegue en el servidor universitario con MySQL:

```bash
# 1. Configurar .env con DATABASE_URL=mysql://...
# 2. Usar Daphne como servidor ASGI
daphne -b 0.0.0.0 -p 8001 monitorhub.asgi:application

# 3. Configurar Nginx como proxy inverso
# 4. Habilitar HTTPS para integración con Azure AD
# 5. Ver guia detallada en docs/guia_despliegue.md
```

---

## Guía de Uso por Rol

### Estudiante
1. Inicia sesión con tu correo institucional `@unisimon.edu.co`
2. Desde el dashboard, explora la lista de monitores aprobados y filtra por materia, nombre o modalidad
3. Selecciona un monitor para ver su perfil detallado, materias y disponibilidad horaria
4. Solicita una monitoría indicando la materia, docente supervisor, nota inicial y nota del corte actual
5. Busca docentes con disponibilidad para tutorías y solicita una sesión directa
6. Comunícate con tu monitor a través del buzón de mensajes vinculado a cada solicitud
7. Una vez completada la monitoría, califica la sesión con estrellas y nota final

### Monitor
1. Inicia sesión y accede a tu dashboard personalizado
2. Revisa las solicitudes de monitoría pendientes de tus estudiantes
3. Gestiona tu disponibilidad horaria (días, horarios, modalidad, ubicación)
4. Comunícate con los estudiantes a través del buzón de mensajes
5. Consulta tu ranking compuesto (estrellas + Hake + volumen de sesiones)
6. Revisa las calificaciones recibidas y tu desempeño

### Docente
1. Inicia sesión y accede a tu dashboard de docente
2. Publica y gestiona tus horarios de disponibilidad para tutorías
3. Revisa las solicitudes de tutoría pendientes de los estudiantes
4. Supervisa los monitores asignados a tus materias
5. Revisa las solicitudes de monitoría vinculadas a tus materias

### Administrador
1. Inicia sesión y accede al panel de administración
2. Revisa las solicitudes de monitores pendientes de aprobación
3. Aprueba o rechaza perfiles de monitor con un solo clic
4. Consulta estadísticas globales: estudiantes, monitores activos, solicitudes y materias
5. Accede al panel de Django Admin (`/admin/`) para gestión avanzada

---

## Sistema de Ranking Hake

El sistema utiliza la **Ganancia Normalizada de Hake** como métrica principal para evaluar la efectividad de las monitorías. Esta métrica, originalmente desarrollada para medir el aprendizaje en física, se adapta al contexto de monitorías académicas para medir cuánto mejoró realmente el estudiante en relación con su punto de partida.

### Fórmula

```
g = (nota_final - nota_inicial) / (nota_maxima - nota_inicial)
```

Donde:
- `nota_inicial`: nota que el estudiante tenía al momento de solicitar la monitoría
- `nota_final`: nota del estudiante después de completar las sesiones
- `nota_maxima`: 5.0 (escala de calificación de la USB)

### Niveles de ganancia

| Nivel | Rango de g | Interpretación |
|-------|-----------|----------------|
| Alta | g >= 0.7 | El estudiante mejoró significativamente |
| Media | 0.3 <= g < 0.7 | Mejora moderada |
| Baja | 0 <= g < 0.3 | Mejora mínima |
| Retroceso | g < 0 | El estudiante bajó su nota (penaliza al monitor) |

### Ranking compuesto del monitor

El ranking final de cada monitor se calcula con la siguiente fórmula ponderada:

```
Score = 0.40 × (estrellas / 5) + 0.40 × ((hake + 1) / 2) + 0.20 × min(total_sesiones / 50, 1.0)
```

- **40% Estrellas normalizadas**: percepción cualitativa del estudiante (1-5 estrellas normalizadas a 0-1)
- **40% Hake normalizado**: efectividad académica medida objetivamente (rango [-1,1] normalizado a [0,1])
- **20% Volumen de sesiones**: experiencia del monitor (tope suave en 50 sesiones para normalizar)

Los promedios del monitor (`promedio_estrellas`, `promedio_hake`, `total_sesiones`) se recalculan automáticamente cada vez que se guarda una nueva calificación, garantizando que el ranking siempre esté actualizado.

---

## Comandos de Gestión Personalizados

El proyecto incluye comandos personalizados de Django para facilitar la configuración y prueba del sistema:

### `cargar_datos_prueba`

Crea un conjunto completo de datos de prueba incluyendo materias, usuarios (estudiantes, monitores, docente, administrador), perfiles y disponibilidades horarias.

```bash
python manage.py cargar_datos_prueba
```

Datos que crea:
- 5 materias (Cálculo I, Bases de Datos, Programación I, Álgebra Lineal, Física I)
- 1 docente con 5 materias asignadas
- 3 estudiantes (diferentes programas y semestres)
- 2 monitores aprobados con disponibilidades y biografías
- 1 administrador

### `configurar_grupos`

Configura los grupos de permisos de Django para cada rol del sistema.

```bash
python manage.py configurar_grupos
```

---

## Documentación Técnica

Diagramas UML (Casos de Uso, Clases, Secuencia, Actividades), Business Model Canvas, wireframes y arquitectura detallada:

| Recurso | Ubicación |
|---------|-----------|
| Documentación HTML completa | [`documentacion_monitorhub.html`](./documentacion_monitorhub.html) |
| Documentación de casos de uso | [`static/img/Documentacion casos de uso/Documentacion_Casos_de_Uso_MonitorHub.docx`](./static/img/Documentacion%20casos%20de%20uso/Documentacion_Casos_de_Uso_MonitorHub.docx) |
| Wireframes | [`static/img/WIREFRAMES_MONITORHUB/wireframes_monitorhub_usb.pdf`](./static/img/WIREFRAMES_MONITORHUB/wireframes_monitorhub_usb.pdf) |
| Diagrama de casos de uso | [`static/img/Diagramas/Diagrama casos de uso/Casos de uso.jpg`](./static/img/Diagramas/Diagrama%20casos%20de%20uso/Casos%20de%20uso.jpg) |
| Diagrama de clases | [`static/img/Diagramas/Diagrama de clases/Diagrama de clase.jpg`](./static/img/Diagramas/Diagrama%20de%20clases/Diagrama%20de%20clase.jpg) |
| Diagrama de actividades | [`static/img/Diagramas/Diagrama de actividades/Diagrama de actividades.jpg`](./static/img/Diagramas/Diagrama%20de%20actividades/Diagrama%20de%20actividades.jpg) |
| Diagramas de secuencia (14) | [`static/img/Diagramas/Diagramas de secuencia/`](./static/img/Diagramas/Diagramas%20de%20secuencia/) |
| Matriz de riesgos | [`Matriz_Riesgos_MonitorHub_USB.xlsx`](./Matriz_Riesgos_MonitorHub_USB.xlsx) |
| Guía de despliegue | [`docs/guia_despliegue.md`](./docs/guia_despliegue.md) |

---

## Licencia

Proyecto académico desarrollado para la asignatura de Ingeniería de Software en la Universidad Simón Bolívar — Sede Cúcuta.

&copy; 2026 Robinson Meza y equipo de desarrollo. Todos los derechos reservados.
