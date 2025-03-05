import os
import shutil
import datetime
from config import DB_NAME

def backup_database(backup_dir="backups"):
    """
    Crea una copia de seguridad de la base de datos.
    
    La copia se almacena en el directorio 'backup_dir' (se crea si no existe) y se nombra con la fecha y hora actuales.
    Retorna la ruta del archivo de backup creado.
    """
    os.makedirs(backup_dir, exist_ok=True)
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = os.path.join(backup_dir, f"backup_{timestamp}.db")
    shutil.copy(DB_NAME, backup_file)
    return backup_file

def restore_database(backup_file, destination=DB_NAME):
    """
    Restaura la base de datos a partir de un archivo de backup.
    
    :param backup_file: Ruta del archivo de backup.
    :param destination: Ruta de la base de datos a restaurar (por defecto, DB_NAME).
    """
    if not os.path.exists(backup_file):
        raise FileNotFoundError(f"No se encontró el archivo de backup: {backup_file}")
    shutil.copy(backup_file, destination)
