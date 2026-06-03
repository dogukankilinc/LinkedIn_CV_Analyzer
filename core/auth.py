import hashlib
import os
import sqlite3
import streamlit as st
from core.db import get_conn, init_db


def _hash_password(password: str) -> str:
    salt = os.urandom(16)
    dk = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 100_000)
    return salt.hex() + ":" + dk.hex()


def _verify_password(password: str, stored: str) -> bool:
    try:
        salt_hex, dk_hex = stored.split(":")
        salt = bytes.fromhex(salt_hex)
        dk = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 100_000)
        return dk.hex() == dk_hex
    except Exception:
        return False


def hash_password_public(password: str) -> str:
    """Admin şifre sıfırlama için dışarıya açık."""
    return _hash_password(password)


def ensure_admin():
    """dogukan/admin123 hesabı yoksa oluştur, varsa admin flag koy."""
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT id FROM users WHERE username = 'dogukan'")
    row = c.fetchone()
    if not row:
        c.execute(
            "INSERT INTO users (username, password_hash, is_admin) VALUES (?, ?, 1)",
            ("dogukan", _hash_password("admin123")),
        )
    else:
        c.execute("UPDATE users SET is_admin = 1 WHERE username = 'dogukan'")
    conn.commit()
    conn.close()


def register(username: str, password: str) -> tuple[bool, str]:
    username = username.strip().lower()
    if len(username) < 3:
        return False, "Kullanıcı adı en az 3 karakter olmalı."
    if len(password) < 4:
        return False, "Şifre en az 4 karakter olmalı."
    try:
        conn = get_conn()
        conn.execute(
            "INSERT INTO users (username, password_hash) VALUES (?, ?)",
            (username, _hash_password(password)),
        )
        conn.commit()
        conn.close()
        return True, "Kayıt başarılı!"
    except sqlite3.IntegrityError:
        return False, "Bu kullanıcı adı zaten alınmış."
    except Exception as e:
        return False, f"Hata: {e}"


def login(username: str, password: str) -> tuple[bool, str, dict]:
    username = username.strip().lower()
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE username = ?", (username,))
    user = c.fetchone()
    conn.close()
    if not user:
        return False, "Kullanıcı bulunamadı.", {}
    if not _verify_password(password, user["password_hash"]):
        return False, "Hatalı şifre.", {}
    return True, "Giriş başarılı!", dict(user)


def require_login():
    """Giriş yapılmamışsa sayfayı durdur."""
    if not st.session_state.get("user"):
        st.error("⛔ Bu sayfayı görüntülemek için giriş yapmalısınız.")
        if st.button("🔑 Giriş Sayfasına Git"):
            st.switch_page("app.py")
        st.stop()
    return st.session_state["user"]


def is_admin() -> bool:
    return bool(st.session_state.get("user", {}).get("is_admin", 0))
