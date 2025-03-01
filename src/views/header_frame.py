import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import os
import logging

class HeaderFrame(ttk.Frame):
    def __init__(self, parent, school_name, abs_logo_path, change_password_command, logout_command):
        super().__init__(parent)
        self.school_name = school_name
        self.abs_logo_path = abs_logo_path
        self.change_password_command = change_password_command
        self.logout_command = logout_command
        self.create_widgets()

    def create_widgets(self):
        self.logo_image = self._load_logo(self)
        name_label = ttk.Label(self, text=f"{self.school_name} - Sistema de Pagos", font=("Arial", 18, "bold"))
        name_label.pack(side="left", padx=10)
        
        btn_change_password = ttk.Button(self, text="Cambiar Clave", command=self.change_password_command)
        btn_change_password.pack(side="right", padx=10)
        btn_logout = ttk.Button(self, text="Cerrar Sesión", command=self.logout_command)
        btn_logout.pack(side="right", padx=10)

    def _load_logo(self, parent):
        if os.path.exists(self.abs_logo_path):
            try:
                image = Image.open(self.abs_logo_path)
                image = image.resize((80, 80), Image.LANCZOS)
                logo_image = ImageTk.PhotoImage(image)
                logo_label = ttk.Label(parent, image=logo_image)
                logo_label.pack(side="left", padx=5)
                return logo_image
            except Exception as e:
                logging.error(f"Error al cargar el logo: {e}")
                return None
        else:
            logging.warning(f"No se encontró la imagen en: {self.abs_logo_path}")
            return None