import sqlite3
import traceback
from datetime import datetime

class PaymentController:
    def __init__(self, db):
        """
        Initialize the PaymentController with a database object.
        db is expected to be a sqlite3.Connection or a custom Database object exposing a connection attribute.
        This initialization ensures that the 'payments' table exists.
        """
        self.db = db
        self.initialize_payments_table()

    def initialize_payments_table(self):
        """
        Create the 'payments' table if it does not exist.
        """
        try:
            # Attempt to get a cursor from the db connection.
            if hasattr(self.db, "cursor") and callable(self.db.cursor):
                cursor = self.db.cursor()
            elif hasattr(self.db, "connection") and hasattr(self.db.connection, "cursor") and callable(self.db.connection.cursor):
                cursor = self.db.connection.cursor()
            else:
                raise AttributeError("El objeto de base de datos no proporciona un cursor válido mediante 'cursor()' o 'connection.cursor()'.")
            
            create_table_query = """
                CREATE TABLE IF NOT EXISTS payments (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    student_id INTEGER,
                    amount REAL,
                    description TEXT,
                    payment_date TEXT
                )
            """
            cursor.execute(create_table_query)
            # Commit the changes using the appropriate commit method.
            if hasattr(self.db, "commit") and callable(self.db.commit):
                self.db.commit()
            elif hasattr(self.db, "connection") and hasattr(self.db.connection, "commit") and callable(self.db.connection.commit):
                self.db.connection.commit()
        except Exception as e:
            detailed_error = traceback.format_exc()
            print("Error al inicializar la tabla 'payments':")
            print(detailed_error)

    def register_payment(self, student_id, amount, description):
        """
        Inserts a new payment record into the payments table.
        Returns a tuple: (success, message, receipt_number, payment_date)
        In case of errors, the full traceback will be printed to the console.
        """
        try:
            # Attempt to get a cursor from the db connection.
            if hasattr(self.db, "connection") and hasattr(self.db.connection, "cursor") and callable(self.db.connection.cursor):
                cursor = self.db.connection.cursor()
            elif hasattr(self.db, "cursor") and callable(self.db.cursor):
                cursor = self.db.cursor()
            else:
                raise AttributeError("El objeto de base de datos no proporciona un cursor válido mediante 'cursor()' o 'connection.cursor()'.")
            
            query = """
                INSERT INTO payments (student_id, amount, description, payment_date)
                VALUES (?, ?, ?, ?)
            """
            payment_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            cursor.execute(query, (student_id, amount, description, payment_date))
            
            # Commit changes using the appropriate commit method.
            if hasattr(self.db, "commit") and callable(self.db.commit):
                self.db.commit()
            elif hasattr(self.db, "connection") and hasattr(self.db.connection, "commit") and callable(self.db.connection.commit):
                self.db.connection.commit()
            else:
                # If no commit method is available, assume auto-commit or raise warning.
                print("Advertencia: No se encontró método commit, verifique la configuración de la base de datos.")
            
            receipt_number = cursor.lastrowid  # Retrieve the auto-incremented receipt number.
            return True, "Pago registrado exitosamente.", receipt_number, payment_date

        except Exception as e:
            # Capture and print the full traceback for debugging.
            detailed_error = traceback.format_exc()
            print("Error al registrar el pago:")
            print(detailed_error)
            return False, f"Error al registrar el pago: {e}", None, None