import sqlite3


class SQLiteDB:
    def __init__(self, db_name) -> None:
        self.conn = sqlite3.connect(database=db_name)
        self.curor = self.conn.cursor()

    def create_table(self):
        """
        创建一个新表。
        """
        query = """--sql
        CREATE TABLE IF NOT EXISTS article(
            mask_id PRIMARY KEY,
            user_id TEXT,
        );
        
        
        """
