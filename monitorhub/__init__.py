# PyMySQL como fallback para MySQL en producción universitaria
# No se usa en Vercel/Neon (PostgreSQL)
try:
    import pymysql
    pymysql.install_as_MySQLdb()
except ImportError:
    pass
