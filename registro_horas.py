import tkinter as tk
from tkinter import messagebox
from datetime import datetime, timedelta
import os
import pandas as pd
import calendar
import platform
import subprocess

ARCHIVO = "horas_trabajadas_2025.csv"

class RegistroHorasApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Registro de Horas Mejorado")
        self.root.geometry("400x320")

        # Reloj y fecha
        self.label_fecha = tk.Label(root, font=('Arial', 12))
        self.label_fecha.pack(pady=3)
        self.label_reloj = tk.Label(root, font=('Arial', 18, 'bold'))
        self.label_reloj.pack(pady=3)
        self.label_info = tk.Label(root, font=('Arial', 10))
        self.label_info.pack(pady=3)

        # Frame para ingresar horas
        frame = tk.Frame(root)
        frame.pack(pady=10)
        tk.Label(frame, text="Horas trabajadas hoy:").grid(row=0, column=0, padx=5, pady=5)
        self.entry_horas = tk.Entry(frame, width=10)
        self.entry_horas.grid(row=0, column=1, padx=5)

        # Botones
        self.btn_guardar = tk.Button(root, text="Guardar horas", command=self.guardar_registro_manual)
        self.btn_guardar.pack(pady=4)
        self.btn_auto = tk.Button(root, text="Cargar 6h del 24 a fin de mes", command=self.cargar_automaticamente)
        self.btn_auto.pack(pady=4)
        self.btn_resumen = tk.Button(root, text="Ver resumen mensual", command=self.abrir_excel)
        self.btn_resumen.pack(pady=4)

        self.actualizar_reloj()
        self.update_info()

    def obtener_fecha_actual(self):
        return datetime.now()

    def es_dia_habil(self, fecha):
        return fecha.weekday() < 5  # 0 = lunes, 6 = domingo

    def cargar_automaticamente(self):
        hoy = self.obtener_fecha_actual()
        año, mes = hoy.year, hoy.month
        _, ultimo_dia = calendar.monthrange(año, mes)

        fechas = []
        for dia in range(24, ultimo_dia + 1):
            fecha = datetime(año, mes, dia)
            if self.es_dia_habil(fecha):
                fechas.append((fecha.strftime("%B"), fecha.strftime("%d"), 6.0))

        nuevos = self.guardar_registros(fechas)
        messagebox.showinfo(
            "Carga automática",
            f"Se cargaron 6 horas por día desde el 24 hasta el {ultimo_dia} (días hábiles)\nNuevos registros: {nuevos}"
        )
        self.update_info()

    def guardar_registro_manual(self):
        hoy = self.obtener_fecha_actual()
        mes = hoy.strftime("%B")
        dia = hoy.strftime("%d")

        # Leer archivo
        if os.path.exists(ARCHIVO):
            df = pd.read_csv(ARCHIVO)
        else:
            df = pd.DataFrame(columns=["MES", "DIA", "HORAS"])

        # Si ya hay registro para hoy
        mask = (df["MES"] == mes) & (df["DIA"] == dia)
        if not df[mask].empty:
            horas_previas = df[mask]["HORAS"].values[0]
            messagebox.showwarning(
                "Registro duplicado",
                f"Ya registraste horas para hoy: {horas_previas} horas."
            )
            self.update_info()
            return

        # Validar horas
        try:
            horas = float(self.entry_horas.get())
            if self.entry_horas.get().strip() == "" or not (0 <= horas <= 24):
                raise ValueError
        except ValueError:
            messagebox.showerror("Error", "Ingrese una cantidad válida de horas (0 a 24)")
            return

        # Guardar registro
        nuevo = pd.DataFrame([[mes, dia, horas]], columns=["MES", "DIA", "HORAS"])
        df = pd.concat([df, nuevo])
        df = df.sort_values(by=["MES", "DIA"])
        df.to_csv(ARCHIVO, index=False)
        messagebox.showinfo("Guardado", f"Se registraron {horas} horas para {dia} {mes}")
        self.entry_horas.delete(0, tk.END)
        self.update_info()

    def guardar_registros(self, lista_registros):
        if os.path.exists(ARCHIVO):
            df = pd.read_csv(ARCHIVO)
        else:
            df = pd.DataFrame(columns=["MES", "DIA", "HORAS"])

        # Evitar duplicados
        existentes = set(zip(df["MES"], df["DIA"]))
        nuevos = [reg for reg in lista_registros if (reg[0], reg[1]) not in existentes]

        if nuevos:
            nuevos_df = pd.DataFrame(nuevos, columns=["MES", "DIA", "HORAS"])
            df = pd.concat([df, nuevos_df])
            df = df.sort_values(by=["MES", "DIA"])
            df.to_csv(ARCHIVO, index=False)
        return len(nuevos)

    def generar_resumen_mensual(self):
        if not os.path.exists(ARCHIVO):
            return "Todavía no hay datos cargados."
        df = pd.read_csv(ARCHIVO)
        resumen = df.groupby("MES")["HORAS"].sum().sort_index()
        resumen_str = "\n".join([f"{mes}: {horas} horas" for mes, horas in resumen.items()])
        return resumen_str if resumen_str else "No hay datos aún."

    def update_info(self):
        hoy = self.obtener_fecha_actual()
        mes = hoy.strftime("%B")
        dia = hoy.strftime("%d")
        hora_actual = hoy.strftime("%H:%M:%S")
        info = f"Día: {dia} {mes} - Hora: {hora_actual}\n"

        ya_registrado = False
        horas_registradas = None
        if os.path.exists(ARCHIVO):
            df = pd.read_csv(ARCHIVO)
            mask = (df["MES"] == mes) & (df["DIA"] == dia)
            if not df[mask].empty:
                ya_registrado = True
                horas_registradas = df[mask]["HORAS"].values[0]

        if ya_registrado:
            info += f"Hoy ya registraste: {horas_registradas} horas.\n"
        else:
            info += f"Hoy no registraste horas.\n"

        resumen = self.generar_resumen_mensual()
        info += "\nResumen mensual:\n" + resumen
        self.label_info.config(text=info)
        self.label_fecha.config(text=hoy.strftime("%A, %d %B %Y"))

    def actualizar_reloj(self):
        self.label_reloj.config(text=datetime.now().strftime("%H:%M:%S"))
        self.root.after(1000, self.actualizar_reloj)
        self.update_info()

    def abrir_excel(self):
        if not os.path.exists(ARCHIVO):
            messagebox.showinfo("Resumen", "Todavía no hay datos cargados.")
            return
        try:
            if platform.system() == "Windows":
                os.startfile(ARCHIVO)
            elif platform.system() == "Darwin":  # macOS
                subprocess.call(["open", ARCHIVO])
            else:  # Linux
                subprocess.call(["xdg-open", ARCHIVO])
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo abrir el archivo: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = RegistroHorasApp(root)
    root.mainloop()