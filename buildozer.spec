[app]

title = Calculator
package.name = calculator
package.domain = org.haussainbabar

source.dir = .
source.exclude_dirs = .venv,app,__pycache__,.git
source.include_exts = py,json,png,jpg,kv,atlas

requirements = python3,kivy==2.3.1,requests

orientation = portrait
version = 1.0.0
fullscreen = 0

android.permissions = INTERNET
android.api = 34
android.minapi = 23
android.ndk = 25b
android.archs = arm64-v8a
android.accept_sdk_license = True

[buildozer]

log_level = 2
warn_on_root = 1