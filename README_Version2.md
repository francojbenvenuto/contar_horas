# Registro de Horas Mejorado

Aplicación de escritorio para registrar, revisar y exportar tus horas trabajadas.  
**Funciona en Windows, Linux y macOS.**

## Características

- Registro manual y automático de horas trabajadas.
- Archivo CSV ordenado con columnas: MES, DIA, HORAS.
- Interfaz amigable: muestra día, hora, si ya se registraron horas hoy y resumen mensual.
- Botón para abrir el archivo Excel directamente.
- Compatible con Windows, Linux y Mac.

## Instalación

1. Instala Python 3.x y pip si aún no los tienes.
2. Instala las dependencias:
   ```bash
   pip install -r requirements.txt
   ```
3. Ejecuta el programa:
   ```bash
   python registro_horas.py
   ```

## Uso

- Ingresa las horas trabajadas y presiona “Guardar horas”.
- Usa el botón “Cargar 6h del 24 a fin de mes” para automatizar la carga para días hábiles.
- Consulta el resumen mensual y abre el archivo CSV con el botón correspondiente.

## Dependencias

- pandas

## Exportar a ejecutable

Para crear un ejecutable (ejemplo con PyInstaller):

```bash
pip install pyinstaller
pyinstaller --onefile --windowed registro_horas.py
```
El ejecutable estará en la carpeta `dist/`.
