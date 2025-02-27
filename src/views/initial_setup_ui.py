import tkinter as tk
from tkinter import ttk, messagebox
import hashlib

class InitialSetupUI:
    def __init__(self, master, user_controller):
        """
        Ventana para la configuración inicial, en la que se solicita establecer la contraseña del administrador.
        :param master: la ventana raíz.
        :param user_controller: instancia de UserController para crear el usuario admin.
        """
        self.master = master
        self.user_controller = user_controller
        self.window = tk.Toplevel(master)
        self.window.title("Configuración Inicial - Establecer Contraseña del Administrador")
        self.window.geometry("400x250")
        self.create_widgets()

    def create_widgets(self):
        frame = ttk.Frame(self.window, padding="20")
        frame.pack(expand=True, fill="both")

        ttk.Label(frame, text="Ingrese la nueva contraseña para el administrador:").pack(pady=5)
        self.entry_password = ttk.Entry(frame, show="*")
        self.entry_password.pack(pady=5, fill="x")

        ttk.Label(frame, text="Confirme la contraseña:").pack(pady=5)
        self.entry_confirm = ttk.Entry(frame, show="*")
        self.entry_confirm.pack(pady=5, fill="x")

        btn = ttk.Button(frame, text="Guardar", command=self.save_admin_password)
        btn.pack(pady=10)

    def save_admin_password(self):
        password = self.entry_password.get().strip()
        confirm = self.entry_confirm.get().strip()
        if not password or not confirm:
            messagebox.showwarning("Campos incompletos", "Debe ingresar y confirmar la contraseña.")
            return
        if password != confirm:
            messagebox.showerror("Error", "Las contraseñas no coinciden.")
            return
        # Crear el usuario administrador usando el user_controller.
        # El método create_user en UserController se encargará de hashear la contraseña.
        success, msg = self.user_controller.create_user("admin", password, "admin")
        if success:
            messagebox.showinfo("Éxito", "Contraseña del administrador establecida correctamente.")
            self.window.destroy()
        else:
            messagebox.showerror("Error", f"No se pudo establecer la contraseña: {msg}")
