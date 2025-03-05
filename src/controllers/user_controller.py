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

    def _execute_fetchone(self, query, params, error_context):
        """
        Ejecuta una consulta que retorna una única fila.
        """
        try:
            with db_cursor(self.db) as cursor:
                cursor.execute(query, params)
                return cursor.fetchone()
        except sqlite3.Error as e:
            logger.error(f"{error_context}: {e}")
            return None

    def _create_user_object(self, username, role):
        """
        Crea y retorna un objeto de usuario dinámico con los atributos username y role.
        """
        user = type("User", (), {})()
        user.username = username
        user.role = role
        return user

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

        # Intentar obtener el usuario por username
        query = "SELECT username, role, password FROM users WHERE username = ?"
        row = self._execute_fetchone(query, (username,), "Error de base de datos durante el login")
        if row:
            stored_hash = row[2]
            # Verificar la contraseña usando bcrypt
            if bcrypt.checkpw(password.encode('utf-8'), stored_hash.encode('utf-8')):
                return self._create_user_object(row[0], row[1])
        else:
            # Si ocurre error en el query o no se encontró el usuario, se continúa con el fallback.
            pass

        # Fallback: solo se aplica si no existe ningún usuario admin en la base de datos
        query = "SELECT COUNT(*) FROM users WHERE username = 'admin'"
        count_row = self._execute_fetchone(query, (), "Error en fallback de login")
        if count_row and count_row[0] == 0:
            # Solo se permite si no existe un admin configurado
            if username == "admin" and password == "admin":
                return self._create_user_object("admin", "admin")
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

        query = "SELECT password FROM users WHERE username = ?"
        row = self._execute_fetchone(query, (username,), "Error de base de datos al cambiar clave")
        if not row:
            return False, "Usuario no encontrado."
        stored_hash = row[0]
        if not bcrypt.checkpw(old_password.encode('utf-8'), stored_hash.encode('utf-8')):
            return False, "La clave actual ingresada es incorrecta."
        try:
            # Hash de la nueva contraseña
            hashed_new_password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            update_query = "UPDATE users SET password = ? WHERE username = ?"
            with db_cursor(self.db) as cursor:
                cursor.execute(update_query, (hashed_new_password, username))
            return True, "Clave actualizada correctamente."
        except sqlite3.Error as e:
            logger.error(f"Error de base de datos al cambiar clave: {e}")
            return False, f"Error al cambiar clave: {e}"
   
    def update_user_password(self, username, new_password):
            """
            Permite al administrador cambiar la contraseña de un usuario sin necesidad de la contraseña antigua.
            """
            if not isinstance(username, str) or not username:
                return False, "El username debe ser una cadena no vacía."
            if not isinstance(new_password, str) or not new_password:
                return False, "La nueva contraseña debe ser una cadena no vacía."
            try:
                hashed_new_password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
                query = "UPDATE users SET password = ? WHERE username = ?"
                with db_cursor(self.db) as cursor:
                    cursor.execute(query, (hashed_new_password, username))
                return True, "Contraseña actualizada correctamente."
            except sqlite3.Error as e:
                logger.error(f"Error al actualizar la contraseña para {username}: {e}")
                return False, f"Error al actualizar la contraseña: {e}"