import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

# Параметры подключения к серверу PostgreSQL (обычно к базе postgres)
conn = psycopg2.connect(
    dbname='postgres',
    user='postgres',         # Замените на имя суперпользователя PostgreSQL
    password='904296',   # Замените на пароль суперпользователя
    host='localhost'
)
conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
cur = conn.cursor()

# Создание базы данных
try:
    cur.execute("CREATE DATABASE efs_db;")
    print("База данных efs_db создана.")
except psycopg2.errors.DuplicateDatabase:
    print("База данных efs_db уже существует.")

# Создание пользователя
try:
    cur.execute("CREATE USER efs_user WITH PASSWORD 'efs_password';")
    print("Пользователь efs_user создан.")
except psycopg2.errors.DuplicateObject:
    print("Пользователь efs_user уже существует.")

# Назначение прав
cur.execute("GRANT ALL PRIVILEGES ON DATABASE efs_db TO efs_user;")
print("Права назначены.")

cur.close()
conn.close() 