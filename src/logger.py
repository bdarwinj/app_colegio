import logging

# Create a logger for your application.
logger = logging.getLogger("colegio_app")
logger.setLevel(logging.DEBUG)

# Create a console handler that outputs debug messages.
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)

# Create a formatter that includes the time, severity, logger name, and message.
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(name)s - %(message)s")
console_handler.setFormatter(formatter)

# Add the console handler to the logger.
logger.addHandler(console_handler)