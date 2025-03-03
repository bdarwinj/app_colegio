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
        self.cursor = self.get_cursor()  # Cursor persistente inicializado una vez

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

    def _commit(self):
        """
        Commits changes to the database.
        """
        if hasattr(self.db, "commit") and callable(self.db.commit):
            self.db.commit()
        elif hasattr(self.db, "connection") and hasattr(self.db.connection, "commit") and callable(self.db.connection.commit):
            self.db.connection.commit()

    def login(self, username, password):
        """
        Attempts to log in by comparing the given username and password (after hashing)
        against the records in the 'users' table.
        If no record is found, and the username and password match the expected admin
        credentials, a fallback admin user is returned.
        Returns a user object if successful, or None if the credentials do not match.
        """
        # Validar tipos de entrada
        if not isinstance(username, str) or not isinstance(password, str):
            logger.error("Username y password deben ser cadenas.")
            return None

        hashed_password = hashlib.sha256(password.encode()).hexdigest()

        try:
            query = "SELECT username, role FROM users WHERE username = ? AND password = ?"
            self.cursor.execute(query, (username, hashed_password))
            row = self.cursor.fetchone()

            if row:
                user = type("User", (), {})()
                user.username = row[0]
                user.role = row[1]
                return user

        except sqlite3.Error as e:
            logger.error(f"Error de base de datos durante el login: {e}")
            return None

        # Fallback: si no hay coincidencia, verificar credenciales de admin por defecto
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
        # Validar tipos y valores no vacíos
        if not isinstance(username, str) or not username:
            return False, "El username debe ser una cadena no vacía."
        if not isinstance(password, str) or not password:
            return False, "La contraseña debe ser una cadena no vacía."
        if not isinstance(role, str) or not role:
            return False, "El rol debe ser una cadena no vacía."

        hashed_password = hashlib.sha256(password.encode()).hexdigest()

        try:
            query = "INSERT INTO users (username, password, role) VALUES (?, ?, ?)"
            self.cursor.execute(query, (username, hashed_password, role))
            self._commit()
            return True, "Usuario creado exitosamente."
        except sqlite3.IntegrityError:
            logger.error("Error de integridad: el nombre de usuario ya existe.")
            return False, "Error: El nombre de usuario ya existe."
        except sqlite3.Error as e:
            logger.error(f"Error de base de datos al crear usuario: {e}")
            return False, f"Error al crear el usuario: {e}"

    def change_password(self, username, old_password, new_password):
        """
        Changes the password for the given username.
        Hashes are used to verify the old password and update it with the new password's hash.
        Returns a tuple (success, message).
        """
        # Validar tipos y valores no vacíos
        if not isinstance(username, str) or not username:
            return False, "El username debe ser una cadena no vacía."
        if not isinstance(old_password, str) or not old_password:
            return False, "La clave actual debe ser una cadena no vacía."
        if not isinstance(new_password, str) or not new_password:
            return False, "La nueva clave debe ser una cadena no vacía."

        try:
            query = "SELECT password FROM users WHERE username = ?"
            self.cursor.execute(query, (username,))
            row = self.cursor.fetchone()
            if not row:
                return False, "Usuario no encontrado."
            
            current_password = row[0]
            hashed_old_password = hashlib.sha256(old_password.encode()).hexdigest()
            if current_password != hashed_old_password:
                return False, "La clave actual ingresada es incorrecta."
            
            hashed_new_password = hashlib.sha256(new_password.encode()).hexdigest()
            update_query = "UPDATE users SET password = ? WHERE username = ?"
            self.cursor.execute(update_query, (hashed_new_password, username))
            self._commit()
            return True, "Clave actualizada correctamente."
        except sqlite3.Error as e:
            logger.error(f"Error de base de datos al cambiar clave: {e}")
            return False, f"Error al cambiar clave: {e}"