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

Se agregó una nueva versión Flutter en `calculadora_bcv_flutter/` que puede compilar un APK en GitHub Actions.

### Versión Flutter

El proyecto Flutter se encuentra en `calculadora_bcv_flutter/`.

Para ejecutar localmente, instala Flutter y el SDK de Android, luego:

```bash
cd calculadora_bcv_flutter
flutter pub get
flutter run
```

Para construir el APK localmente:

```bash
cd calculadora_bcv_flutter
flutter build apk --release
```

### Versión Buildozer (anterior)

La versión Kivy/Buildozer sigue disponible en el repositorio, pero la ruta recomendada ahora es usar Flutter.

- `main.py`: entrypoint de la app Android con interfaz Kivy.
- `buildozer.spec`: configuración de Buildozer para crear el APK.
- `requirements_android.txt`: dependencias necesarias para la versión móvil.
