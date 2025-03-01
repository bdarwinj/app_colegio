import tkinter as tk
from tkinter import ttk

class AdminPanel(ttk.LabelFrame):
    def __init__(self, parent, config_command, payment_command, courses_command, users_command):
        super().__init__(parent, text="Panel de Administración")
        self.config_command = config_command
        self.payment_command = payment_command
        self.courses_command = courses_command
        self.users_command = users_command
        self.create_widgets()

    def create_widgets(self):
        self.btn_config = ttk.Button(self, text="Editar Configuración", command=self.config_command)
        self.btn_config.pack(side="left", padx=5, pady=5)
        self.btn_registrar_pago = ttk.Button(self, text="Registrar Pago", command=self.payment_command)
        self.btn_registrar_pago.pack(side="left", padx=5, pady=5)
        self.btn_cursos = ttk.Button(self, text="Administrar Cursos", command=self.courses_command)
        self.btn_cursos.pack(side="left", padx=5, pady=5)
        self.btn_usuarios = ttk.Button(self, text="Administrar Usuarios", command=self.users_command)
        self.btn_usuarios.pack(side="left", padx=5, pady=5)