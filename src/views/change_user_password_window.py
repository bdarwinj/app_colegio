# src/views/change_user_password_window.py
import tkinter as tk
from tkinter import ttk, messagebox
from src.controllers.user_controller import UserController

class ChangeUserPasswordWindow(tk.Toplevel):
    def __init__(self, master, username, user_controller):
        """
        Ventana para que el administrador cambie la contraseña de un usuario.
        :param master: Ventana padre.
        :param username: Nombre de usuario del usuario a modificar.
        :param user_controller: Instancia de UserController.
        """
        super().__init__(master)
        self.username = username
        self.user_controller = user_controller
        self.title(f"Cambiar contraseña para {username}")
        self.geometry("400x250")
        self.create_widgets()

    def create_widgets(self):
        frame = ttk.Frame(self, padding="20")
        frame.pack(expand=True, fill="both")
        
        ttk.Label(frame, text="Nueva Contraseña:").grid(row=0, column=0, sticky="w", pady=5)
        self.new_password_entry = ttk.Entry(frame, show="*")
        self.new_password_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        
        ttk.Label(frame, text="Confirmar Nueva Contraseña:").grid(row=1, column=0, sticky="w", pady=5)
        self.confirm_password_entry = ttk.Entry(frame, show="*")
        self.confirm_password_entry.grid(row=1, column=1, padx=5, pady=5, sticky="ew")
        
        self.change_password_button = ttk.Button(frame, text="Cambiar Contraseña", command=self.change_password)
        self.change_password_button.grid(row=2, column=0, columnspan=2, pady=20)
        
        frame.columnconfigure(1, weight=1)

    def change_password(self):
        new_password = self.new_password_entry.get().strip()
        confirm_password = self.confirm_password_entry.get().strip()
        
        if not new_password or not confirm_password:
            messagebox.showerror("Error", "Todos los campos son obligatorios.")
            return
        if new_password != confirm_password:
            messagebox.showerror("Error", "Las contraseñas no coinciden.")
            return
        
        success, msg = self.user_controller.update_user_password(self.username, new_password)
        if success:
            messagebox.showinfo("Éxito", msg)
            self.destroy()
        else:
            messagebox.showerror("Error", msg)