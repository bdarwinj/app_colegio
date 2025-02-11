from src.models.user import User

class UserController:
    def __init__(self, db):
        self.db = db

    def login(self, username, password):
        query = "SELECT id, username, role FROM users WHERE username = ? AND password = ?"
        self.db.cursor.execute(query, (username, password))
        row = self.db.cursor.fetchone()
        if row:
            return User(row[0], row[1], row[2])
        else:
            return None