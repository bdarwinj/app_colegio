import logging
import sys

def setup_logger():
    # Configura el logger para que se muestren todos los eventos desde DEBUG en adelante
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)

    # Crear manejador para salida a consola
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.DEBUG)
    
    # Establecer el formato para los mensajes de log
    formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(name)s - %(message)s',
        "%Y-%m-%d %H:%M:%S"
    )
    console_handler.setFormatter(formatter)
    
    # Evitar agregar múltiples manejadores si ya se han configurado
    if not logger.handlers:
        logger.addHandler(console_handler)