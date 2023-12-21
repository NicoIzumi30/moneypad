from config.config import get_db

conn = get_db()

class Income:
    def __init__(self, user_id, nominal, source_type, note, date, id=None):
        self.user_id = user_id
        self.nominal = nominal
        self.source_type = source_type
        self.note = note
        self.date = date
        self.id = id

    def save(self):
        cursor = conn.cursor()
        sql = """INSERT INTO income (user_id, nominal, source_type, note, date) VALUES (%s, %s, %s, %s, %s)"""
        cursor.execute(sql, (self.user_id, self.nominal, self.source_type, self.note, self.date))
        conn.commit()
        
    def update(self):
        cursor = conn.cursor()
        sql = """UPDATE income SET user_id=%s, nominal=%s, source_type=%s, note=%s, date=%s WHERE id=%s"""
        cursor.execute(sql, (self.user_id, self.nominal, self.source_type, self.note, self.date, self.id))
        conn.commit()

    def delete(self, id):
        cursor = conn.cursor()
        sql = """DELETE FROM income WHERE id=%s"""
        cursor.execute(sql, (id,))
        conn.commit()
        cursor.close()