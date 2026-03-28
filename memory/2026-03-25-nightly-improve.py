#!/usr/bin/env python3
import time
import datetime as dt
import os
import json

# Cadència i horitzó (ajusta si cal)
CADENCIA_SECS = 15 * 60  # 15 minuts
END_HOUR = 5

def end_time_for_tonight(now=None):
    if now is None:
        now = dt.datetime.now()
    # Fins a les 05:00 del dia següent
    end = dt.datetime.combine(now.date(), dt.time(END_HOUR, 0))
    if now >= end:
        end = dt.datetime.combine(now.date() + dt.timedelta(days=1), dt.time(END_HOUR, 0))
    return end

# Rutes de memòria
MEMORY_DIR = "memory"
LOG_PREFIX = dt.date.today().isoformat()
LOG_PATH = os.path.join(MEMORY_DIR, f"{LOG_PREFIX}-nightly-improve.log")

def ensure_directories():
    if not os.path.exists(MEMORY_DIR):
        os.makedirs(MEMORY_DIR)

def load_recent_memory():
    # Lectura simple de MEMORY.md i resums de sessió nocturns
    memory = {}
    memory_path = os.path.join(MEMORY_DIR, "MEMORY.md")
    if os.path.exists(memory_path):
        with open(memory_path, "r", encoding="utf-8") as f:
            memory["memory"] = f.read()
    # Últims resums de sessió (si existissin)
    summaries = []
    for fname in sorted(os.listdir(MEMORY_DIR), reverse=True):
        if "nightly-session-summary" in fname:
            try:
                with open(os.path.join(MEMORY_DIR, fname), "r", encoding="utf-8") as f:
                    summaries.append(f.read())
            except Exception:
                pass
    memory["session_summaries"] = summaries[:5]
    return memory

def propose_improvements(memory_blob):
    # Exemple d’improvisacions; pots adaptar-ho segons el teu cas
    improvements = [
        "- Revisa MEMORY.md i actualitza categories: idioma (Català), zona horària, format de data.",
        "- Crea un resum nocturn (session-nightly) amb temes i properes accions.",
        "- Implementa compressió de context en prompts (tentatives d’estalvi de tokens).",
        "- Activa diàleg de descomposició de tasques per a tasques complexes.",
    ]
    # pots afegir informació del memory_blob si vols ser més específic
    if memory_blob.get("memory"):
        improvements.append("- Inserir resums breus de la memòria recents en el summary nocturn.")
    return improvements

def log_tick(ts, improvements, log_path):
    line = {
        "timestamp": ts,