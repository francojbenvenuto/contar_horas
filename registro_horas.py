import tkinter as tk
from tkinter import messagebox
from datetime import datetime, timedelta
import os
import pandas as pd
import calendar

ARCHIVO = "horas_trabajadas_2025.csv"

def obtener_fecha_actual():
    return datetime.now().strftime("%Y-%m-%d")

def es_dia_habil(fecha):
    return fecha.weekday() < 5  # 0 = lunes, 6 = domingo

def cargar_automaticamente():
    hoy = datetime.now()
    año = hoy.year
    mes = hoy.month
    _, ultimo_dia = calendar.monthrange(año, mes)

    fechas = []
    for dia in range(24, ultimo_dia + 1):
        fecha = datetime(año, mes, dia)
        if es_dia_habil(fecha):
            fechas.append((fecha.strftime("%Y-%m-%d"), 6))

    guardar_registros(fechas)
    messagebox.showinfo("Carga automática", f"Se cargaron 6 horas por día desde el 24 hasta el {ultimo_dia} (días hábiles)")

def guardar_registro_manual():
    fecha = obtener_fecha_actual()

    # Cargar el archivo si existe
    if os.path.exists(ARCHIVO):
        df = pd.read_csv(ARCHIVO)
        if fecha in df["fecha"].tolist():
            messagebox.showwarning("Registro duplicado", "No, en el día ya registraste horas.")
            return
    else:
        df = pd.DataFrame(columns=["fecha", "horas"])

    # Validar horas ingresadas
    try:
        horas = float(entry_horas.get())
        if not (0 <= horas <= 24):
            raise ValueError
    except ValueError:
        messagebox.showerror("Error", "Ingrese una cantidad válida de horas (0 a 24)")
        return

    # Guardar nueva entrada
    nuevo = pd.DataFrame([[fecha, horas]], columns=["fecha", "horas"])
    df = pd.concat([df, nuevo])
    df = df.sort_values(by="fecha")
    df.to_csv(ARCHIVO, index=False)
    messagebox.showinfo("Guardado", f"Se registraron {horas} horas para el día {fecha}")
    entry_horas.delete(0, tk.END)


def guardar_registros(lista_registros):
    if os.path.exists(ARCHIVO):
        df = pd.read_csv(ARCHIVO)
    else:
        df = pd.DataFrame(columns=["fecha", "horas"])

    fechas_existentes = df["fecha"].tolist()
    nuevos_registros = [(f, h) for (f, h) in lista_registros if f not in fechas_existentes]

    if nuevos_registros:
        nuevos_df = pd.DataFrame(nuevos_registros, columns=["fecha", "horas"])
        df = pd.concat([df, nuevos_df])
        df = df.sort_values(by="fecha")
        df.to_csv(ARCHIVO, index=False)

def mostrar_resumen():
    if not os.path.exists(ARCHIVO):
        messagebox.showinfo("Resumen", "Todavía no hay datos cargados.")
        return

    df = pd.read_csv(ARCHIVO)
    df["fecha"] = pd.to_datetime(df["fecha"])
    df["mes"] = df["fecha"].dt.strftime("%B")

    resumen = df.groupby("mes")["horas"].sum().sort_index()
    resumen_str = "\n".join([f"{mes}: {horas} horas" for mes, horas in resumen.items()])
    messagebox.showinfo("Resumen mensual", resumen_str)

# ---------------- INTERFAZ ----------------

ventana = tk.Tk()
ventana.title("Registro de Horas")
ventana.geometry("320x260")

reloj = tk.Label(ventana, font=('Arial', 16))
reloj.pack(pady=10)

def actualizar_reloj():
    reloj.config(text=datetime.now().strftime("%H:%M:%S"))
    ventana.after(1000, actualizar_reloj)

actualizar_reloj()

frame = tk.Frame(ventana)
frame.pack(pady=10)

label_horas = tk.Label(frame, text="Horas trabajadas hoy:")
label_horas.grid(row=0, column=0, padx=5, pady=5)

entry_horas = tk.Entry(frame, width=10)
entry_horas.grid(row=0, column=1, padx=5)

btn_guardar = tk.Button(ventana, text="Guardar horas", command=guardar_registro_manual)
btn_guardar.pack(pady=5)

btn_auto = tk.Button(ventana, text="Cargar 6h del 24 a fin de mes", command=cargar_automaticamente)
btn_auto.pack(pady=5)

btn_resumen = tk.Button(ventana, text="Ver resumen mensual", command=mostrar_resumen)
btn_resumen.pack(pady=5)

ventana.mainloop()
