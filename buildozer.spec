[app]

title = Calculator
package.name = calculator
package.domain = org.haussainbabar

source.dir = .
source.exclude_dirs = .venv,app,__pycache__,.git,.github
source.include_exts = py,json,png,jpg,jpeg,kv,atlas

requirements = python3,kivy==2.3.1,requests

version = 1.0.0
orientation = portrait
fullscreen = 0

android.permissions = INTERNET
android.api = 35
android.minapi = 23
android.ndk = 28c
android.ndk_api = 23
android.archs = arm64-v8a
android.accept_sdk_license = True

p4a.bootstrap = sdl2
p4a.branch = master
p4a.commit = v2026.05.09

[buildozer]

log_level = 2
warn_on_root = 1