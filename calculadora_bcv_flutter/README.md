Calculadora BCV - Flutter

Este directorio contiene una versión mínima de la `Calculadora BCV` en Flutter.

Pasos para usar localmente:

1. Instala Flutter y configura el SDK de Android (ver https://flutter.dev/docs/get-started/install)
2. Desde la carpeta `calculadora_bcv_flutter` ejecuta:

```bash
flutter pub get
flutter run  # para probar en emulador/dispositivo
flutter build apk --release  # para compilar el APK
```

La UI acepta expresiones aritméticas en el campo "Monto" (por ejemplo `10+5/2`) y formatos de tasa como `30.5`, `30,5` o `Bs. 30,5`.

> Nota: el workflow de GitHub Actions `/.github/workflows/build_apk.yml` ahora puede crear los archivos Android necesarios y compilar el APK desde este directorio.
