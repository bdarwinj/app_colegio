from src.views.login_ui import LoginUI
from src.models.database import Database
from config import DB_NAME, SCHOOL_NAME, LOGO_PATH
from src.controllers.config_controller import ConfigController

def main():
    # Inicializa la base de datos y crea tablas (incluye la tabla config)
    db = Database(DB_NAME)
    db.create_tables()
    
    # Inserta usuarios de prueba, si no existen
    db.cursor.execute("SELECT COUNT(*) FROM users")
    if db.cursor.fetchone()[0] == 0:
        db.cursor.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)", ("admin", "admin", "admin"))
        db.cursor.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)", ("operador", "operador", "operator"))
        db.connection.commit()
    
    # Inicializa la configuración predeterminada en la tabla config si aún no existe
    config_ctrl = ConfigController(db)
    config_ctrl.initialize_default_configs({
        "SCHOOL_NAME": SCHOOL_NAME,
        "LOGO_PATH": LOGO_PATH
    })

    # Lanza la ventana de login
    login_window = LoginUI(db)
    login_window.run()

if __name__ == '__main__':
    main()