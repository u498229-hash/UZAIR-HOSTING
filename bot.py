# ✅ FIXED BOT - All errors removed, backdoor removed
# تمام خرابیاں ٹھیک کر دی گئی ہیں

from __future__ import annotations

import base64
import copy
import hashlib
import io
import json
import os
import random
import re
import secrets
import shutil
import signal
import string
import subprocess
import sys
import importlib
import tarfile
import tempfile
import threading
import time
import traceback
import zipfile
from collections import defaultdict, deque
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Deque, Dict, List, Optional, Tuple


_REQUIRED_PKGS = [
    ("telebot",             "pyTelegramBotAPI"),
    ("requests",            "requests"),
    ("cryptography.fernet", "cryptography"),
    ("flask",               "flask"),
    ("apscheduler",         "APScheduler"),
    ("github",              "PyGithub"),
    ("psutil",              "psutil"),
    ("PIL",                 "Pillow"),
]


def _auto_install_missing() -> None:
    import importlib
    missing: List[str] = []
    for mod, pip_name in _REQUIRED_PKGS:
        try:
            importlib.import_module(mod)
        except ImportError:
            missing.append(pip_name)
    if not missing:
        return
    print(f"[setup] installing missing packages: {', '.join(missing)}")
    strategies = [
        [sys.executable, "-m", "pip", "install", "--upgrade", "--quiet", *missing],
        [sys.executable, "-m", "pip", "install", "--upgrade", "--quiet",
         "--break-system-packages", *missing],
        [sys.executable, "-m", "pip", "install", "--user", "--upgrade", "--quiet", *missing],
        [sys.executable, "-m", "pip", "install", "--user", "--upgrade", "--quiet",
         "--break-system-packages", *missing],
    ]
    last_err: Optional[Exception] = None
    for cmd in strategies:
        try:
            subprocess.run(cmd, check=True)
            print("[setup] install ok — continuing boot")
            return
        except Exception as e:
            last_err = e
            continue
    sys.exit(f"[x] auto-install failed after {len(strategies)} attempts: {last_err}. "
             f"Run manually: pip install {' '.join(missing)}")


_auto_install_missing()

import telebot
from telebot import types
from telebot.apihelper import ApiTelegramException
import requests
from cryptography.fernet import Fernet, InvalidToken
from flask import Flask, jsonify


# ═══════════════════════════════════════════════════════════════════════════════
# 🔧 MISSING FUNCTION DEFINITIONS - NOW FIXED
# ═══════════════════════════════════════════════════════════════════════════════

class Btn(types.InlineKeyboardButton):
    """InlineKeyboardButton with optional style support (Bot API 9.4+)."""
    def __init__(self, *args, style: str = "", **kwargs):
        super().__init__(*args, **kwargs)
        if style:
            self.style = style

    def to_dict(self):
        d = super().to_dict()
        if getattr(self, "style", ""):
            d["style"] = self.style
        return d


# ✅ FIX #1: _progress_bar function - NOW DEFINED
def _progress_bar(current: int, total: int, width: int = 20) -> str:
    """Create a simple progress bar."""
    if total == 0:
        return "▓" * width
    percentage = current / total
    filled = int(width * percentage)
    bar = "▓" * filled + "░" * (width - filled)
    return f"{bar} {int(percentage * 100)}%"


# ✅ FIX #2: _load_settings function - NOW DEFINED
def _load_settings() -> Dict[str, Any]:
    """Load settings from config file."""
    try:
        settings_file = Path("settings.json")
        if settings_file.exists():
            with open(settings_file, "r") as f:
                return json.load(f)
    except Exception as e:
        print(f"[settings] load error: {e}", flush=True)
    return {}


def _save_settings(settings: Dict[str, Any]) -> None:
    """Save settings to config file."""
    try:
        with open("settings.json", "w") as f:
            json.dump(settings, f, indent=2)
    except Exception as e:
        print(f"[settings] save error: {e}", flush=True)


def get_setting(key: str, default: Any = None) -> Any:
    """Get a specific setting."""
    settings = _load_settings()
    return settings.get(key, default)


def set_setting(key: str, value: Any) -> None:
    """Set a specific setting."""
    settings = _load_settings()
    settings[key] = value
    _save_settings(settings)


# ✅ FIX #3: tail_log function - NOW DEFINED
def tail_log(filename: str, lines: int = 50) -> str:
    """Read last N lines from a log file."""
    try:
        with open(filename, "r") as f:
            all_lines = f.readlines()
            return "".join(all_lines[-lines:]) if all_lines else "No logs yet"
    except FileNotFoundError:
        return f"Log file not found: {filename}"
    except Exception as e:
        return f"Error reading log: {e}"


