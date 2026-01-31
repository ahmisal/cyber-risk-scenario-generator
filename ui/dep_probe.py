
import sys
import os
import time

def log(msg):
    print(f"[{time.time():.2f}] {msg}", flush=True)

log("Starting dependency probe...")

log("Importing numpy...")
try:
    import numpy
    log("Imported numpy")
except ImportError:
    log("numpy not found")

log("Importing PIL (Pillow)...")
try:
    import PIL
    log("Imported PIL")
except ImportError:
    log("PIL not found")

log("Importing matplotlib...")
try:
    import matplotlib
    log("Imported matplotlib")
except ImportError:
    log("matplotlib not found")

log("Importing pandas...")
try:
    import pandas
    log("Imported pandas")
except ImportError:
    log("pandas not found")

log("Importing anyio...")
try:
    import anyio
    log("Imported anyio")
except ImportError:
    log("anyio not found")

log("Importing httpcore...")
try:
    import httpcore
    log("Imported httpcore")
except ImportError:
    log("httpcore not found")

log("Importing httpx...")
try:
    import httpx
    log("Imported httpx")
except ImportError:
    log("httpx not found")

log("Importing fastapi...")
try:
    import fastapi
    log("Imported fastapi")
except ImportError:
    log("fastapi not found")

log("Importing uvicorn...")
try:
    import uvicorn
    log("Imported uvicorn")
except ImportError:
    log("uvicorn not found")

log("Importing websockets...")
try:
    import websockets
    log("Imported websockets")
except ImportError:
    log("websockets not found")

log("Importing gradio (final check)...")
try:
    import gradio
    log("Imported gradio")
except ImportError:
    log("gradio not found")

log("Probe complete.")
