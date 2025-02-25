from src.views.login_ui import LoginUI
from src.models.database import Database
from config import DB_NAME, SCHOOL_NAME, LOGO_PATH
from src.controllers.config_controller import ConfigController
from src.controllers.user_controller import UserController
from src.logger import logger  # Importamos nuestro logger personalizado
from tkinter import Tk

def main():
    logger.info("Inicializando la aplicación...")
    
    # Inicialización de la base de datos
    db = Database(DB_NAME)
    db.create_tables()
    
    # Instanciar el UserController
    user_controller = UserController(db)
    
    # Verificar si hay usuarios en la base de datos
    cursor = db.cursor
    cursor.execute("SELECT COUNT(*) FROM users")
    user_count = cursor.fetchone()[0]
    
    # Si no hay usuarios, solicitar configurar la contraseña del administrador
    if user_count == 0:
        logger.info("Primera vez que se ejecuta la aplicación. Se requiere establecer una contraseña para el administrador.")
        root = Tk()
        root.withdraw()  # Oculta la ventana principal
        from src.views.initial_setup_ui import InitialSetupUI
        setup_ui = InitialSetupUI(root, user_controller)
        root.wait_window(setup_ui.window)
        root.destroy()
    
    # (Opcional) Insertar usuario operador si no existe
    cursor.execute("SELECT COUNT(*) FROM users WHERE role = 'operator'")
    if cursor.fetchone()[0] == 0:
        logger.info("Insertando usuario operador de prueba.")
        user_controller.create_user("operador", "operador", "operator")
    
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
