import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import os
from src.controllers.user_controller import UserController
from src.controllers.config_controller import ConfigController
from src.views.app_ui import AppUI

class LoginUI:
    def __init__(self, db):
        self.db = db
        self.user_controller = UserController(self.db)
        self.config_controller = ConfigController(db)
        self.root = tk.Tk()
        self.root.title("Login - Sistema Colegio")
        self.root.geometry("400x350")
        self.create_widgets()

    def create_widgets(self):
        # Panel de cabecera: logo y nombre del colegio
        header_frame = ttk.Frame(self.root)
        header_frame.pack(pady=10)
        
        configs = self.config_controller.get_all_configs()
        school_name = configs.get("SCHOOL_NAME", "Colegio Ejemplo")
        logo_path = configs.get("LOGO_PATH", "logo.png")
        # Convertir a ruta absoluta
        abs_logo_path = os.path.abspath(logo_path)
        
        image_label = None
        if os.path.exists(abs_logo_path):
            try:
                image = Image.open(abs_logo_path)
                image = image.resize((80, 80), Image.LANCZOS)
                self.logo = ImageTk.PhotoImage(image)
                image_label = ttk.Label(header_frame, image=self.logo)
                image_label.pack()
            except Exception as e:
                print(f"Error al cargar el logo: {e}")
        else:
            print(f"No se encontró la imagen en: {abs_logo_path}")
        
        name_label = ttk.Label(header_frame, text=school_name, font=("Arial", 16, "bold"))
        name_label.pack(pady=5)
        
        # Frame de Login
        frame = ttk.Frame(self.root, padding=20)
        frame.pack(expand=True)

        ttk.Label(frame, text="Usuario:").grid(row=0, column=0, pady=5, sticky="w")
        self.entry_username = ttk.Entry(frame)
        self.entry_username.grid(row=0, column=1, pady=5)

        ttk.Label(frame, text="Contraseña:").grid(row=1, column=0, pady=5, sticky="w")
        self.entry_password = ttk.Entry(frame, show="*")
        self.entry_password.grid(row=1, column=1, pady=5)

        self.btn_login = ttk.Button(frame, text="Iniciar Sesión", command=self.attempt_login)
        self.btn_login.grid(row=2, column=0, columnspan=2, pady=10)

    def attempt_login(self):
        username = self.entry_username.get()
        password = self.entry_password.get()
        user = self.user_controller.login(username, password)
        if user:
            messagebox.showinfo("Éxito", f"Bienvenido, {user.username}!")
            self.root.destroy()
            # Inicia la interfaz principal pasando el usuario logueado
            app = AppUI(self.db, user)
            app.run()
        else:
            messagebox.showerror("Error", "Usuario o contraseña incorrectos.")

    def run(self):
        self.root.mainloop()