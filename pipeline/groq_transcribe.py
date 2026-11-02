#!/usr/bin/env python3
"""Распознать запись через Groq (Whisper Large v3) без терминала пользователя.

Использование:
  groq_transcribe.py <аудио или видео> <выходная папка _timed> --key <файл с ключом>

Режет запись на части по 30 мин (моно 16 кГц AAC 48k, чтобы каждая часть была < 25 МБ),
отправляет в Groq с verbose_json и сохраняет zapis_chast_NN.json в выходную папку —
тот же формат, что делает transcribe.sh, поэтому дальше работает transcript_tools.py.
Нужны ffmpeg и curl.
"""
import sys, os, subprocess, glob, json, argparse, tempfile, time

ap = argparse.ArgumentParser()
ap.add_argument("src"); ap.add_argument("out"); ap.add_argument("--key", required=True)
a = ap.parse_args()
key = open(a.key).read().strip()
os.makedirs(a.out, exist_ok=True)
tmp = tempfile.mkdtemp()
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", a.src, "-vn", "-ac", "1", "-ar", "16000",
                "-c:a", "aac", "-b:a", "48k", "-f", "segment", "-segment_time", "1800",
                "-reset_timestamps", "1", os.path.join(tmp, "zapis_chast_%02d.m4a")], check=True)
for f in sorted(glob.glob(os.path.join(tmp, "*.m4a"))):
    name = os.path.splitext(os.path.basename(f))[0]
    dst = os.path.join(a.out, name + ".json")
    for attempt in range(6):
        r = subprocess.run(["curl", "-sS", "--max-time", "600", "https://api.groq.com/openai/v1/audio/transcriptions",
                            "-H", f"Authorization: Bearer {key}", "-F", f"file=@{f}",
                            "-F", "model=whisper-large-v3", "-F", "language=ru",
                            "-F", "response_format=verbose_json", "-F", "timestamp_granularities[]=segment",
                            "-F", "temperature=0"], capture_output=True, text=True)
        try:
            d = json.loads(r.stdout)
        except Exception:
            d = {"error": r.stdout[:300] + r.stderr[:300]}
        if "segments" in d:
            json.dump(d, open(dst, "w"), ensure_ascii=False); print("ok", name, len(d["segments"]), "сегм."); break
        print("ошибка", name, str(d)[:200], file=sys.stderr)
        if "invalid_api_key" in str(d): sys.exit(2)
        time.sleep(30)
    else:
        sys.exit(f"не удалось распознать {name}")
