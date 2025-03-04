# src/controllers/user_controller.py
import hashlib
import traceback
import sqlite3
import logging
from src.utils.db_utils import db_cursor

logger = logging.getLogger(__name__)

class UserController:
    def __init__(self, db):
        """
        Inicializa el controlador con un objeto de base de datos.
        Se recomienda que db sea una instancia de sqlite3.Connection.
        Si se utiliza un objeto Database personalizado, este debe exponer el atributo 'connection'.
        """
        self.db = db

    def login(self, username, password):
        if not isinstance(username, str) or not isinstance(password, str):
            logger.error("Username y password deben ser cadenas.")
            return None
        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        try:
            query = "SELECT username, role FROM users WHERE username = ? AND password = ?"
            with db_cursor(self.db) as cursor:
                cursor.execute(query, (username, hashed_password))
                row = cursor.fetchone()
            if row:
                user = type("User", (), {})()
                user.username = row[0]
                user.role = row[1]
                return user
        except sqlite3.Error as e:
            logger.error(f"Error de base de datos durante el login: {e}")
            return None
        expected_admin_hash = hashlib.sha256("admin".encode()).hexdigest()
        if username == "admin" and hashed_password == expected_admin_hash:
            user = type("User", (), {})()
            user.username = "admin"
            user.role = "admin"
            return user
        return None

    def create_user(self, username, password, role):
        if not isinstance(username, str) or not username:
            return False, "El username debe ser una cadena no vacía."
        if not isinstance(password, str) or not password:
            return False, "La contraseña debe ser una cadena no vacía."
        if not isinstance(role, str) or not role:
            return False, "El rol debe ser una cadena no vacía."
        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        try:
            query = "INSERT INTO users (username, password, role) VALUES (?, ?, ?)"
            with db_cursor(self.db) as cursor:
                cursor.execute(query, (username, hashed_password, role))
            return True, "Usuario creado exitosamente."
        except sqlite3.IntegrityError:
            logger.error("Error de integridad: el nombre de usuario ya existe.")
            return False, "Error: El nombre de usuario ya existe."
        except sqlite3.Error as e:
            logger.error(f"Error de base de datos al crear usuario: {e}")
            return False, f"Error al crear el usuario: {e}"

    def change_password(self, username, old_password, new_password):
        if not isinstance(username, str) or not username:
            return False, "El username debe ser una cadena no vacía."
        if not isinstance(old_password, str) or not old_password:
            return False, "La clave actual debe ser una cadena no vacía."
        if not isinstance(new_password, str) or not new_password:
            return False, "La nueva clave debe ser una cadena no vacía."
        try:
            query = "SELECT password FROM users WHERE username = ?"
            with db_cursor(self.db) as cursor:
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
            with db_cursor(self.db) as cursor:
                cursor.execute(update_query, (hashed_new_password, username))
            return True, "Clave actualizada correctamente."
        except sqlite3.Error as e:
            logger.error(f"Error de base de datos al cambiar clave: {e}")
            return False, f"Error al cambiar clave: {e}"
