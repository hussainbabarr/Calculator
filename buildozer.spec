[app]
# (str) Title of your application
title = Calculator
# (str) Package name
package.name = calculator
# (str) Package domain (needed for android/ios packaging)
package.domain = org.haussainbabar
# (str) Source code directory
source.dir = .
source.exclude_dirs = .venv,app,__pycache__,.git
source.include_exts = py,json,png,jpg,kv,atlas
# (list) Application requirements
requirements = python3,kivy==2.3.1,requests
# (str) Supported orientation (portrait is mobile-friendly)
orientation = portrait
# (str) Application version
version = 1.0.0
# (bool) Fullscreen mode
fullscreen = 0

[buildozer]
# (str) Log level
log_level = 2
# (str) Warn if buildozer is run as root
warn_on_root = 1

[android]
# (list) Android permissions
android.permissions = INTERNET
# (str) Android API target
android.api = 34
android.sdk = 34
android.ndk = 25b
# (str) Android minimum API
android.minapi = 23
# (str) Android architecture
android.arch = arm64-v8a
