from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models


class UsuarioManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('El correo electrónico es obligatorio')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('rol', Usuario.Rol.ADMINISTRADOR)
        return self.create_user(email, password, **extra_fields)


class Usuario(AbstractUser):
    class Rol(models.TextChoices):
        ESTUDIANTE    = 'ESTUDIANTE',    'Estudiante'
        MONITOR       = 'MONITOR',       'Monitor'
        DOCENTE       = 'DOCENTE',       'Docente'
        ADMINISTRADOR = 'ADMINISTRADOR', 'Administrador'

    username       = None
    email          = models.EmailField(unique=True, verbose_name='Correo institucional')
    id_microsoft   = models.CharField(max_length=255, blank=True, verbose_name='ID Microsoft')
    rol            = models.CharField(max_length=20, choices=Rol.choices, default=Rol.ESTUDIANTE, verbose_name='Rol')
    activo         = models.BooleanField(default=True, verbose_name='Activo')
    fecha_creacion = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de creación')

    USERNAME_FIELD  = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    objects = UsuarioManager()

    class Meta:
        verbose_name        = 'Usuario'
        verbose_name_plural = 'Usuarios'
        ordering            = ['last_name', 'first_name']

    def __str__(self):
        return f"{self.get_full_name()} ({self.email})"

    @property
    def nombre_completo(self):
        return self.get_full_name()


class PerfilEstudiante(models.Model):
    usuario           = models.OneToOneField(Usuario, on_delete=models.CASCADE, related_name='perfil_estudiante')
    codigo_estudiante = models.CharField(max_length=20, unique=True, verbose_name='Código estudiantil')
    programa          = models.CharField(max_length=100, verbose_name='Programa académico')
    semestre          = models.PositiveIntegerField(verbose_name='Semestre')

    class Meta:
        verbose_name        = 'Perfil Estudiante'
        verbose_name_plural = 'Perfiles Estudiantes'

    def __str__(self):
        return f"{self.usuario.nombre_completo} — {self.programa} (Sem. {self.semestre})"


class PerfilDocente(models.Model):
    usuario      = models.OneToOneField(Usuario, on_delete=models.CASCADE, related_name='perfil_docente')
    departamento = models.CharField(max_length=100, verbose_name='Departamento')
    materias     = models.ManyToManyField('monitores.Materia', related_name='docentes', blank=True, verbose_name='Materias asignadas')

    class Meta:
        verbose_name        = 'Perfil Docente'
        verbose_name_plural = 'Perfiles Docentes'

    def __str__(self):
        return f"{self.usuario.nombre_completo} — {self.departamento}"
