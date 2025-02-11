import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import os
import shutil
from src.controllers.config_controller import ConfigController

class ConfigUI:
    def __init__(self, db):
        self.db = db
        self.config_controller = ConfigController(db)
        self.window = tk.Toplevel()
        self.window.title("Editar Configuración")
        self.window.geometry("450x300")
        self.create_widgets()

    def create_widgets(self):
        # Recuperar configuración actual
        configs = self.config_controller.get_all_configs()
        # Etiquetas y campos de entrada para cada configuración editable
        ttk.Label(self.window, text="Nombre del Colegio:").grid(row=0, column=0, padx=10, pady=10, sticky="w")
        self.entry_school_name = ttk.Entry(self.window, width=40)
        self.entry_school_name.grid(row=0, column=1, padx=10, pady=10)
        self.entry_school_name.insert(0, configs.get("SCHOOL_NAME", ""))

        ttk.Label(self.window, text="Ruta del Logo:").grid(row=1, column=0, padx=10, pady=10, sticky="w")
        self.entry_logo_path = ttk.Entry(self.window, width=40)
        self.entry_logo_path.grid(row=1, column=1, padx=10, pady=10)
        self.entry_logo_path.insert(0, configs.get("LOGO_PATH", ""))
        
        # Botón para escoger archivo de imagen
        self.btn_choose_logo = ttk.Button(self.window, text="Seleccionar Imagen", command=self.choose_logo)
        self.btn_choose_logo.grid(row=2, column=1, padx=10, pady=5, sticky="e")

        # Botón para guardar los cambios
        btn_save = ttk.Button(self.window, text="Guardar", command=self.save_config)
        btn_save.grid(row=3, column=0, columnspan=2, pady=20)

    def choose_logo(self):
        # Abrir un file dialog para seleccionar una imagen
        file_path = filedialog.askopenfilename(
            title="Seleccionar imagen", 
            filetypes=[("Image Files", "*.png;*.jpg;*.jpeg;*.gif"), ("All Files", "*.*")]
        )
        if file_path:
            # Crear carpeta assets si no existe
            assets_folder = os.path.join(os.getcwd(), "assets")
            if not os.path.exists(assets_folder):
                os.makedirs(assets_folder)
            # Copiar la imagen seleccionada a la carpeta assets
            file_name = os.path.basename(file_path)
            destination = os.path.join(assets_folder, file_name)
            try:
                shutil.copy(file_path, destination)
                # Actualizar el entry con la ruta relativa al logo
                relative_path = os.path.join("assets", file_name)
                self.entry_logo_path.delete(0, tk.END)
                self.entry_logo_path.insert(0, relative_path)
                messagebox.showinfo("Éxito", "Imagen cargada correctamente")
            except Exception as e:
                messagebox.showerror("Error", f"Error al copiar la imagen: {e}")

    def save_config(self):
        school_name = self.entry_school_name.get().strip()
        logo_path = self.entry_logo_path.get().strip()
        if not school_name:
            messagebox.showwarning("Campos incompletos", "El nombre del colegio no puede estar vacío")
            return

        success1, msg1 = self.config_controller.update_config("SCHOOL_NAME", school_name)
        success2, msg2 = self.config_controller.update_config("LOGO_PATH", logo_path)
        if success1 and success2:
            messagebox.showinfo("Éxito", "La configuración se ha actualizado correctamente.")
            self.window.destroy()
        else:
            messagebox.showerror("Error", f"{msg1 or ''}\n{msg2 or ''}")