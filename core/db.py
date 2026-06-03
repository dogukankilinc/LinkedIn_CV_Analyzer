import sqlite3
import json
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / "data" / "figes_cv.db"


def get_conn() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH), check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Veritabanı tablolarını oluşturur (yoksa)."""
    conn = get_conn()
    c = conn.cursor()

    c.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id            INTEGER PRIMARY KEY AUTOINCREMENT,
        username      TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        is_admin      INTEGER DEFAULT 0,
        created_at    TEXT DEFAULT (datetime('now','localtime'))
    )""")

    c.execute("""
    CREATE TABLE IF NOT EXISTS analyses (
        id           INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id      INTEGER NOT NULL,
        ad_soyad     TEXT,
        sektor       TEXT,
        model        TEXT,
        language     TEXT,
        sure_str     TEXT,
        potansiyel   TEXT,
        json_result  TEXT,
        pdf_data     BLOB,
        created_at   TEXT DEFAULT (datetime('now','localtime')),
        FOREIGN KEY (user_id) REFERENCES users(id)
    )""")

    conn.commit()
    conn.close()


def save_analysis(user_id: int, ad_soyad: str, sektor: str, model: str,
                  language: str, sure_str: str, potansiyel: str,
                  json_result: dict, pdf_data: bytes | None) -> int:
    """Analizi kaydeder. Her kullanıcı için en fazla 10 analiz saklanır."""
    conn = get_conn()
    c = conn.cursor()

    c.execute("""
        INSERT INTO analyses
            (user_id, ad_soyad, sektor, model, language, sure_str, potansiyel, json_result, pdf_data)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (user_id, ad_soyad, sektor, model, language, sure_str, potansiyel,
          json.dumps(json_result, ensure_ascii=False), pdf_data))

    new_id = c.lastrowid

    # Kullanıcı başına son 10'u tut
    c.execute("""
        DELETE FROM analyses WHERE user_id = ? AND id NOT IN (
            SELECT id FROM analyses WHERE user_id = ?
            ORDER BY created_at DESC LIMIT 10
        )
    """, (user_id, user_id))

    conn.commit()
    conn.close()
    return new_id


def get_user_history(user_id: int) -> list[dict]:
    """Kullanıcının son 10 analizini döner (pdf_data hariç)."""
    conn = get_conn()
    c = conn.cursor()
    c.execute("""
        SELECT id, ad_soyad, sektor, model, language, sure_str, potansiyel, json_result, created_at
        FROM analyses WHERE user_id = ?
        ORDER BY created_at DESC LIMIT 10
    """, (user_id,))
    rows = [dict(r) for r in c.fetchall()]
    conn.close()
    return rows


def get_analysis_pdf(analysis_id: int) -> bytes | None:
    """Analize ait PDF bytes döner."""
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT pdf_data FROM analyses WHERE id = ?", (analysis_id,))
    row = c.fetchone()
    conn.close()
    return bytes(row["pdf_data"]) if row and row["pdf_data"] else None


def check_duplicate(user_id: int, ad_soyad: str) -> dict | None:
    """Bu kullanıcı bu kişiyi daha önce analiz etti mi?"""
    conn = get_conn()
    c = conn.cursor()
    c.execute("""
        SELECT id, ad_soyad, potansiyel, created_at FROM analyses
        WHERE user_id = ? AND LOWER(ad_soyad) = LOWER(?)
        ORDER BY created_at DESC LIMIT 1
    """, (user_id, ad_soyad))
    row = c.fetchone()
    conn.close()
    return dict(row) if row else None


def get_all_users() -> list[dict]:
    """Admin: tüm kullanıcılar ve analiz sayıları."""
    conn = get_conn()
    c = conn.cursor()
    c.execute("""
        SELECT u.id, u.username, u.is_admin, u.created_at,
               COUNT(a.id) AS analiz_sayisi
        FROM users u
        LEFT JOIN analyses a ON a.user_id = u.id
        GROUP BY u.id
        ORDER BY u.created_at DESC
    """)
    rows = [dict(r) for r in c.fetchall()]
    conn.close()
    return rows


def get_all_analyses() -> list[dict]:
    """Admin: tüm analizler."""
    conn = get_conn()
    c = conn.cursor()
    c.execute("""
        SELECT a.id, u.username, a.ad_soyad, a.sektor,
               a.model, a.potansiyel, a.sure_str, a.created_at
        FROM analyses a
        JOIN users u ON u.id = a.user_id
        ORDER BY a.created_at DESC
    """)
    rows = [dict(r) for r in c.fetchall()]
    conn.close()
    return rows


def update_user_password(user_id: int, new_hash: str):
    conn = get_conn()
    conn.execute("UPDATE users SET password_hash = ? WHERE id = ?", (new_hash, user_id))
    conn.commit()
    conn.close()


def delete_user(user_id: int):
    conn = get_conn()
    conn.execute("DELETE FROM analyses WHERE user_id = ?", (user_id,))
    conn.execute("DELETE FROM users WHERE id = ?", (user_id,))
    conn.commit()
    conn.close()
