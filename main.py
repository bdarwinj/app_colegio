from src.views.login_ui import LoginUI
from src.models.database import Database
from config import DB_NAME, SCHOOL_NAME, LOGO_PATH
from src.controllers.config_controller import ConfigController
from src.logger import logger  # Importamos nuestro logger personalizado

def main():
    # Registro de inicio de la aplicación
    logger.info("Inicializando la aplicación...")

    # Inicialización de la base de datos
    db = Database(DB_NAME)
    # Creación de las tablas en la base de datos
    db.create_tables()
    
    # Verificación e inserción de usuarios de prueba
    cursor = db.cursor
    cursor.execute("SELECT COUNT(*) FROM users")
    if cursor.fetchone()[0] == 0:
        logger.info("Insertando usuarios de prueba.")
        cursor.execute(
            "INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
            ("admin", "admin", "admin")
        )
        cursor.execute(
            "INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
            ("operador", "operador", "operator")
        )
        db.connection.commit()
    
    # Inicialización de la configuración predeterminada
    config_ctrl = ConfigController(db)
    config_ctrl.initialize_default_configs({
        "SCHOOL_NAME": SCHOOL_NAME,
        "LOGO_PATH": LOGO_PATH
    })
    logger.info("Configuración inicializada.")

    # Lanzamiento de la ventana de login
    login_window = LoginUI(db)
    login_window.run()

if __name__ == '__main__':
    main()