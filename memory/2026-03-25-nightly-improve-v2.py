#!/usr/bin/env python3
import time
import datetime as dt
import os
import json

CADENCIA_SECS = 15 * 60  # 15 minutes
END_HOUR = 5
REVIEW_EVERY = 4  # perform self-review every N ticks

def end_time_for_tonight(now=None):
    if now is None:
        now = dt.datetime.now()
    end = dt.datetime.combine(now.date(), dt.time(END_HOUR, 0))
    if now >= end:
        end = dt.datetime.combine(now.date() + dt.timedelta(days=1), dt.time(END_HOUR, 0))
    return end

MEMORY_DIR = "memory"
LOG_PREFIX = dt.date.today().isoformat()
LOG_PATH = os.path.join(MEMORY_DIR, f"{LOG_PREFIX}-nightly-improve.log")
SUMMARY_PATH = os.path.join(MEMORY_DIR, f"{LOG_PREFIX}-nightly-session-summary.md")
SELF_REVIEW_PATH = os.path.join(MEMORY_DIR, f"{LOG_PREFIX}-nightly-selfreview.md")

def ensure_directories():
    if not os.path.exists(MEMORY_DIR):
        os.makedirs(MEMORY_DIR)

def load_recent_memory():
    memory = {}
    memory_path = os.path.join(MEMORY_DIR, "MEMORY.md")
    if os.path.exists(memory_path):
        with open(memory_path, "r", encoding="utf-8") as f:
            memory["memory"] = f.read()
    # Get recent nightly summaries
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

def propose_improvements(memory_blob, tick):
    base = [
        "- Revisa MEMORY.md i actualitza categories: idioma (Català), zona horària, format de data.",
        "- Crea un resum nocturn (session-nightly) amb temes i properes accions.",
        "- Implementa compressió de context en prompts (estalvi de tokens).",
        "- Activa descomposició de tasques per a tasques complexes.",
    ]
    if memory_blob.get("memory"):
        base.append("- Inserir resums breus de la memòria recents en el summary nocturn.")
    # Add a tick-specific note
    base.append(f"- Revisió interna (tick {tick}): detectar fallades i registrar-ho.")
    return base

def log_tick(ts, improvements, log_path):
    line = {
        "timestamp": ts,
        "improvements": improvements
    }
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(json.dumps(line, ensure_ascii=False) + "\n")

def append_session_summary(ts, improvements, summary_path):
    with open(summary_path, "a", encoding="utf-8") as f:
        f.write(f"Time: {ts}\n")
        f.write("Improvements:\n")
        for imp in improvements:
            f.write(f"- {imp}\n")
        f.write("\n")

def write_self_review(ts, tick, log_path):
    content = []
    content.append(f"Time: {ts}")
    content.append(f"Tick: {tick}")
    content.append("Summary:")
    content.append("- Self-review executed. Check loop performance and token usage.")
    content.append("")
    with open(SELF_REVIEW_PATH, "a", encoding="utf-8") as f:
        f.write("\n".join(content) + "\n")

def main():
    ensure_directories()
    end_time = end_time_for_tonight()
    tick = 0
    while dt.datetime.now() < end_time:
        now = dt.datetime.now()
        memory_blob = load_recent_memory()
        improvements = propose_improvements(memory_blob, tick)
        ts = now.isoformat(timespec="seconds")
        log_tick(ts, improvements, LOG_PATH)
        append_session_summary(ts, improvements, SUMMARY_PATH)
        if tick % REVIEW_EVERY == 0:
            write_self_review(ts, tick, LOG_PATH)
        tick += 1
        time.sleep(CADENCIA_SECS)
    print("Nightly improvement v2 finished at", dt.datetime.now())

if __name__ == "__main__":
    main()
