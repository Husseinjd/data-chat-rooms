from sqlalchemy import create_engine

class DatabaseConnection:
    def __init__(self):
        self.engine = None

    def connect(self, username, password, db_name):
        connection_string = f"postgresql://{username}:{password}@localhost:5432/{db_name}"
        self.engine = create_engine(connection_string)
        return self.engine

    def test_connection(self):
        if not self.engine:
            raise ValueError("Database not connected. Call connect() first.")
        try:
            with self.engine.connect():
                return True
        except Exception as e:
            return str(e)