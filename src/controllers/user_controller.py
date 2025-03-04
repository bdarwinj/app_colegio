# src/controllers/user_controller.py
import bcrypt
import sqlite3
from src.utils.db_utils import db_cursor
from src.logger import logger

class UserController:
    def __init__(self, db):
        """
        Inicializa el controlador con un objeto de base de datos.
        Se recomienda que db sea una instancia de sqlite3.Connection.
        Si se utiliza un objeto Database personalizado, este debe exponer el atributo 'connection'.
        """
        self.db = db

    def login(self, username, password):
        """
        Intenta iniciar sesión comparando el username y la contraseña (hasheada)
        con los registros de la tabla 'users'. 
        Si no se encuentra un registro y no existe un usuario admin en la base de datos,
        se permite el login con las credenciales por defecto ("admin", "admin").
        """
        if not isinstance(username, str) or not isinstance(password, str):
            logger.error("Username y password deben ser cadenas.")
            return None

        try:
            query = "SELECT username, role, password FROM users WHERE username = ?"
            with db_cursor(self.db) as cursor:
                cursor.execute(query, (username,))
                row = cursor.fetchone()

            if row:
                stored_hash = row[2]
                # Verificar la contraseña usando bcrypt
                if bcrypt.checkpw(password.encode('utf-8'), stored_hash.encode('utf-8')):
                    user = type("User", (), {})()
                    user.username = row[0]
                    user.role = row[1]
                    return user
        except sqlite3.Error as e:
            logger.error(f"Error de base de datos durante el login: {e}")
            return None

        # Fallback: Solo se aplica si no existe ningún usuario admin en la base de datos
        try:
            query = "SELECT COUNT(*) FROM users WHERE username = 'admin'"
            with db_cursor(self.db) as cursor:
                cursor.execute(query)
                count = cursor.fetchone()[0]
            if count == 0:
                # Solo se permite si no existe un admin configurado
                # Verificar que la contraseña ingresada es "admin"
                if username == "admin" and password == "admin":
                    user = type("User", (), {})()
                    user.username = "admin"
                    user.role = "admin"
                    return user
        except sqlite3.Error as e:
            logger.error(f"Error en fallback de login: {e}")

        return None

    def create_user(self, username, password, role):
        """
        Crea un nuevo usuario en la tabla 'users' con el username, contraseña y rol dados.
        La contraseña se almacena usando bcrypt para mayor seguridad.
        """
        if not isinstance(username, str) or not username:
            return False, "El username debe ser una cadena no vacía."
        if not isinstance(password, str) or not password:
            return False, "La contraseña debe ser una cadena no vacía."
        if not isinstance(role, str) or not role:
            return False, "El rol debe ser una cadena no vacía."

        try:
            # Hash de la contraseña usando bcrypt; se almacena como cadena
            hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
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
        """
        Cambia la contraseña para el usuario dado.
        Verifica que la contraseña antigua sea correcta usando bcrypt y actualiza con la nueva contraseña hasheada.
        """
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
            stored_hash = row[0]
            if not bcrypt.checkpw(old_password.encode('utf-8'), stored_hash.encode('utf-8')):
                return False, "La clave actual ingresada es incorrecta."
            # Hash de la nueva contraseña
            hashed_new_password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            update_query = "UPDATE users SET password = ? WHERE username = ?"
            with db_cursor(self.db) as cursor:
                cursor.execute(update_query, (hashed_new_password, username))
            return True, "Clave actualizada correctamente."
        except sqlite3.Error as e:
            logger.error(f"Error de base de datos al cambiar clave: {e}")
            return False, f"Error al cambiar clave: {e}"