import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import os
from pathlib import Path
from src.controllers.user_controller import UserController
from src.controllers.config_controller import ConfigController

class LoginUI:
    """
    Interfaz de usuario para la pantalla de inicio de sesión.
    """
    def __init__(self, db):
        """
        Inicializa la interfaz de usuario de inicio de sesión.

        Args:
            db: La conexión a la base de datos.
        """
        self.db = db
        self.user_controller = UserController(self.db)
        self.config_controller = ConfigController(self.db)
        self.root = tk.Tk()
        self.root.title("Login - Sistema Colegio")
        self.root.geometry("400x350")
        self.center_window(400, 350)
        self.load_config()  # Cargar la configuración al inicio
        self.create_widgets()
        self.entry_username.focus_set()

    def load_config(self):
        """Carga la configuración de la base de datos."""
        configs = self.config_controller.get_all_configs()
        self.school_name = configs.get("SCHOOL_NAME", "Colegio Ejemplo")
        self.logo_path = configs.get("LOGO_PATH", "logo.png")
        self.abs_logo_path = Path(self.logo_path).resolve()

    def center_window(self, width, height):
        """
        Centra la ventana en la pantalla.

        Args:
            width: Ancho de la ventana.
            height: Alto de la ventana.
        """
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width // 2) - (width // 2)
        y = (screen_height // 2) - (height // 2)
        self.root.geometry(f"{width}x{height}+{x}+{y}")

    def create_widgets(self):
        """Crea los widgets de la interfaz de inicio de sesión."""
        header_frame = ttk.Frame(self.root)
        header_frame.pack(pady=10)

        # Mostrar el logo si existe, o un logo de reemplazo
        if os.path.exists(str(self.abs_logo_path)):
            try:
                image = Image.open(self.abs_logo_path)
                image = image.resize((80, 80), Image.LANCZOS)
                self.logo = ImageTk.PhotoImage(image)
                ttk.Label(header_frame, image=self.logo).pack()
            except Exception as e:
                print(f"Error al cargar el logo: {e}")
                self.show_placeholder_logo(header_frame)
        else:
            print(f"No se encontró la imagen en: {self.abs_logo_path}")
            self.show_placeholder_logo(header_frame)

        ttk.Label(header_frame, text=self.school_name, font=("Arial", 16, "bold")).pack(pady=5)

        form_frame = ttk.Frame(self.root, padding=20)
        form_frame.pack(expand=True)
        ttk.Label(form_frame, text="Usuario:").grid(row=0, column=0, pady=5, sticky="w")
        self.entry_username = ttk.Entry(form_frame)
        self.entry_username.grid(row=0, column=1, pady=5)
        ttk.Label(form_frame, text="Contraseña:").grid(row=1, column=0, pady=5, sticky="w")
        self.entry_password = ttk.Entry(form_frame, show="*")
        self.entry_password.grid(row=1, column=1, pady=5)
        self.entry_password.bind("<Return>", lambda event: self.attempt_login())
        ttk.Button(form_frame, text="Iniciar Sesión", command=self.attempt_login)\
            .grid(row=2, column=0, columnspan=2, pady=10)

    def show_placeholder_logo(self, frame):
        """Muestra un logo de reemplazo o un mensaje en caso de error."""
        ttk.Label(frame, text="Logo no disponible", font=("Arial", 12)).pack()

    def attempt_login(self):
        """
        Intenta iniciar sesión con las credenciales ingresadas.
        """
        username = self.entry_username.get()
        password = self.entry_password.get()
        user = self.user_controller.login(username, password)
        if user:
            messagebox.showinfo("Éxito", f"Bienvenido, {user.username}!")
            self.root.destroy()
            from src.views.app_ui import AppUI
            app = AppUI(self.db, user)
            app.run()
        else:
            messagebox.showerror("Error", "Usuario o contraseña incorrectos.")

    def run(self):
        """Inicia el bucle principal de la interfaz de usuario."""
        self.root.mainloop()