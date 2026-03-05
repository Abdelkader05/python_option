import sqlite3
import os
from app.database import init_database, get_db_connection




if os.path.exists('platonAAV.db'):
    os.remove('platonAAV.db')


init_database()


with open("../RessourcesCommunes-20260304/donnees_test.sql", "r") as f:
    sql_script = f.read()


with get_db_connection() as conn:
    cursor = conn.cursor()

    conn.executescript(sql_script)

    conn.commit()

conn.close()