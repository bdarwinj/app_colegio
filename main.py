from src.views.login_ui import LoginUI
from src.models.database import Database
from config import DB_NAME, SCHOOL_NAME, LOGO_PATH
from src.controllers.config_controller import ConfigController
from src.logger import logger  # Import our custom logger

def main():
    logger.info("Inicializando la aplicación...")

    # Inicializa la base de datos y crea las tablas, incluyendo la tabla de configuración
    db = Database(DB_NAME)
    db.create_tables()
    
    # Inserta usuarios de prueba, si no existen
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
    
    # Inicializa la configuración predeterminada en la tabla config si aún no existe
    config_ctrl = ConfigController(db)
    config_ctrl.initialize_default_configs({
        "SCHOOL_NAME": SCHOOL_NAME,
        "LOGO_PATH": LOGO_PATH
    })
    logger.info("Configuración inicializada.")

    # Lanza la ventana de login
    login_window = LoginUI(db)
    login_window.run()

if __name__ == '__main__':
    main()