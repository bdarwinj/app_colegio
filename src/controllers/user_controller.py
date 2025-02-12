import hashlib
import traceback
import sqlite3
import logging

logger = logging.getLogger(__name__)

class UserController:
    def __init__(self, db):
        """
        Initialize the controller with a database object.
        It is recommended that db is a sqlite3.Connection.
        If using a custom Database object, it should expose a 'connection' attribute.
        """
        self.db = db

    def get_cursor(self):
        """
        Returns a valid cursor from the database.
        """
        if hasattr(self.db, "cursor") and callable(self.db.cursor):
            return self.db.cursor()
        elif hasattr(self.db, "connection"):
            return self.db.connection.cursor()
        else:
            raise AttributeError("El objeto de base de datos no tiene un cursor válido.")

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
            cursor = self.get_cursor()
            query = "SELECT username, role FROM users WHERE username = ? AND password = ?"
            cursor.execute(query, (username, hashed_password))
            row = cursor.fetchone()

            if row:
                user = type("User", (), {})()
                user.username = row[0]
                user.role = row[1]
                return user

        except Exception:
            logger.exception("Error during login:")

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
            cursor = self.get_cursor()
            query = "INSERT INTO users (username, password, role) VALUES (?, ?, ?)"
            cursor.execute(query, (username, hashed_password, role))

            if hasattr(self.db, "commit") and callable(self.db.commit):
                self.db.commit()
            elif hasattr(self.db, "connection") and hasattr(self.db.connection, "commit") and callable(self.db.connection.commit):
                self.db.connection.commit()

            return True, "Usuario creado exitosamente."
        except sqlite3.IntegrityError:
            logger.exception("Error al crear el usuario:")
            return False, "Error: El nombre de usuario ya existe."
        except Exception as e:
            logger.exception("Error al crear el usuario:")
            return False, f"Error al crear el usuario: {e}"

    def change_password(self, username, old_password, new_password):
        """
        Changes the password for the given username.
        Hashes are used to verify the old password and update it with the new password's hash.
        Returns a tuple (success, message).
        """
        try:
            cursor = self.get_cursor()
            query = "SELECT password FROM users WHERE username = ?"
            cursor.execute(query, (username,))
            row = cursor.fetchone()
            if not row:
                return False, "Usuario no encontrado."
            
            current_password = row[0]
            hashed_old_password = hashlib.sha256(old_password.encode()).hexdigest()
            if current_password != hashed_old_password:
                return False, "La clave actual ingresada es incorrecta."
            
            hashed_new_password = hashlib.sha256(new_password.encode()).hexdigest()
            update_query = "UPDATE users SET password = ? WHERE username = ?"
            cursor.execute(update_query, (hashed_new_password, username))
            
            if hasattr(self.db, "commit") and callable(self.db.commit):
                self.db.commit()
            elif hasattr(self.db, "connection") and hasattr(self.db.connection, "commit") and callable(self.db.connection.commit):
                self.db.connection.commit()
                
            return True, "Clave actualizada correctamente."
        except Exception as e:
            logger.exception("Error al cambiar clave:")
            return False, f"Error al cambiar clave: {e}"