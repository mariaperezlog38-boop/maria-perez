# Conversor Dólar ⇄ Bolívar

Este proyecto es una calculadora de conversión entre dólares y bolívares usando `customtkinter` para la interfaz gráfica.

## Archivos

- `calculadora_bcv_v1.py`: aplicación principal con la interfaz gráfica.
- `calculadora_bcv_logic.py`: funciones de lógica de conversión, validación y formato.
- `requirements.txt`: dependencias necesarias para ejecutar la aplicación.

## Instalación

1. Crear el entorno virtual:

```powershell
python -m venv .venv
```

2. Activar el entorno:

```powershell
& ".venv/Scripts/Activate.ps1"
```

3. Instalar dependencias:

```powershell
pip install -r requirements.txt
```

## Uso

Ejecuta la aplicación con:

```powershell
& ".venv/Scripts/python.exe" "calculadora_bcv_v1.py"
```

## Pruebas

Ejecuta la prueba de lógica con:

```powershell
& ".venv/Scripts/python.exe" -m unittest test_calculadora_bcv_logic.py
```

## Notas

- La aplicación usa `pyBCV` para obtener la tasa BCV automáticamente.
- Si `pyBCV` no está disponible, se solicitará la tasa manualmente.
- La lógica de conversión está separada de la interfaz gráfica para facilitar pruebas y mantenimiento.

## Versión Android

Esta versión móvil usa `main.py` con Kivy para una interfaz táctil.

### Cómo ejecutar en desktop con Kivy

1. Instala Kivy y dependencias móviles:

```powershell
& ".venv/Scripts/python.exe" -m pip install -r requirements_android.txt
```

2. Ejecuta la app Android en el escritorio con:

```powershell
& ".venv/Scripts/python.exe" "main.py"
```

### Cómo construir el APK

1. Usa un entorno Linux o WSL con Buildozer instalado.
2. En la raíz del proyecto, ejecuta:

```bash
buildozer android debug
```

3. El APK se generará en `bin/`.

### Archivos Android

- `main.py`: entrypoint de la app Android con interfaz Kivy.
- `buildozer.spec`: configuración de Buildozer para crear el APK.
- `requirements_android.txt`: dependencias necesarias para la versión móvil.
