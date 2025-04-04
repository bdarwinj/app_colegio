class ConfigController:
    def __init__(self, db):
        self.db = db

    def initialize_default_configs(self, defaults: dict):
        """
        Inserta los valores predeterminados en la tabla config si no existen aún.
        """
        for key, value in defaults.items():
            self.db.cursor.execute("SELECT COUNT(*) FROM config WHERE key = ?", (key,))
            count = self.db.cursor.fetchone()[0]
            if count == 0:
                self.db.cursor.execute("INSERT INTO config (key, value) VALUES (?, ?)", (key, value))
        self.db.connection.commit()

    def get_config(self, key):
        query = "SELECT value FROM config WHERE key = ?"
        self.db.cursor.execute(query, (key,))
        row = self.db.cursor.fetchone()
        return row["value"] if row else None

    def get_all_configs(self):
        query = "SELECT key, value FROM config"
        self.db.cursor.execute(query)
        return dict((row["key"], row["value"]) for row in self.db.cursor.fetchall())

    def update_config(self, key, value):
        try:
            query = "UPDATE config SET value = ? WHERE key = ?"
            self.db.cursor.execute(query, (value, key))
            self.db.connection.commit()
            return True, "Configuración actualizada correctamente."
        except Exception as e:
            return False, f"Error al actualizar la configuración: {e}"