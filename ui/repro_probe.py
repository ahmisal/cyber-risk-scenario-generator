
import sys
import os
import time
import tempfile

def log(msg):
    print(f"[{time.time():.2f}] {msg}", flush=True)

log("Starting EXACT reproduction probe...")

# Preamble from gradio_app.py
os.environ["GRADIO_ANALYTICS_ENABLED"] = "False"
os.environ["MPLCONFIGDIR"] = os.path.join(tempfile.gettempdir(), "matplotlib_cache")

log("Importing requests...")
import requests
log("Imported requests.")

log("Importing gradio...")
import gradio as gr
log("Imported gradio.")

log("Probe complete.")
