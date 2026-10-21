#!/usr/bin/env python3
"""HTTPS-hostable JARVIS study app: mobile web front end + Uzbek Neural TTS."""
from __future__ import annotations
import asyncio
import json
import os
import re
import secrets
import time
from collections import deque
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from threading import Lock

import edge_tts

ROOT = Path(__file__).resolve().parent
PUBLIC = ROOT / "public"
PORT = int(os.environ.get("PORT", "8765"))
HOST = "0.0.0.0"
ACCESS_TOKEN = os.environ.get("JARVIS_ACCESS_TOKEN") or secrets.token_urlsafe(28)
ALLOWED_VOICES = {"uz-UZ-SardorNeural", "uz-UZ-MadinaNeural"}

CYR_TO_LAT = {
    "А":"A", "Б":"B", "В":"V", "Г":"G", "Д":"D", "Ё":"Yo", "Ж":"J", "З":"Z", "И":"I", "Й":"Y", "К":"K", "Л":"L", "М":"M", "Н":"N", "О":"O", "П":"P", "Р":"R", "С":"S", "Т":"T", "У":"U", "Ф":"F", "Х":"X", "Ц":"Ts", "Ч":"Ch", "Ш":"Sh", "Щ":"Shch", "Ъ":"", "Ы":"I", "Ь":"", "Э":"E", "Ю":"Yu", "Я":"Ya",
    "а":"a", "б":"b", "в":"v", "г":"g", "д":"d", "ё":"yo", "ж":"j", "з":"z", "и":"i", "й":"y", "к":"k", "л":"l", "м":"m", "н":"n", "о":"o", "п":"p", "р":"r", "с":"s", "т":"t", "у":"u", "ф":"f", "х":"x", "ц":"ts", "ч":"ch", "ш":"sh", "щ":"shch", "ъ":"", "ы":"i", "ь":"", "э":"e", "ю":"yu", "я":"ya",
    "Ў":"Oʻ", "ў":"oʻ", "Қ":"Q", "қ":"q", "Ғ":"Gʻ", "ғ":"gʻ", "Ҳ":"H", "ҳ":"h",
}

def to_uzbek_latin(text: str) -> str:
    text = str(text or "")
    substitutions = [
        (r"Қ\s*Қ\s*С", "qo‘shilgan qiymat solig‘i"),
        (r"\bБҲМ\b", "bazaviy hisoblash miqdori"),
        (r"\bСТИР\b", "es ti er"),
        (r"\bДт\b", "debet"), (r"\bКт\b", "kredit"),
        (r"\bЭРИ\b", "elektron raqamli imzo"),
        (r"\bПФ\s*[–—-]?\s*100\s*[- ]?сон\b", "pe ef yuz sonli"),
        (r"\bҚҚС\b", "qo‘shilgan qiymat solig‘i"),
        (r"\bФИО\b", "familiya ism sharif"),
    ]
    for pattern, replacement in substitutions:
        text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
    text = text.replace("’", "ʻ").replace("‘", "ʻ").replace("ʼ", "ʻ").replace("`", "ʻ")
    chars = []
    for index, ch in enumerate(text):
        if ch in ("Е", "е"):
            prev = text[index - 1] if index else ""
            at_start = not prev or (not prev.isalnum() and prev not in ("ʻ", "'"))
            chars.append(("Ye" if ch == "Е" else "ye") if at_start else ("E" if ch == "Е" else "e"))
        else:
            chars.append(CYR_TO_LAT.get(ch, ch))
    result = "".join(chars)
    result = result.replace("—", ", ").replace("–", ", ").replace(";", ", ")
    result = re.sub(r"\s+", " ", result).strip()
    result = re.sub(r"\s+([,.;:!?])", r"\1", result)
    return result

_CACHE: dict[tuple[str, str], bytes] = {}
_CACHE_ORDER: deque[tuple[str, str]] = deque()
_CACHE_LOCK = Lock()
_CACHE_MAX = 120
_RATE_LOCK = Lock()
_RATE: dict[str, deque[float]] = {}

async def synthesize(text: str, voice: str) -> bytes:
    speech_text = to_uzbek_latin(text)
    key = (voice, speech_text)
    with _CACHE_LOCK:
        cached = _CACHE.get(key)
    if cached is not None:
        return cached
    last_error = None
    for attempt in range(2):
        try:
            communication = edge_tts.Communicate(speech_text, voice, rate="+6%", volume="+0%", pitch="+0Hz")
            chunks = []
            async for chunk in communication.stream():
                if chunk.get("type") == "audio":
                    chunks.append(chunk["data"])
            audio = b"".join(chunks)
            if not audio:
                raise RuntimeError("Ovoz xizmati bo‘sh audio qaytardi")
            with _CACHE_LOCK:
                if key not in _CACHE:
                    _CACHE[key] = audio
                    _CACHE_ORDER.append(key)
                    if len(_CACHE_ORDER) > _CACHE_MAX:
                        _CACHE.pop(_CACHE_ORDER.popleft(), None)
            return audio
        except Exception as exc:
            last_error = exc
            if attempt == 0:
                await asyncio.sleep(0.35)
    raise RuntimeError(f"Ovoz xizmati ulanilmadi: {last_error}")

