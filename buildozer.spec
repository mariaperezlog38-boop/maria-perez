[app]
# (str) Title of your application
title = Calculadora BCV

# (str) Package name
package.name = calculadora_bcv

# (str) Package domain (unique identifier)
package.domain = org.example

# (str) Source code where the main.py is located
source.dir = .

# (list) Source file extensions to include
source.include_exts = py,png

# (str) Application version
version = 1.0.0

# (list) Application requirements
requirements = python3,kivy

# (str) Icon file
icon.filename = icono.ico

# (str) Supported orientation
orientation = portrait

# (list) Permissions
android.permissions = INTERNET

# (str) Target Android API
android.api = 33

# (str) Minimum Android API
android.minapi = 21

# (str) Android NDK version
android.ndk = 25b

# (str) Presplash image
#presplash.filename = %(source.dir)s/presplash.png

[buildozer]
log_level = 2
warn_on_root = 1