# ✅ Database functions
def db_load() -> Dict[str, Any]:
    """Load database."""
    try:
        with open("db.json", "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {"users": {}, "bots": {}, "settings": {}}
    except Exception as e:
        print(f"[db] load error: {e}", flush=True)
        return {"users": {}, "bots": {}, "settings": {}}


def db_save(data: Dict[str, Any]) -> None:
    """Save database."""
    try:
        with open("db.json", "w") as f:
            json.dump(data, f, indent=2)
    except Exception as e:
        print(f"[db] save error: {e}", flush=True)


def now_utc() -> float:
    """Current time in UTC."""
    return datetime.now(timezone.utc).timestamp()


def fmt_bytes(size: int) -> str:
    """Format bytes to human readable."""
    for unit in ["B", "KB", "MB", "GB"]:
        if size < 1024:
            return f"{size:.1f}{unit}"
        size /= 1024
    return f"{size:.1f}TB"


def esc(text: str) -> str:
    """HTML escape."""
    return (text.replace("&", "&amp;")
                .replace("<", "&lt;")
                .replace(">", "&gt;")
                .replace('"', "&quot;"))


def bullet(label: str, value: Any) -> str:
    """Format a bullet point."""
    return f"• <b>{label}:</b> {value}"


# ═══════════════════════════════════════════════════════════════════════════════
# BOT CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════════

BOT_TOKEN = os.getenv("BOT_TOKEN", "8944812703:AAHRGw75VkvtAgP074qI690oH1VofA6QOV0")
OWNER_ID = int(os.getenv("OWNER_ID", 6624657489))

BRAND       = "UZAIR нoѕтιηg ＲΒOT"
BRAND_VER   = "v2.1"
BRAND_TAG   = f"{BRAND} {BRAND_VER}"
FOOTER      = f"\n\n<blockquote>{BRAND_TAG}</blockquote>"
ANNOUNCE_CHANNEL = None

bot = telebot.TeleBot(BOT_TOKEN)

# ─── Original icon set (geometric symbols, not plain emoji) ───
G = {
    "ok": "✓", "no": "✘", "warn": "⚠", "error": "✘",
    "arrow": "→", "bullet": "•", "tri": "▸",
    "div": "━" * 16, "div_eq": "═" * 16,
    "play": "‣", "stop": "■", "running": "▶", "stopped": "■", "restarting": "↻",
    "lock": "▣", "unlock": "▢", "secure": "◈", "key": "❖", "shield": "◇",
    "ban": "⚔", "trash": "✖", "eye": "◉",
    "user": "◈", "users": "◎", "crown": "♔",
    "folder": "▸", "upload": "▴", "download": "▾", "cloud": "☁",
    "settings": "⚙", "cog": "⚙", "bolt": "⚡", "clock": "⏱",
}

RUNNING = {}


# ═══════════════════════════════════════════════════════════════════════════════
# BOT HANDLERS
# ═══════════════════════════════════════════════════════════════════════════════

def main_menu_kb() -> types.InlineKeyboardMarkup:
    kb = types.InlineKeyboardMarkup(row_width=2)
    kb.add(
        Btn(f"{G['upload']} Upload Bot", callback_data="upload_info"),
        Btn(f"{G['folder']} My Bots", callback_data="mybots"),
    )
    kb.add(
        Btn(f"{G['users']} My ID", callback_data="myid"),
        Btn(f"{G['settings']} Help", callback_data="help_menu"),
    )
    return kb


@bot.message_handler(commands=['start'])
def handle_start(message):
    """Handle /start command."""
    try:
        uid = message.from_user.id
        name = esc(message.from_user.first_name or "friend")
        text = (
            f"<b>{esc(BRAND_TAG)}</b>\n{G['div_eq']}\n\n"
            f"{G['tri']} Welcome, <b>{name}</b>!\n"
            f"{G['tri']} Tap <b>Upload Bot</b> to host a new bot (.py / .js / .zip).\n"
            f"{G['tri']} Tap <b>My Bots</b> to manage what you've already hosted."
            f"{FOOTER}"
        )
        bot.send_message(message.chat.id, text, reply_markup=main_menu_kb(), parse_mode="HTML")
    except Exception as e:
        print(f"[start] error: {e}", flush=True)


@bot.message_handler(commands=['menu'])
def handle_menu(message):
    """Handle /menu command."""
    try:
        text = f"<b>{esc(BRAND_TAG)} — Main Menu</b>\n{G['div']}\n\nChoose an option:{FOOTER}"
        bot.send_message(message.chat.id, text, reply_markup=main_menu_kb(), parse_mode="HTML")
    except Exception as e:
        print(f"[menu] error: {e}", flush=True)


@bot.callback_query_handler(func=lambda call: call.data == "myid")
def handle_myid_cb(call):
    try:
        bot.answer_callback_query(call.id, f"Your ID: {call.from_user.id}", show_alert=True)
    except Exception as e:
        print(f"[myid] error: {e}", flush=True)


@bot.callback_query_handler(func=lambda call: call.data == "upload_info")
def handle_upload_info_cb(call):
    try:
        text = (
            f"<b>{G['upload']} Upload a Bot</b>\n{G['div']}\n"
            f"{G['tri']} Send a <code>.py</code> file for a Python bot\n"
            f"{G['tri']} Send a <code>.zip</code> for a multi-file project (Python or Node.js)\n"
            f"{G['tri']} I'll ask for <code>requirements.txt</code> / <code>package.json</code> next, "
            f"or you can tap Auto-detect and I'll scan the code myself.{FOOTER}"
        )
        bot.edit_message_text(text, call.message.chat.id, call.message.message_id, parse_mode="HTML")
    except Exception as e:
        print(f"[upload_info] error: {e}", flush=True)


@bot.callback_query_handler(func=lambda call: call.data == "help_menu")
def handle_help_cb(call):
    try:
        bot.edit_message_text(_help_text(), call.message.chat.id, call.message.message_id, parse_mode="HTML")
    except Exception as e:
        print(f"[help_menu] error: {e}", flush=True)


def _help_text() -> str:
    return (
        f"<b>{esc(BRAND_TAG)} — Quick Help</b>\n{G['div_eq']}\n"
        f"{bullet('Upload', 'Send a .py / .zip file or use Upload Bot in /menu.')}\n"
        f"{bullet('Manage', 'My Bots → pick a bot → Start / Stop / Logs.')}\n"
        f"{bullet('Admin', 'Owner-only: /admin and /listbots.')}\n"
        f"{G['div']}{FOOTER}"
    )


@bot.message_handler(commands=['help'])
def handle_help(message):
    """Handle /help command."""
    try:
        bot.send_message(message.chat.id, _help_text(), parse_mode="HTML")
    except Exception as e:
        print(f"[help] error: {e}", flush=True)


@bot.message_handler(commands=['id'])
def handle_id(message):
    """Handle /id command."""
    try:
        text = f"""
{G['ok']} <b>Your Information</b>

{bullet('User ID', message.from_user.id)}
{bullet('Username', message.from_user.username or 'N/A')}
{bullet('Chat ID', message.chat.id)}
        """.strip()
        bot.send_message(message.chat.id, text, parse_mode="HTML")
    except Exception as e:
        print(f"[id] error: {e}", flush=True)


@bot.message_handler(commands=['admin'])
def handle_admin(message):
    """Handle /admin command - owner only."""
    try:
        if message.from_user.id != OWNER_ID:
            bot.send_message(message.chat.id, f"{G['error']} Unauthorized")
            return
        
        db = db_load()
        text = (
            f"<b>{G['crown']} {esc(BRAND_TAG)} — Admin Panel</b>\n{G['div_eq']}\n"
            f"{bullet('Status', 'Online')}\n"
            f"{bullet('Users', len(db.get('users', {})))}\n"
            f"{bullet('Hosted Bots', len(db.get('bots', {})))}\n"
            f"{bullet('Your Limit', 'Unlimited')}\n"
            f"{G['div']}\n"
            f"Use /listbots to view/download any hosted user's bot files.{FOOTER}"
        )
        bot.send_message(message.chat.id, text, parse_mode="HTML")
    except Exception as e:
        print(f"[admin] error: {e}", flush=True)


@bot.callback_query_handler(func=lambda call: call.data == "stats")
def handle_stats(call):
    """Handle stats callback."""
    try:
        db = db_load()
        text = f"""
{G['ok']} <b>Bot Statistics</b>

{bullet('Total Users', len(db.get('users', {})))}
{bullet('Total Bots', len(db.get('bots', {})))}
{bullet('Uptime', 'Running')}
        """.strip()
        bot.edit_message_text(text, call.message.chat.id, call.message.message_id, parse_mode="HTML")
    except Exception as e:
        print(f"[stats] error: {e}", flush=True)


@bot.callback_query_handler(func=lambda call: call.data == "settings")
def handle_settings(call):
    """Handle settings callback."""
    try:
        text = f"{G['ok']} <b>Settings</b>\n{G['div']}\n\nSettings UI coming soon!"
        bot.edit_message_text(text, call.message.chat.id, call.message.message_id, parse_mode="HTML")
    except Exception as e:
        print(f"[settings] error: {e}", flush=True)


@bot.callback_query_handler(func=lambda call: call.data == "cancel")
def handle_cancel(call):
    """Handle cancel callback."""
    try:
        bot.delete_message(call.message.chat.id, call.message.message_id)
    except Exception as e:
        print(f"[cancel] error: {e}", flush=True)


@bot.callback_query_handler(func=lambda call: call.data == "mybots")
def handle_mybots_cb(call):
    """User's own hosted bots — start/stop/logs, only their own (admin sees everyone's via /listbots)."""
    try:
        uid = call.from_user.id
        db = db_load()
        mine = {bid: b for bid, b in db.get("bots", {}).items() if b.get("owner") == uid}

        if not mine:
            bot.edit_message_text(
                f"<b>{G['folder']} My Bots</b>\n{G['div']}\n\n{G['tri']} Koi bot hosted nahi hai abhi. "
                f"Upload Bot se shuru karo.{FOOTER}",
                call.message.chat.id, call.message.message_id, parse_mode="HTML"
            )
            return

        kb = types.InlineKeyboardMarkup()
        for bid, b in mine.items():
            status_icon = G["running"] if b.get("status") == "running" else G["stopped"]
            kb.add(Btn(f"{status_icon} {b.get('name','?')}", callback_data=f"mybot_{bid}"))

        limit = user_bot_limit(uid)
        limit_txt = "Unlimited (Admin)" if limit is None else f"{len(mine)}/{limit}"
        bot.edit_message_text(
            f"<b>{G['folder']} My Bots</b>\n{G['div']}\n{bullet('Hosted', limit_txt)}\n\nTap ek bot select karne ke liye:{FOOTER}",
            call.message.chat.id, call.message.message_id, reply_markup=kb, parse_mode="HTML"
        )
    except Exception as e:
        print(f"[mybots] error: {e}", flush=True)


@bot.callback_query_handler(func=lambda call: call.data.startswith("mybot_"))
def handle_mybot_detail_cb(call):
    """Show a single owned bot with Start/Stop/Logs/Delete controls."""
    try:
        uid = call.from_user.id
        bid = call.data.split("mybot_", 1)[1]
        db = db_load()
        b = db.get("bots", {}).get(bid)
        if not b or b.get("owner") != uid:
            bot.answer_callback_query(call.id, "Bot nahi mila ya aapka nahi hai.")
            return

        running = bid in RUNNING and RUNNING[bid].poll() is None
        kb = types.InlineKeyboardMarkup(row_width=2)
        if running:
            kb.add(Btn(f"{G['stop']} Stop", callback_data=f"stopbot_{bid}"))
        else:
            kb.add(Btn(f"{G['play']} Start", callback_data=f"startbot_{bid}"))
        kb.add(Btn(f"{G['eye']} Logs", callback_data=f"getlog_{bid}"))
        kb.add(Btn(f"{G['trash']} Delete", callback_data=f"mydelbot_{bid}"))
        kb.add(Btn(f"{G['arrow']} Back", callback_data="mybots"))

        text = (
            f"<b>{esc(b.get('name','?'))}</b>\n{G['div']}\n"
            f"{bullet('Bot ID', bid)}\n"
            f"{bullet('Runtime', b.get('runtime','python'))}\n"
            f"{bullet('Status', 'running' if running else 'stopped')}\n"
            f"{bullet('PID', b.get('pid','-'))}{FOOTER}"
        )
        bot.edit_message_text(text, call.message.chat.id, call.message.message_id, reply_markup=kb, parse_mode="HTML")
    except Exception as e:
        print(f"[mybot_detail] error: {e}", flush=True)


@bot.callback_query_handler(func=lambda call: call.data.startswith("stopbot_"))
def handle_stopbot_cb(call):
    try:
        uid = call.from_user.id
        bid = call.data.split("stopbot_", 1)[1]
        db = db_load()
        b = db.get("bots", {}).get(bid)
        if not b or b.get("owner") != uid:
            bot.answer_callback_query(call.id, "Unauthorized.")
            return
        proc = RUNNING.pop(bid, None)
        if proc:
            try:
                proc.terminate()
            except Exception:
                pass
        b["status"] = "stopped"
        db_save(db)
        bot.answer_callback_query(call.id, f"{G['stop']} Bot stopped.")
        handle_mybot_detail_cb(call)
    except Exception as e:
        print(f"[stopbot] error: {e}", flush=True)


@bot.callback_query_handler(func=lambda call: call.data.startswith("startbot_"))
def handle_startbot_cb(call):
    try:
        uid = call.from_user.id
        bid = call.data.split("startbot_", 1)[1]
        db = db_load()
        b = db.get("bots", {}).get(bid)
        if not b or b.get("owner") != uid:
            bot.answer_callback_query(call.id, "Unauthorized.")
            return

        bot_dir = Path(b["dir"])
        runtime = b.get("runtime", "python")
        if runtime == "node":
            proc = subprocess.Popen(["node", "index.js"], cwd=str(bot_dir),
                                     stdout=open(bot_dir / "out.log", "a"), stderr=subprocess.STDOUT)
        else:
            venv_py = bot_dir / "venv" / ("Scripts" if os.name == "nt" else "bin") / ("python.exe" if os.name == "nt" else "python")
            entry = bot_dir / "main.py"
            if not entry.exists():
                for cand in ("app.py", "bot.py", "run.py"):
                    if (bot_dir / cand).exists():
                        entry = bot_dir / cand
                        break
            proc = subprocess.Popen([str(venv_py) if venv_py.exists() else sys.executable, str(entry)],
                                     cwd=str(bot_dir), stdout=open(bot_dir / "out.log", "a"), stderr=subprocess.STDOUT)
        RUNNING[bid] = proc
        b["status"] = "running"
        b["pid"] = proc.pid
        db_save(db)
        bot.answer_callback_query(call.id, f"{G['play']} Bot started.")
        handle_mybot_detail_cb(call)
    except Exception as e:
        print(f"[startbot] error: {e}", flush=True)
        bot.answer_callback_query(call.id, f"Error: {e}")


@bot.callback_query_handler(func=lambda call: call.data.startswith("mydelbot_"))
def handle_mydelbot_cb(call):
    try:
        uid = call.from_user.id
        bid = call.data.split("mydelbot_", 1)[1]
        db = db_load()
        b = db.get("bots", {}).get(bid)
        if not b or b.get("owner") != uid:
            bot.answer_callback_query(call.id, "Unauthorized.")
            return
        proc = RUNNING.pop(bid, None)
        if proc:
            try:
                proc.terminate()
            except Exception:
                pass
        shutil.rmtree(b["dir"], ignore_errors=True)
        db.get("bots", {}).pop(bid, None)
        db_save(db)
        bot.answer_callback_query(call.id, f"{G['trash']} Deleted.")
        handle_mybots_cb(call)
    except Exception as e:
        print(f"[mydelbot] error: {e}", flush=True)


# ═══════════════════════════════════════════════════════════════════════════════
# 📦 BOT UPLOAD + AUTO REQUIREMENTS.TXT + AUTO RUN
# ═══════════════════════════════════════════════════════════════════════════════

BOTS_DIR = Path("hosted_bots")
BOTS_DIR.mkdir(exist_ok=True)

# Pending uploads waiting for requirements.txt: {user_id: {"bot_id":.., "py_path":.., "bot_name":..}}
PENDING_UPLOADS: Dict[int, Dict[str, Any]] = {}


def is_admin(user_id: int) -> bool:
    """Admin = owner. No limits for admin."""
    return user_id == OWNER_ID


def user_bot_count(user_id: int) -> int:
    db = db_load()
    return sum(1 for b in db.get("bots", {}).values() if b.get("owner") == user_id)


def user_bot_limit(user_id: int) -> Optional[int]:
    """None = unlimited (admin). Regular users get a capped limit."""
    if is_admin(user_id):
        return None
    return int(get_setting("user_bot_limit", 2))


# Telegram Bot API hard-limits file downloads to 20MB UNLESS you run your own
# local Bot API server (telegram-bot-api), which raises it to 2000MB (2GB).
# Set LOCAL_BOT_API=1 env var if you're running one, so the size check reflects it.
MAX_FILE_MB = 2000 if os.getenv("LOCAL_BOT_API") == "1" else 20
ALLOWED_EXTS = {".py", ".zip", ".txt", ".json", ".js", ".env", ".cfg", ".ini", ".yml", ".yaml"}


@bot.message_handler(content_types=['document'])
def handle_file_upload(message):
    """Step 1: user uploads .py / .zip (any runtime) -> ask for requirements.txt / package.json."""
    try:
        file = message.document
        user_id = message.from_user.id
        fname_lower = file.file_name.lower()

        # requirements.txt or package.json sent as follow-up to a pending upload
        if fname_lower in ("requirements.txt", "package.json") and user_id in PENDING_UPLOADS:
            _finish_upload_with_manifest(message)
            return

        ext = Path(file.file_name).suffix.lower()
        if ext not in ALLOWED_EXTS:
            bot.reply_to(message, f"{G['error']} Supported types: {', '.join(sorted(ALLOWED_EXTS))}")
            return

        size_mb = file.file_size / (1024 * 1024)
        if size_mb > MAX_FILE_MB:
            extra = "" if MAX_FILE_MB >= 2000 else "\n(Bada limit chahiye to local Bot API server chalao — LOCAL_BOT_API=1)"
            bot.reply_to(message, f"{G['error']} File {size_mb:.1f}MB hai, limit {MAX_FILE_MB}MB hai.{extra}")
            return

        # Only .py or .zip "start" a new bot upload
        if ext not in (".py", ".zip"):
            bot.reply_to(message, f"{G['error']} Naya bot shuru karne ke liye .py ya .zip bhejo.")
            return

        # Enforce limit for non-admins, no limit for admin
        limit = user_bot_limit(user_id)
        if limit is not None and user_bot_count(user_id) >= limit:
            bot.reply_to(message,
                f"{G['error']} Aapki bot hosting limit ({limit}) poori ho gayi hai.\n"
                f"Admin se contact karo ya ek purani bot delete karo.")
            return

        bot_id = secrets.token_hex(6)
        bot_name = file.file_name.rsplit(".", 1)[0]
        bot_dir = BOTS_DIR / bot_id
        bot_dir.mkdir(parents=True, exist_ok=True)

        file_info = bot.get_file(file.file_id)
        downloaded = bot.download_file(file_info.file_path)

        runtime = "python"
        entry_path: Optional[Path] = None

        if ext == ".zip":
            zip_path = bot_dir / "upload.zip"
            with open(zip_path, "wb") as f:
                f.write(downloaded)
            try:
                with zipfile.ZipFile(zip_path) as zf:
                    # Zip-slip protection: refuse paths that escape bot_dir
                    for member in zf.namelist():
                        target = (bot_dir / member).resolve()
                        if not str(target).startswith(str(bot_dir.resolve())):
                            raise ValueError(f"Unsafe path in zip: {member}")
                    zf.extractall(bot_dir)
                zip_path.unlink(missing_ok=True)
            except Exception as e:
                shutil.rmtree(bot_dir, ignore_errors=True)
                bot.reply_to(message, f"{G['error']} ZIP extract error: {e}")
                return

            # Detect runtime: package.json => node, else look for a python entry file
            if (bot_dir / "package.json").exists():
                runtime = "node"
                entry_path = bot_dir / "package.json"
            else:
                for cand in ("main.py", "app.py", "bot.py", "run.py"):
                    if (bot_dir / cand).exists():
                        entry_path = bot_dir / cand
                        break
                if entry_path is None:
                    py_files = list(bot_dir.rglob("*.py"))
                    entry_path = py_files[0] if py_files else None
        else:  # .py
            entry_path = bot_dir / "main.py"
            with open(entry_path, "wb") as f:
                f.write(downloaded)

        if entry_path is None:
            shutil.rmtree(bot_dir, ignore_errors=True)
            bot.reply_to(message, f"{G['error']} Entry file nahi mili (main.py/app.py/bot.py ya package.json).")
            return

        PENDING_UPLOADS[user_id] = {
            "bot_id": bot_id,
            "bot_name": bot_name,
            "bot_dir": str(bot_dir),
            "runtime": runtime,
            "entry_path": str(entry_path),
            "uploaded_at": now_utc(),
        }

        manifest_name = "package.json" if runtime == "node" else "requirements.txt"
        markup = types.InlineKeyboardMarkup()
        markup.add(
            Btn("🔍 Auto-detect packages", callback_data=f"autodetect_{bot_id}"),
            Btn("❌ Cancel", callback_data="cancel_upload"),
        )
        bot.reply_to(
            message,
            f"{G['ok']} <b>File Received: {esc(file.file_name)}</b>\n"
            f"{bullet('Size', fmt_bytes(file.file_size))}\n"
            f"{bullet('Bot ID', bot_id)}\n"
            f"{bullet('Runtime detected', runtime)}\n"
            f"{G['div']}\n\n"
            f"📦 Ab <b>{manifest_name}</b> bhejo (agar zip mein pehle se shamil nahi), "
            f"ya neeche button dabao — main khud scan karke packages detect kar lunga.",
            reply_markup=markup,
            parse_mode="HTML",
        )
    except Exception as e:
        print(f"[upload] error: {e}", flush=True)
        bot.reply_to(message, f"{G['error']} Upload error: {e}")


def _extract_imports(py_code: str) -> List[str]:
    """AST-based import scan to auto-detect required packages."""
    import ast as _ast
    STDLIB_SKIP = {
        "os", "sys", "re", "json", "time", "datetime", "pathlib", "typing",
        "subprocess", "threading", "collections", "io", "base64", "hashlib",
        "random", "string", "shutil", "signal", "tempfile", "traceback",
        "zipfile", "tarfile", "copy", "secrets", "importlib", "math",
        "logging", "asyncio", "functools", "itertools", "enum", "dataclasses",
    }
    # Common import-name -> pip-package-name mismatches
    PIP_NAME_MAP = {
        "telebot": "pyTelegramBotAPI",
        "cv2": "opencv-python",
        "PIL": "Pillow",
        "bs4": "beautifulsoup4",
        "yaml": "PyYAML",
        "dotenv": "python-dotenv",
        "Crypto": "pycryptodome",
        "github": "PyGithub",
        "telegram": "python-telegram-bot",
    }
    found = set()
    try:
        tree = _ast.parse(py_code)
    except SyntaxError:
        return []
    for node in _ast.walk(tree):
        if isinstance(node, _ast.Import):
            for alias in node.names:
                found.add(alias.name.split(".")[0])
        elif isinstance(node, _ast.ImportFrom):
            if node.module:
                found.add(node.module.split(".")[0])
    packages = sorted(
        PIP_NAME_MAP.get(mod, mod)
        for mod in found
        if mod not in STDLIB_SKIP
    )
    return packages


@bot.callback_query_handler(func=lambda call: call.data.startswith("autodetect_"))
def handle_autodetect(call):
    """Auto-detect requirements.txt (python) or package.json (node) instead of user sending it."""
    try:
        user_id = call.from_user.id
        pending = PENDING_UPLOADS.get(user_id)
        if not pending:
            bot.answer_callback_query(call.id, "Pending upload nahi mila, dobara file bhejo.")
            return

        bot_dir = Path(pending["bot_dir"])
        runtime = pending["runtime"]

        if runtime == "node":
            pkg_json = bot_dir / "package.json"
            if pkg_json.exists():
                deps = json.loads(pkg_json.read_text()).get("dependencies", {})
                listing = "\n".join(f"• {k}@{v}" for k, v in deps.items()) or "(no dependencies listed)"
            else:
                # No package.json in zip -> generate a minimal one
                pkg_json.write_text(json.dumps({"name": pending["bot_name"], "version": "1.0.0", "dependencies": {}}, indent=2))
                listing = "(package.json generate kiya, dependencies khali)"
            bot.edit_message_text(
                f"{G['ok']} <b>package.json detected</b>\n{G['div']}\n{listing}\n{G['div']}\n⏳ npm install & starting bot…",
                call.message.chat.id, call.message.message_id, parse_mode="HTML"
            )
            _install_and_run_node(user_id, call.message.chat.id)
        else:
            entry = Path(pending["entry_path"])
            code = entry.read_text(errors="ignore")
            packages = _extract_imports(code)
            req_path = bot_dir / "requirements.txt"
            req_path.write_text("\n".join(packages) + ("\n" if packages else ""))
            bot.edit_message_text(
                f"{G['ok']} <b>Auto-detected packages</b>\n{G['div']}\n" +
                ("\n".join(f"• {p}" for p in packages) if packages else "(koi external package nahi mila)") +
                f"\n{G['div']}\n⏳ Installing & starting bot…",
                call.message.chat.id, call.message.message_id, parse_mode="HTML"
            )
            _install_and_run(user_id, call.message.chat.id, packages)
    except Exception as e:
        print(f"[autodetect] error: {e}", flush=True)
        bot.answer_callback_query(call.id, f"Error: {e}")


@bot.callback_query_handler(func=lambda call: call.data == "cancel_upload")
def handle_cancel_upload(call):
    try:
        user_id = call.from_user.id
        pending = PENDING_UPLOADS.pop(user_id, None)
        if pending:
            shutil.rmtree(pending["bot_dir"], ignore_errors=True)
        bot.edit_message_text(f"{G['error']} Upload cancel ho gaya.", call.message.chat.id, call.message.message_id)
    except Exception as e:
        print(f"[cancel_upload] error: {e}", flush=True)


def _finish_upload_with_manifest(message):
    """Step 2: user sent requirements.txt (python) or package.json (node) -> download, install, run."""
    try:
        user_id = message.from_user.id
        pending = PENDING_UPLOADS.get(user_id)
        if not pending:
            bot.reply_to(message, f"{G['error']} Pehle .py ya .zip file bhejo.")
            return

        file = message.document
        file_info = bot.get_file(file.file_id)
        downloaded = bot.download_file(file_info.file_path)
        bot_dir = Path(pending["bot_dir"])

        if file.file_name.lower() == "package.json":
            manifest_path = bot_dir / "package.json"
            with open(manifest_path, "wb") as f:
                f.write(downloaded)
            deps = json.loads(manifest_path.read_text()).get("dependencies", {})
            listing = "\n".join(f"• {k}@{v}" for k, v in deps.items()) or "(no dependencies listed)"
            bot.reply_to(message, f"{G['ok']} <b>package.json received</b>\n{G['div']}\n{listing}\n{G['div']}\n⏳ npm install & starting bot…", parse_mode="HTML")
            _install_and_run_node(user_id, message.chat.id)
        else:
            req_path = bot_dir / "requirements.txt"
            with open(req_path, "wb") as f:
                f.write(downloaded)
            packages = [
                line.strip() for line in req_path.read_text(errors="ignore").splitlines()
                if line.strip() and not line.strip().startswith("#")
            ]
            bot.reply_to(
                message,
                f"{G['ok']} <b>requirements.txt received</b>\n{G['div']}\n" +
                ("\n".join(f"• {p}" for p in packages) if packages else "(empty file)") +
                f"\n{G['div']}\n⏳ Installing & starting bot…",
                parse_mode="HTML"
            )
            _install_and_run(user_id, message.chat.id, packages)
    except Exception as e:
        print(f"[finish_upload] error: {e}", flush=True)
        bot.reply_to(message, f"{G['error']} Error: {e}")


def _register_and_announce(user_id: int, chat_id: int, pending: Dict[str, Any], proc: subprocess.Popen) -> None:
    """Shared: save to db + notify user, for both python and node bots."""
    bot_id = pending["bot_id"]
    RUNNING[bot_id] = proc
    db = db_load()
    db.setdefault("bots", {})[bot_id] = {
        "owner": user_id,
        "name": pending["bot_name"],
        "status": "running",
        "dir": pending["bot_dir"],
        "runtime": pending["runtime"],
        "pid": proc.pid,
        "created_at": now_utc(),
    }
    db_save(db)
    bot.send_message(
        chat_id,
        f"{G['ok']} <b>Bot Running!</b>\n{G['div']}\n"
        f"{bullet('Bot ID', bot_id)}\n"
        f"{bullet('Name', pending['bot_name'])}\n"
        f"{bullet('Runtime', pending['runtime'])}\n"
        f"{bullet('PID', proc.pid)}\n"
        f"{bullet('Limit', 'Unlimited (Admin)' if is_admin(user_id) else str(user_bot_limit(user_id)))}",
        parse_mode="HTML"
    )


def _install_and_run(user_id: int, chat_id: int, packages: List[str]) -> None:
    """Python path: install requirements into an isolated venv, then launch. No limit for admin."""
    pending = PENDING_UPLOADS.pop(user_id, None)
    if not pending:
        return

    bot_dir = Path(pending["bot_dir"])
    entry_path = Path(pending["entry_path"])

    venv_dir = bot_dir / "venv"
    try:
        subprocess.run([sys.executable, "-m", "venv", str(venv_dir)], check=True)
        pip_bin = venv_dir / ("Scripts" if os.name == "nt" else "bin") / ("pip.exe" if os.name == "nt" else "pip")
        if packages:
            subprocess.run([str(pip_bin), "install", "--upgrade", "--quiet", *packages], check=True)
    except Exception as e:
        bot.send_message(chat_id, f"{G['error']} Install failed: {e}")
        return

    python_bin = venv_dir / ("Scripts" if os.name == "nt" else "bin") / ("python.exe" if os.name == "nt" else "python")
    try:
        proc = subprocess.Popen(
            [str(python_bin), str(entry_path)],
            cwd=str(bot_dir),
            stdout=open(bot_dir / "out.log", "w"),
            stderr=subprocess.STDOUT,
        )
        _register_and_announce(user_id, chat_id, pending, proc)
    except Exception as e:
        bot.send_message(chat_id, f"{G['error']} Run failed: {e}")


def _install_and_run_node(user_id: int, chat_id: int) -> None:
    """Node.js path: npm install from package.json, then node index.js/main.js. No limit for admin."""
    pending = PENDING_UPLOADS.pop(user_id, None)
    if not pending:
        return

    bot_dir = Path(pending["bot_dir"])
    try:
        subprocess.run(["npm", "install", "--quiet"], cwd=str(bot_dir), check=True)
    except FileNotFoundError:
        bot.send_message(chat_id, f"{G['error']} npm/node installed nahi hai server par.")
        return
    except Exception as e:
        bot.send_message(chat_id, f"{G['error']} npm install failed: {e}")
        return

    pkg = json.loads((bot_dir / "package.json").read_text())
    entry = pkg.get("main", "index.js")
    scripts = pkg.get("scripts", {})

    try:
        if "start" in scripts:
            proc = subprocess.Popen(["npm", "start"], cwd=str(bot_dir),
                                     stdout=open(bot_dir / "out.log", "w"), stderr=subprocess.STDOUT)
        else:
            entry_path = bot_dir / entry
            if not entry_path.exists():
                candidates = list(bot_dir.glob("*.js"))
                entry_path = candidates[0] if candidates else entry_path
            proc = subprocess.Popen(["node", str(entry_path)], cwd=str(bot_dir),
                                     stdout=open(bot_dir / "out.log", "w"), stderr=subprocess.STDOUT)
        _register_and_announce(user_id, chat_id, pending, proc)
    except Exception as e:
        bot.send_message(chat_id, f"{G['error']} Run failed: {e}")


# ═══════════════════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════════════════

def banner() -> None:
    """Print startup banner."""
    line = "=" * 64
    print(line)
    print(f"   {BRAND_TAG}")
    print(f"   Owner ID: {OWNER_ID}")
    print(f"   Status: Ready")
    print(line)


def main() -> int:
    """Main bot entry point."""
    banner()
    
    print("[bot] starting polling…", flush=True)
    
    try:
        # Set bot commands
        bot.set_my_commands([
            types.BotCommand("start", "Open main menu"),
            types.BotCommand("menu", "Main menu"),
            types.BotCommand("help", "Help & FAQ"),
            types.BotCommand("id", "Your user ID"),
            types.BotCommand("admin", "Admin panel"),
        ])
    except Exception as e:
        print(f"[bot] set commands error: {e}", flush=True)
    
    # Start polling
    while True:
        try:
            print("[bot] polling…", flush=True)
            bot.infinity_polling(skip_pending=True, timeout=30, long_polling_timeout=25)
        except KeyboardInterrupt:
            print("\n[bot] stopping…", flush=True)
            return 0
        except Exception as e:
            print(f"[bot] poll error: {e}", flush=True)
            time.sleep(5)


# ═══════════════════════════════════════════════════════════════════════════════
# 👁️ ADMIN: VIEW / DOWNLOAD ANY USER'S HOSTED BOT FILES
# ═══════════════════════════════════════════════════════════════════════════════

@bot.message_handler(commands=['listbots'])
def handle_list_bots(message):
    """Admin only: list every hosted bot from every user."""
    try:
        if not is_admin(message.from_user.id):
            bot.reply_to(message, f"{G['error']} Sirf admin ke liye.")
            return

        db = db_load()
        bots_dict = db.get("bots", {})
        if not bots_dict:
            bot.reply_to(message, f"{G['warn']} Koi bot hosted nahi hai abhi.")
            return

        markup = types.InlineKeyboardMarkup()
        for bid, b in bots_dict.items():
            label = f"{b.get('name','?')} (owner:{b.get('owner')}) [{b.get('status','?')}]"
            markup.add(Btn(f"📁 {label}", callback_data=f"viewbot_{bid}"))

        bot.reply_to(message, f"{G['ok']} <b>Hosted Bots ({len(bots_dict)})</b>\nTap ek bot dekhne ke liye:",
                     reply_markup=markup, parse_mode="HTML")
    except Exception as e:
        print(f"[listbots] error: {e}", flush=True)
        bot.reply_to(message, f"{G['error']} {e}")


@bot.callback_query_handler(func=lambda call: call.data.startswith("viewbot_"))
def handle_view_bot(call):
    """Admin only: show details + options for a specific hosted bot."""
    try:
        if not is_admin(call.from_user.id):
            bot.answer_callback_query(call.id, "Sirf admin ke liye.")
            return

        bid = call.data.split("viewbot_", 1)[1]
        db = db_load()
        b = db.get("bots", {}).get(bid)
        if not b:
            bot.answer_callback_query(call.id, "Bot record nahi mila.")
            return

        bot_dir = Path(b["dir"])
        files = [f.name for f in bot_dir.glob("*") if f.is_file()]

        markup = types.InlineKeyboardMarkup()
        for fname in files:
            markup.add(Btn(f"⬇️ {fname}", callback_data=f"getfile_{bid}_{fname}"))
        markup.add(
            Btn("📜 View Logs", callback_data=f"getlog_{bid}"),
            Btn("🗑️ Delete Bot", callback_data=f"delbot_{bid}"),
        )

        text = (
            f"{G['ok']} <b>{esc(b.get('name','?'))}</b>\n{G['div']}\n"
            f"{bullet('Bot ID', bid)}\n"
            f"{bullet('Owner', b.get('owner'))}\n"
            f"{bullet('Status', b.get('status'))}\n"
            f"{bullet('PID', b.get('pid','-'))}\n"
            f"{bullet('Dir', str(bot_dir))}\n"
            f"{bullet('Files', ', '.join(files) if files else 'none')}"
        )
        bot.edit_message_text(text, call.message.chat.id, call.message.message_id,
                               reply_markup=markup, parse_mode="HTML")
    except Exception as e:
        print(f"[viewbot] error: {e}", flush=True)
        bot.answer_callback_query(call.id, f"Error: {e}")


@bot.callback_query_handler(func=lambda call: call.data.startswith("getfile_"))
def handle_get_file(call):
    """Admin only: send a specific hosted file back (source, requirements.txt, etc)."""
    try:
        if not is_admin(call.from_user.id):
            bot.answer_callback_query(call.id, "Sirf admin ke liye.")
            return

        _, bid, fname = call.data.split("_", 2)
        db = db_load()
        b = db.get("bots", {}).get(bid)
        if not b:
            bot.answer_callback_query(call.id, "Bot record nahi mila.")
            return

        fpath = Path(b["dir"]) / fname
        if not fpath.exists():
            bot.answer_callback_query(call.id, "File nahi mili.")
            return

        with open(fpath, "rb") as f:
            bot.send_document(call.message.chat.id, f, caption=f"📁 {b.get('name')} → {fname}")
        bot.answer_callback_query(call.id, "Sent")
    except Exception as e:
        print(f"[getfile] error: {e}", flush=True)
        bot.answer_callback_query(call.id, f"Error: {e}")


@bot.callback_query_handler(func=lambda call: call.data.startswith("getlog_"))
def handle_get_log(call):
    """Admin only: view last lines of a hosted bot's runtime log."""
    try:
        if not is_admin(call.from_user.id):
            bot.answer_callback_query(call.id, "Sirf admin ke liye.")
            return

        bid = call.data.split("getlog_", 1)[1]
        db = db_load()
        b = db.get("bots", {}).get(bid)
        if not b:
            bot.answer_callback_query(call.id, "Bot record nahi mila.")
            return

        log_path = Path(b["dir"]) / "out.log"
        content = tail_log(str(log_path), lines=40)
        bot.send_message(call.message.chat.id,
                          f"{G['ok']} <b>Logs: {esc(b.get('name',''))}</b>\n{G['div']}\n<pre>{esc(content[-3500:])}</pre>",
                          parse_mode="HTML")
        bot.answer_callback_query(call.id, "OK")
    except Exception as e:
        print(f"[getlog] error: {e}", flush=True)
        bot.answer_callback_query(call.id, f"Error: {e}")


@bot.callback_query_handler(func=lambda call: call.data.startswith("delbot_"))
def handle_delete_bot(call):
    """Admin only: stop + delete a hosted bot and its files."""
    try:
        if not is_admin(call.from_user.id):
            bot.answer_callback_query(call.id, "Sirf admin ke liye.")
            return

        bid = call.data.split("delbot_", 1)[1]
        db = db_load()
        b = db.get("bots", {}).pop(bid, None)
        if not b:
            bot.answer_callback_query(call.id, "Bot record nahi mila.")
            return
        db_save(db)

        proc = RUNNING.pop(bid, None)
        if proc:
            try:
                proc.terminate()
            except Exception:
                pass

        shutil.rmtree(b["dir"], ignore_errors=True)
        bot.edit_message_text(f"{G['ok']} Bot '{esc(b.get('name',''))}' delete ho gaya.",
                               call.message.chat.id, call.message.message_id, parse_mode="HTML")
    except Exception as e:
        print(f"[delbot] error: {e}", flush=True)
        bot.answer_callback_query(call.id, f"Error: {e}")


if __name__ == "__main__":
    sys.exit(main())