class Handler(BaseHTTPRequestHandler):
    server_version = "JarvisMobile/1.0"
    def log_message(self, fmt, *args):
        # Avoid logging question text or user answers.
        print("[%s] %s" % (self.log_date_time_string(), fmt % args))

    def _send(self, status: int, body: bytes, mime: str, cache: str = "no-store"):
        self.send_response(status)
        self.send_header("Content-Type", mime)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", cache)
        self.send_header("X-Content-Type-Options", "nosniff")
        self.end_headers()
        self.wfile.write(body)

    def _json(self, status: int, obj: dict):
        self._send(status, json.dumps(obj, ensure_ascii=False).encode("utf-8"), "application/json; charset=utf-8")

    def _token_ok(self) -> bool:
        import hmac
        supplied = self.headers.get("X-Jarvis-Token", "")
        return hmac.compare_digest(supplied, ACCESS_TOKEN)

    def do_GET(self):
        path = self.path.split("?", 1)[0]
        if path == "/health":
            self._json(200, {"ok": True, "service": "JARVIS Mobile TTS", "voice": "Uzbek Neural"})
            return
        if path in ("/", "/index.html"):
            try:
                data = (PUBLIC / "index.html").read_text(encoding="utf-8")
                data = data.replace("__JARVIS_ACCESS_TOKEN_JSON__", json.dumps(ACCESS_TOKEN))
                self._send(200, data.encode("utf-8"), "text/html; charset=utf-8")
            except OSError:
                self._json(500, {"error": "index.html topilmadi"})
            return
        names = {
            "/manifest.webmanifest": ("manifest.webmanifest", "application/manifest+json; charset=utf-8"),
            "/sw.js": ("sw.js", "application/javascript; charset=utf-8"),
            "/icon-192.png": ("icon-192.png", "image/png"),
            "/icon-512.png": ("icon-512.png", "image/png"),
        }
        if path in names:
            filename, mime = names[path]
            try:
                self._send(200, (PUBLIC / filename).read_bytes(), mime, "public, max-age=3600")
            except OSError:
                self._json(404, {"error": "Fayl topilmadi"})
            return
        self._json(404, {"error": "Sahifa topilmadi"})

    def do_POST(self):
        path = self.path.split("?", 1)[0]
        if path != "/tts":
            self._json(404, {"error": "Manzil topilmadi"})
            return
        if not self._token_ok():
            self._json(403, {"error": "Ruxsat berilmadi. Sahifani qayta oching."})
            return
        ip = self.client_address[0]
        now = time.time()
        with _RATE_LOCK:
            bucket = _RATE.setdefault(ip, deque())
            while bucket and now - bucket[0] > 60:
                bucket.popleft()
            if len(bucket) >= 45:
                self._json(429, {"error": "Juda ko‘p so‘rov. Bir oz kuting."})
                return
            bucket.append(now)
        try:
            length = int(self.headers.get("Content-Length", "0"))
            if length < 1 or length > 12000:
                raise ValueError("So‘rov hajmi noto‘g‘ri")
            data = json.loads(self.rfile.read(length).decode("utf-8"))
            text = str(data.get("text", "")).strip()
            voice = str(data.get("voice", "uz-UZ-SardorNeural"))
            if not text:
                raise ValueError("O‘qiladigan matn bo‘sh")
            if len(text) > 1200:
                raise ValueError("Ovozli matn juda uzun")
            if voice not in ALLOWED_VOICES:
                raise ValueError("Tanlangan ovoz mavjud emas")
            audio = asyncio.run(synthesize(text, voice))
            self._send(200, audio, "audio/mpeg", "private, max-age=0")
        except (ValueError, json.JSONDecodeError) as exc:
            self._json(400, {"error": str(exc)})
        except Exception as exc:
            self._json(502, {"error": ("Tabiiy ovoz yaratilmadi. Internetni tekshiring. " + str(exc))[:400]})

if __name__ == "__main__":
    if not (PUBLIC / "index.html").exists():
        raise SystemExit("public/index.html topilmadi")
    server = ThreadingHTTPServer((HOST, PORT), Handler)
    print(f"JARVIS mobil serveri port {PORT} da ishlamoqda.")
    print("Server HTTPS hosting orqasida ishlashi kerak; telefon uchun xavfsiz mikrofon ruxsati talab etiladi.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
