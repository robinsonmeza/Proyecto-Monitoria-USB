import pymysql

# Registra PyMySQL como sustituto de mysqlclient (necesario para producción con MySQL)
pymysql.install_as_MySQLdb()
