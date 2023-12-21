import mysql.connector

db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'database': 'moneypad'
}
def get_db():
    return mysql.connector.connect(**db_config)

