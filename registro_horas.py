import tkinter as tk
from tkinter import messagebox
from datetime import datetime
import os
import pandas as pd
import calendar
import platform
import subprocess
import pygame
import threading

ARCHIVO = "horas_trabajadas_2025.csv"
PRECIO_DEFECTO = 3500

class MusicaFondo:
    def __init__(self):
        self.estado = "playing"
        self.volumen = 0.5  # Volumen inicial (0.0 a 1.0)
        self.iniciado = False

    def reproducir(self):
        if not self.iniciado:
            def play():
                try:
                    pygame.mixer.init()
                    ruta_musica = os.path.join(os.getcwd(), "musica_fondo.mp3")
                    if os.path.exists(ruta_musica):
                        pygame.mixer.music.load(ruta_musica)
                        pygame.mixer.music.set_volume(self.volumen)
                        pygame.mixer.music.play(-1)
                        self.iniciado = True
                    else:
                        print("Archivo 'musica_fondo.mp3' no encontrado en la carpeta de la app.")
                except Exception as e:
                    print(f"Error reproduciendo música: {e}")
            threading.Thread(target=play, daemon=True).start()
        else:
            pygame.mixer.music.unpause()
            self.estado = "playing"

    def pausar(self):
        if pygame.mixer.get_init() and pygame.mixer.music.get_busy():
            pygame.mixer.music.pause()
            self.estado = "paused"

    def toggle(self):
        if self.estado == "playing":
            self.pausar()
        else:
            self.reproducir()

    def set_volumen(self, value):
        self.volumen = float(value)
        if pygame.mixer.get_init():
            pygame.mixer.music.set_volume(self.volumen)

def leer_precio_por_hora():
    if not os.path.exists(ARCHIVO):
        return PRECIO_DEFECTO
    with open(ARCHIVO, encoding="utf-8") as f:
        first_line = f.readline().strip()
        if first_line.startswith("PRECIO_POR_HORA"):
            try:
                return float(first_line.split(";")[1])
            except Exception:
                return PRECIO_DEFECTO
    return PRECIO_DEFECTO

def cargar_datos():
    if not os.path.exists(ARCHIVO):
        with open(ARCHIVO, "w", encoding="utf-8") as f:
            f.write(f"PRECIO_POR_HORA;{PRECIO_DEFECTO}\nMES;DIA;HORAS\n")
        return pd.DataFrame(columns=["MES", "DIA", "HORAS"])
    df = pd.read_csv(ARCHIVO, sep=";", skiprows=1, dtype=str)
    return df

def guardar_datos(df):
    precio = leer_precio_por_hora()
    with open(ARCHIVO, "w", encoding="utf-8") as f:
        f.write(f"PRECIO_POR_HORA;{precio}\n")
    df.to_csv(ARCHIVO, mode="a", index=False, sep=';')

class RegistroHorasApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Registro de Horas Mejorado")
        self.root.geometry("580x500")

        # Música
        self.musica = MusicaFondo()
        self.musica.reproducir()  # Inicia automáticamente

        # Fecha y hora (solo una vez)
        self.label_fecha = tk.Label(root, font=('Arial', 12))
        self.label_fecha.pack(pady=6)
        self.label_info = tk.Label(root, font=('Arial', 10), justify='left')
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
        self.btn_resumen = tk.Button(root, text="Ver resumen mensual (abrir Excel)", command=self.abrir_excel)
        self.btn_resumen.pack(pady=4)

        # Frame gris para el total cobro
        self.frame_cobro = tk.Frame(root, bg="#e0e0e0", bd=2, relief="groove")
        self.frame_cobro.pack(pady=12, padx=14, fill="x")
        self.label_total_cobro = tk.Label(
            self.frame_cobro, text="Total cobro: $0.00",
            font=('Arial', 13, 'bold'), bg="#e0e0e0", fg="#2d2d2d",
            padx=8, pady=8
        )
        self.label_total_cobro.pack()

        # --- Controles de Música ocultos en un Frame minimizado ---
        self.frame_musica = tk.Frame(root)
        # No se muestra por defecto, sólo si se pasa el mouse por encima de la esquina inferior derecha
        self.frame_musica.place(relx=1.0, rely=1.0, anchor="se", x=-5, y=-5)
        self.frame_musica.lower()  # Lo envía al fondo visual

        self.boton_pausa = tk.Button(
            self.frame_musica, text="⏯", width=2, command=self.toggle_musica, relief="flat"
        )
        self.boton_pausa.grid(row=0, column=0, padx=2)
        self.slider_volumen = tk.Scale(
            self.frame_musica, from_=0, to=100, orient=tk.HORIZONTAL, length=56,
            command=self.cambiar_volumen, showvalue=0
        )
        self.slider_volumen.set(int(self.musica.volumen * 100))
        self.slider_volumen.grid(row=0, column=1, padx=2)

        # Área sensible muy pequeña en la esquina inferior derecha
        self.hitbox_musica = tk.Frame(root, width=22, height=22, bg="#e0e0e0")
        self.hitbox_musica.place(relx=1.0, rely=1.0, anchor="se", x=0, y=0)
        self.hitbox_musica.lower()

        self.hitbox_musica.bind("<Enter>", self.mostrar_controles_musica)
        self.frame_musica.bind("<Leave>", self.ocultar_controles_musica)
        self.frame_musica.bind("<Enter>", lambda e: None)

        self.actualizar_reloj()
        self.update_info()

    def mostrar_controles_musica(self, event=None):
        self.frame_musica.lift()
        self.frame_musica.tkraise()
        self.frame_musica.place(relx=1.0, rely=1.0, anchor="se", x=-5, y=-5)
        self.frame_musica.after(0, lambda: self.frame_musica.config(bg="#f0f0f0"))

    def ocultar_controles_musica(self, event=None):
        self.frame_musica.lower()

    def toggle_musica(self):
        self.musica.toggle()
        if self.musica.estado == "playing":
            self.boton_pausa.config(text="⏯")
        else:
            self.boton_pausa.config(text="⏯")

    def cambiar_volumen(self, value):
        self.musica.set_volumen(float(value) / 100)

    def obtener_fecha_actual(self):
        return datetime.now()

    def es_dia_habil(self, fecha):
        return fecha.weekday() < 5

    def cargar_automaticamente(self):
        hoy = self.obtener_fecha_actual()
        año, mes = hoy.year, hoy.month
        _, ultimo_dia = calendar.monthrange(año, mes)

        df = cargar_datos()
        df["MES"] = df["MES"].astype(str).str.strip()
        df["DIA"] = df["DIA"].astype(str).str.zfill(2)
        existentes = set(zip(df["MES"], df["DIA"]))

        fechas = []
        for dia in range(24, ultimo_dia + 1):
            fecha = datetime(año, mes, dia)
            if self.es_dia_habil(fecha):
                mes_str = fecha.strftime("%B")
                dia_str = fecha.strftime("%d")
                if (mes_str, dia_str) not in existentes:
                    fechas.append((mes_str, dia_str, 6.0))

        if fechas:
            nuevos_df = pd.DataFrame(fechas, columns=["MES", "DIA", "HORAS"])
            df = pd.concat([df, nuevos_df], ignore_index=True)
            df["MES"] = df["MES"].astype(str).str.strip()
            df["DIA"] = df["DIA"].astype(str).str.zfill(2)
            df = df.drop_duplicates(subset=["MES", "DIA"], keep='last')
            df = df.sort_values(by=["MES", "DIA"])
            guardar_datos(df)
            messagebox.showinfo(
                "Carga automática",
                f"Se cargaron 6 horas en {len(fechas)} días hábiles nuevos del {24} al {ultimo_dia}."
            )
        else:
            messagebox.showinfo(
                "Carga automática",
                "No hay días hábiles nuevos para cargar desde el 24 a fin de mes."
            )
        self.update_info()

    def guardar_registro_manual(self):
        hoy = self.obtener_fecha_actual()
        if not self.es_dia_habil(hoy):
            messagebox.showwarning("No permitido", "Sólo puedes cargar horas en días hábiles (lunes a viernes).")
            return

        mes = hoy.strftime("%B")
        dia = hoy.strftime("%d").zfill(2)
        df = cargar_datos()
        df["MES"] = df["MES"].astype(str).str.strip()
        df["DIA"] = df["DIA"].astype(str).str.zfill(2)

        mask = (df["MES"] == mes) & (df["DIA"] == dia)
        if mask.any():
            horas_previas = df.loc[mask, "HORAS"].iloc[0]
            messagebox.showwarning(
                "Registro duplicado",
                f"Ya cargaste {horas_previas} horas hoy."
            )
            self.update_info()
            return

        try:
            horas = float(self.entry_horas.get())
            if self.entry_horas.get().strip() == "" or not (0 <= horas <= 24):
                raise ValueError
        except ValueError:
            messagebox.showerror("Error", "Ingrese una cantidad válida de horas (0 a 24)")
            return

        nuevo = pd.DataFrame([[mes, dia, horas]], columns=["MES", "DIA", "HORAS"])
        df = pd.concat([df, nuevo], ignore_index=True)
        df["MES"] = df["MES"].astype(str).str.strip()
        df["DIA"] = df["DIA"].astype(str).str.zfill(2)
        df = df.drop_duplicates(subset=["MES", "DIA"], keep='last')
        df = df.sort_values(by=["MES", "DIA"])
        guardar_datos(df)
        messagebox.showinfo("Guardado", f"Se registraron {horas} horas para {dia} {mes}")
        self.entry_horas.delete(0, tk.END)
        self.update_info()

    def generar_resumen_mensual(self):
        precio = leer_precio_por_hora()
        if not os.path.exists(ARCHIVO):
            return "Todavía no hay datos cargados.", 0.0, 0.0, precio
        df = cargar_datos()
        if df.empty:
            return "No hay datos aún.", 0.0, 0.0, precio
        df["HORAS"] = df["HORAS"].astype(float)
        resumen = df.groupby("MES")["HORAS"].sum().sort_index()
        resumen_str = ""
        total_horas = 0.0
        for mes, horas in resumen.items():
            resumen_str += f"{mes}: {horas:.1f} horas - ${precio:,.0f}/h\n"
            total_horas += horas
        total_cobro = total_horas * precio
        return resumen_str.strip(), total_horas, total_cobro, precio

    def update_info(self, bloquear=None):
        hoy = self.obtener_fecha_actual()
        mes = hoy.strftime("%B")
        dia = hoy.strftime("%d").zfill(2)
        info = ""

        df = cargar_datos()
        if not df.empty:
            df["MES"] = df["MES"].astype(str).str.strip()
            df["DIA"] = df["DIA"].astype(str).str.zfill(2)
            mask = (df["MES"] == mes) & (df["DIA"] == dia)
        else:
            mask = pd.Series(dtype=bool)

        if mask.any():
            horas_registradas = df.loc[mask, "HORAS"].iloc[0]
            info += f"Ya cargaste {horas_registradas} horas hoy.\n"
            self.entry_horas.config(state="disabled", disabledbackground="#e0e0e0")
            self.btn_guardar.config(state="disabled")
        else:
            info += f"No cargaste horas hoy.\n"
            self.entry_horas.config(state="normal", background="white")
            self.btn_guardar.config(state="normal")

        resumen, total_horas, total_cobro, precio = self.generar_resumen_mensual()
        info += f"\nRegistro mensual:\n{resumen}\n"
        self.label_info.config(text=info)
        self.label_total_cobro.config(text=f"Total cobro: ${total_cobro:,.2f}")

    def actualizar_reloj(self):
        self.label_fecha.config(text=datetime.now().strftime("%A, %d %B %Y - %H:%M:%S"))
        self.root.after(1000, self.actualizar_reloj)
        self.update_info()

    def abrir_excel(self):
        if not os.path.exists(ARCHIVO):
            messagebox.showinfo("Resumen", "Todavía no hay datos cargados.")
            return
        try:
            if platform.system() == "Windows":
                os.startfile(ARCHIVO)
            elif platform.system() == "Darwin":
                subprocess.call(["open", ARCHIVO])
            else:
                subprocess.call(["xdg-open", ARCHIVO])
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo abrir el archivo: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = RegistroHorasApp(root)
    root.mainloop()