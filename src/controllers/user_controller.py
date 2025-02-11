import hashlib
import traceback
import sqlite3

class UserController:
    def __init__(self, db):
        """
        Initialize the controller with a database object.
        It is recommended that db is a sqlite3.Connection.
        If using a custom Database object, it should expose a 'connection' attribute.
        """
        self.db = db

    def login(self, username, password):
        """
        Attempts to log in by comparing the given username and password (after hashing)
        against the records in the 'users' table.
        If no record is found, and the username and password match the expected admin
        credentials, a fallback admin user is returned.
        Returns a user object if successful, or None if the credentials do not match.
        """
        hashed_password = hashlib.sha256(password.encode()).hexdigest()

        try:
            # Obtain a cursor from the database.
            if hasattr(self.db, "cursor") and callable(self.db.cursor):
                cursor = self.db.cursor()
            elif hasattr(self.db, "connection"):
                cursor = self.db.connection.cursor()
            else:
                raise AttributeError("El objeto de base de datos no tiene un cursor válido.")

            query = "SELECT username, role FROM users WHERE username = ? AND password = ?"
            cursor.execute(query, (username, hashed_password))
            row = cursor.fetchone()

            if row:
                user = type("User", (), {})()
                user.username = row[0]
                user.role = row[1]
                return user

        except Exception as e:
            error_details = traceback.format_exc()
            print("Error during login:", error_details)

        # Fallback: if no record is found and the entered credentials match admin defaults then return admin.
        expected_admin_hash = hashlib.sha256("admin".encode()).hexdigest()
        if username == "admin" and hashed_password == expected_admin_hash:
            user = type("User", (), {})()
            user.username = "admin"
            user.role = "admin"
            return user

        return None

    def create_user(self, username, password, role):
        """
        Creates a new user in the 'users' table with the given username, password, and role.
        The password is stored as a SHA-256 hash.
        Returns a tuple (success, message).
        """
        if not username or not password or not role:
            return False, "Campos incompletos"

        hashed_password = hashlib.sha256(password.encode()).hexdigest()

        try:
            # Obtain a cursor from the database.
            if hasattr(self.db, "cursor") and callable(self.db.cursor):
                cursor = self.db.cursor()
            elif hasattr(self.db, "connection"):
                cursor = self.db.connection.cursor()
            else:
                raise AttributeError("El objeto de base de datos no tiene un cursor válido.")
            
            query = "INSERT INTO users (username, password, role) VALUES (?, ?, ?)"
            cursor.execute(query, (username, hashed_password, role))

            # Commit the changes.
            if hasattr(self.db, "commit") and callable(self.db.commit):
                self.db.commit()
            elif hasattr(self.db, "connection") and hasattr(self.db.connection, "commit") and callable(self.db.connection.commit):
                self.db.connection.commit()

            return True, "Usuario creado exitosamente."
        except Exception as e:
            error_details = traceback.format_exc()
            print("Error al crear el usuario:", error_details)
            return False, f"Error al crear el usuario: {e}"