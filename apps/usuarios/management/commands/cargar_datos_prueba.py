"""
Management command: cargar_datos_prueba
Creates test fixtures for MonitorHub USB.

Usage:
    python manage.py cargar_datos_prueba
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
import datetime


class Command(BaseCommand):
    help = 'Carga datos de prueba para MonitorHub USB'

    def handle(self, *args, **options):
        self.stdout.write(self.style.MIGRATE_HEADING('=== Cargando datos de prueba ==='))

        from apps.usuarios.models import Usuario, PerfilEstudiante, PerfilDocente
        from apps.monitores.models import Materia, PerfilMonitor, DisponibilidadMonitor

        # ── 1. MATERIAS ──────────────────────────────────────────────
        self.stdout.write('  Creando materias…')
        materias_data = [
            ('CAL-101', 'Cálculo I',            'Matemáticas'),
            ('BD-201',  'Bases de Datos',        'Ingeniería de Sistemas'),
            ('PROG-101','Programación I',         'Ingeniería de Sistemas'),
            ('ALG-102', 'Álgebra Lineal',         'Matemáticas'),
            ('FIS-101', 'Física I',               'Ciencias Básicas'),
        ]
        materias = {}
        for codigo, nombre, depto in materias_data:
            obj, created = Materia.objects.get_or_create(
                codigo=codigo,
                defaults={'nombre': nombre, 'departamento': depto},
            )
            materias[codigo] = obj
            status = 'CREADA' if created else 'ya existe'
            self.stdout.write(f'    {codigo} — {nombre}: {status}')

        # ── 2. DOCENTE ───────────────────────────────────────────────
        self.stdout.write('  Creando docente…')
        docente_user, created = Usuario.objects.get_or_create(
            email='r_rodriguez@unisimon.edu.co',
            defaults={
                'first_name': 'Maria',
                'last_name':  'Rodriguez',
                'rol':        'DOCENTE',
                'is_active':  True,
            },
        )
        if created:
            docente_user.set_password('docente123')
            docente_user.save()
            self.stdout.write('    Docente creada: Maria Rodriguez')
        else:
            self.stdout.write('    Docente ya existe')

        perfil_docente, _ = PerfilDocente.objects.get_or_create(
            usuario=docente_user,
            defaults={'departamento': 'Ingeniería'},
        )
        # Assign all 5 materias
        for mat in materias.values():
            perfil_docente.materias.add(mat)
        perfil_docente.save()

        # ── 3. ESTUDIANTES ───────────────────────────────────────────
        self.stdout.write('  Creando estudiantes…')
        estudiantes_data = [
            ('c_perez@unisimon.edu.co',   'Carlos',  'Perez',   '2021001', 'Ingeniería de Sistemas',  4),
            ('a_gomez@unisimon.edu.co',   'Ana',     'Gomez',   '2021002', 'Ingeniería Industrial',   3),
            ('l_torres@unisimon.edu.co',  'Luis',    'Torres',  '2021003', 'Ingeniería de Sistemas',  5),
        ]
        estudiantes = {}
        for email, fname, lname, codigo, programa, semestre in estudiantes_data:
            user, created = Usuario.objects.get_or_create(
                email=email,
                defaults={
                    'first_name': fname,
                    'last_name':  lname,
                    'rol':        'ESTUDIANTE',
                    'is_active':  True,
                },
            )
            if created:
                user.set_password('estudiante123')
                user.save()
            perfil, _ = PerfilEstudiante.objects.get_or_create(
                usuario=user,
                defaults={
                    'codigo_estudiante': codigo,
                    'programa':         programa,
                    'semestre':         semestre,
                },
            )
            estudiantes[email] = (user, perfil)
            status = 'CREADO' if created else 'ya existe'
            self.stdout.write(f'    {fname} {lname}: {status}')

        # ── 4. MONITORES ─────────────────────────────────────────────
        self.stdout.write('  Creando monitores…')

        # Monitor 1: Pedro Martinez
        mon1_user, created = Usuario.objects.get_or_create(
            email='p_martinez@unisimon.edu.co',
            defaults={
                'first_name': 'Pedro',
                'last_name':  'Martinez',
                'rol':        'MONITOR',
                'is_active':  True,
            },
        )
        if created:
            mon1_user.set_password('monitor123')
            mon1_user.save()

        mon1_perfil_est, _ = PerfilEstudiante.objects.get_or_create(
            usuario=mon1_user,
            defaults={
                'codigo_estudiante': '2019001',
                'programa':         'Ingeniería de Sistemas',
                'semestre':         8,
            },
        )

        mon1, _ = PerfilMonitor.objects.get_or_create(
            usuario=mon1_user,
            defaults={
                'perfil_estudiante': mon1_perfil_est,
                'aprobado':          True,
                'aprobado_por':      None,
                'fecha_aprobacion':  timezone.now(),
                'biografia': (
                    'Estudiante de 8vo semestre con excelentes notas en Cálculo. '
                    'Apasionado por las matemáticas y comprometido con ayudar a '
                    'mis compañeros a superar sus dificultades académicas.'
                ),
            },
        )
        mon1.materias.add(materias['CAL-101'], materias['ALG-102'])

        # Disponibilidades Monitor 1
        DisponibilidadMonitor.objects.get_or_create(
            monitor=mon1,
            dia_semana='LUNES',
            hora_inicio=datetime.time(14, 0),
            defaults={
                'hora_fin':  datetime.time(16, 0),
                'modalidad': 'PRESENCIAL',
                'ubicacion': 'Bloque 7 — Sala 201',
                'activo':    True,
            },
        )
        DisponibilidadMonitor.objects.get_or_create(
            monitor=mon1,
            dia_semana='MIERCOLES',
            hora_inicio=datetime.time(14, 0),
            defaults={
                'hora_fin':  datetime.time(16, 0),
                'modalidad': 'VIRTUAL',
                'ubicacion': '',
                'activo':    True,
            },
        )
        self.stdout.write(f'    Pedro Martinez (monitor): {"CREADO" if created else "ya existe"}')

        # Monitor 2: Sofia Vargas
        mon2_user, created = Usuario.objects.get_or_create(
            email='s_vargas@unisimon.edu.co',
            defaults={
                'first_name': 'Sofia',
                'last_name':  'Vargas',
                'rol':        'MONITOR',
                'is_active':  True,
            },
        )
        if created:
            mon2_user.set_password('monitor123')
            mon2_user.save()

        mon2_perfil_est, _ = PerfilEstudiante.objects.get_or_create(
            usuario=mon2_user,
            defaults={
                'codigo_estudiante': '2019002',
                'programa':         'Ingeniería de Sistemas',
                'semestre':         7,
            },
        )

        mon2, _ = PerfilMonitor.objects.get_or_create(
            usuario=mon2_user,
            defaults={
                'perfil_estudiante': mon2_perfil_est,
                'aprobado':          True,
                'aprobado_por':      None,
                'fecha_aprobacion':  timezone.now(),
                'biografia': (
                    'Apasionada por las bases de datos y la programación. '
                    'Con experiencia en MySQL, PostgreSQL y Python, me dedico '
                    'a explicar conceptos complejos de forma sencilla y práctica.'
                ),
            },
        )
        mon2.materias.add(materias['BD-201'], materias['PROG-101'])

        # Disponibilidades Monitor 2
        DisponibilidadMonitor.objects.get_or_create(
            monitor=mon2,
            dia_semana='MARTES',
            hora_inicio=datetime.time(10, 0),
            defaults={
                'hora_fin':  datetime.time(12, 0),
                'modalidad': 'VIRTUAL',
                'ubicacion': '',
                'activo':    True,
            },
        )
        DisponibilidadMonitor.objects.get_or_create(
            monitor=mon2,
            dia_semana='JUEVES',
            hora_inicio=datetime.time(10, 0),
            defaults={
                'hora_fin':  datetime.time(12, 0),
                'modalidad': 'PRESENCIAL',
                'ubicacion': 'Laboratorio de Cómputo — Bloque 5',
                'activo':    True,
            },
        )
        self.stdout.write(f'    Sofia Vargas (monitor): {"CREADO" if created else "ya existe"}')

        # ── 5. ADMIN ─────────────────────────────────────────────────
        self.stdout.write('  Creando administrador…')
        admin_user, created = Usuario.objects.get_or_create(
            email='admin@unisimon.edu.co',
            defaults={
                'first_name': 'Admin',
                'last_name':  'MonitorHub',
                'rol':        'ADMINISTRADOR',
                'is_staff':   True,
                'is_superuser': True,
                'is_active':  True,
            },
        )
        if created:
            admin_user.set_password('admin123')
            admin_user.save()
            self.stdout.write('    Admin creado: admin@unisimon.edu.co / admin123')
        else:
            self.stdout.write('    Admin ya existe')

        # ── Summary ──────────────────────────────────────────────────
        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS('Datos de prueba cargados exitosamente'))
        self.stdout.write('')
        self.stdout.write('Credenciales de acceso:')
        self.stdout.write('  ADMIN        : admin@unisimon.edu.co / admin123')
        self.stdout.write('  MONITOR 1    : p_martinez@unisimon.edu.co / monitor123')
        self.stdout.write('  MONITOR 2    : s_vargas@unisimon.edu.co / monitor123')
        self.stdout.write('  ESTUDIANTE 1 : c_perez@unisimon.edu.co / estudiante123')
        self.stdout.write('  ESTUDIANTE 2 : a_gomez@unisimon.edu.co / estudiante123')
        self.stdout.write('  ESTUDIANTE 3 : l_torres@unisimon.edu.co / estudiante123')
        self.stdout.write('  DOCENTE      : r_rodriguez@unisimon.edu.co / docente123')
