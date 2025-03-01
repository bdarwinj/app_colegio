import tkinter as tk
from tkinter import ttk, messagebox
import logging

class ChangePasswordWindow(tk.Toplevel):
    def __init__(self, master, user_controller, current_user):
        super().__init__(master)
        self.user_controller = user_controller
        self.current_user = current_user
        self.title("Cambiar Clave")
        self.geometry("400x250")
        self.create_widgets()

    def create_widgets(self):
        frame = ttk.Frame(self, padding="20")
        frame.pack(expand=True, fill="both")
        
        ttk.Label(frame, text="Clave Actual:").grid(row=0, column=0, sticky="w", pady=5)
        self.old_password_entry = ttk.Entry(frame, show="*")
        self.old_password_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        
        ttk.Label(frame, text="Nueva Clave:").grid(row=1, column=0, sticky="w", pady=5)
        self.new_password_entry = ttk.Entry(frame, show="*")
        self.new_password_entry.grid(row=1, column=1, padx=5, pady=5, sticky="ew")
        
        ttk.Label(frame, text="Confirmar Nueva Clave:").grid(row=2, column=0, sticky="w", pady=5)
        self.confirm_password_entry = ttk.Entry(frame, show="*")
        self.confirm_password_entry.grid(row=2, column=1, padx=5, pady=5, sticky="ew")
        
        self.change_password_button = ttk.Button(frame, text="Cambiar Clave", command=self.change_password)
        self.change_password_button.grid(row=3, column=0, columnspan=2, pady=20)
        
        frame.columnconfigure(1, weight=1)

    def validate_inputs(self):
        old_password = self.old_password_entry.get().strip()
        new_password = self.new_password_entry.get().strip()
        confirm_password = self.confirm_password_entry.get().strip()
        
        if not old_password or not new_password or not confirm_password:
            messagebox.showerror("Error", "Todos los campos son obligatorios.")
            return False
        if new_password != confirm_password:
            messagebox.showerror("Error", "La nueva clave y su confirmación no coinciden.")
            return False
        return True

    def change_password(self):
        if not self.validate_inputs():
            return
        
        old_password = self.old_password_entry.get().strip()
        new_password = self.new_password_entry.get().strip()
        
        try:
            username = self.current_user.username if hasattr(self.current_user, "username") else self.current_user
            success, message = self.user_controller.change_password(username, old_password, new_password)
            if success:
                messagebox.showinfo("Éxito", message)
                logging.info(f"Contraseña cambiada exitosamente para usuario: {username}")
                self.destroy()
            else:
                messagebox.showerror("Error", message)
                logging.warning(f"Intento fallido de cambio de contraseña para usuario: {username}")
        except Exception as e:
            logging.error(f"Error al cambiar la contraseña: {e}")
            messagebox.showerror("Error", f"Ocurrió un error al cambiar la clave: {str(e)}")