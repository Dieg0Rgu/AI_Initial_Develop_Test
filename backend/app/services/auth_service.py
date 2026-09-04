from __future__ import annotations
import os
import sqlite3
import hmac
import hashlib
import base64
import json
import time
from pathlib import Path
from typing import Optional, Dict, Any

try:
    import bcrypt
    HAS_BCRYPT = True
except ImportError:
    HAS_BCRYPT = False

BASE_DIR = Path(__file__).resolve().parent.parent.parent
DB_DIR = BASE_DIR / "backend" / "data"
if not DB_DIR.exists():
    DB_DIR = BASE_DIR / "data"
DB_DIR = BASE_DIR / "data"
os.makedirs(DB_DIR, exist_ok=True)
DB_PATH = DB_DIR / "auth.db"

AUTH_SECRET = os.getenv("AUTH_SECRET_KEY", "gastroteacher-auth-secure-secret-key-2026-xyz-987")
TOKEN_TTL_SECONDS = 86400 * 7  # 7 days


class AuthService:
    def __init__(self, db_path: Optional[Path] = None):
        self.db_path = str(db_path or DB_PATH)
        self._init_db()

    def _get_conn(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self):
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        with self._get_conn() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    email TEXT UNIQUE NOT NULL,
                    username TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    full_name TEXT NOT NULL,
                    role TEXT NOT NULL DEFAULT 'viewer',
                    created_at REAL NOT NULL
                )
            """)
            conn.commit()

            # Seed default admin if empty
            cursor = conn.execute("SELECT COUNT(*) FROM users")
            count = cursor.fetchone()[0]
            if count == 0:
                self._create_user(
                    conn=conn,
                    email="admin@gastroteacher.com",
                    username="admin",
                    password="admin123",
                    full_name="Administrador Gastroteacher",
                    role="admin"
                )

    def _hash_password(self, password: str) -> str:
        if HAS_BCRYPT:
            return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
        salt = os.urandom(16).hex()
        dk = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt.encode("utf-8"), 100000)
        return f"pbkdf2:{salt}:{dk.hex()}"

    def _verify_password(self, password: str, hashed: str) -> bool:
        try:
            if hashed.startswith("$2b$") or hashed.startswith("$2a$"):
                if HAS_BCRYPT:
                    return bcrypt.checkpw(password.encode("utf-8"), hashed.encode("utf-8"))
            elif hashed.startswith("pbkdf2:"):
                _, salt, dk_hex = hashed.split(":")
                dk = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt.encode("utf-8"), 100000)
                return hmac.compare_digest(dk.hex(), dk_hex)
        except Exception:
            return False
        return False

    def _create_user(
        self,
        conn: sqlite3.Connection,
        email: str,
        username: str,
        password: str,
        full_name: str,
        role: str = "viewer"
    ) -> Dict[str, Any]:
        pwd_hash = self._hash_password(password)
        now = time.time()
        cursor = conn.execute(
            """
            INSERT INTO users (email, username, password_hash, full_name, role, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (email.lower().strip(), username.lower().strip(), pwd_hash, full_name.strip(), role, now)
        )
        conn.commit()
        user_id = cursor.lastrowid
        return {
            "id": user_id,
            "email": email.lower().strip(),
            "username": username.lower().strip(),
            "full_name": full_name.strip(),
            "role": role,
            "created_at": now
        }

    def register(
        self,
        email: str,
        username: str,
        password: str,
        full_name: str,
        role: str = "viewer"
    ) -> Dict[str, Any]:
        email_clean = email.lower().strip()
        username_clean = username.lower().strip()

        if len(password) < 6:
            raise ValueError("La contraseña debe tener al menos 6 caracteres.")
        if not email_clean or "@" not in email_clean:
            raise ValueError("El correo electrónico no es válido.")
        if not username_clean or len(username_clean) < 3:
            raise ValueError("El nombre de usuario debe tener al menos 3 caracteres.")

        with self._get_conn() as conn:
            cursor = conn.execute("SELECT id FROM users WHERE email = ?", (email_clean,))
            if cursor.fetchone():
                raise ValueError(f"El correo {email_clean} ya está registrado.")

            cursor = conn.execute("SELECT id FROM users WHERE username = ?", (username_clean,))
            if cursor.fetchone():
                raise ValueError(f"El nombre de usuario {username_clean} ya está en uso.")

            user = self._create_user(conn, email_clean, username_clean, password, full_name, role)
            token = self.create_token(user)
            return {
                "user": user,
                "token": token
            }

    def authenticate(self, username_or_email: str, password: str) -> Optional[Dict[str, Any]]:
        clean_id = username_or_email.lower().strip()
        with self._get_conn() as conn:
            cursor = conn.execute(
                "SELECT * FROM users WHERE email = ? OR username = ?",
                (clean_id, clean_id)
            )
            row = cursor.fetchone()
            if not row:
                return None

            user_dict = dict(row)
            if not self._verify_password(password, user_dict["password_hash"]):
                return None

            user_profile = {
                "id": user_dict["id"],
                "email": user_dict["email"],
                "username": user_dict["username"],
                "full_name": user_dict["full_name"],
                "role": user_dict["role"],
                "created_at": user_dict["created_at"]
            }
            token = self.create_token(user_profile)
            return {
                "user": user_profile,
                "token": token
            }

    def create_token(self, user: Dict[str, Any]) -> str:
        payload = {
            "sub": user["id"],
            "email": user["email"],
            "username": user["username"],
            "role": user.get("role", "viewer"),
            "exp": int(time.time()) + TOKEN_TTL_SECONDS
        }
        payload_bytes = json.dumps(payload, separators=(',', ':')).encode("utf-8")
        payload_b64 = base64.urlsafe_b64encode(payload_bytes).decode("utf-8").rstrip("=")

        sig = hmac.new(AUTH_SECRET.encode("utf-8"), payload_b64.encode("utf-8"), hashlib.sha256).hexdigest()
        return f"{payload_b64}.{sig}"

    def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        if not token or "." not in token:
            return None
        try:
            payload_b64, sig = token.split(".", 1)
            expected_sig = hmac.new(
                AUTH_SECRET.encode("utf-8"),
                payload_b64.encode("utf-8"),
                hashlib.sha256
            ).hexdigest()

            if not hmac.compare_digest(sig, expected_sig):
                return None

            padding = 4 - (len(payload_b64) % 4)
            if padding != 4:
                payload_b64 += "=" * padding

            payload_bytes = base64.urlsafe_b64decode(payload_b64.encode("utf-8"))
            data = json.loads(payload_bytes.decode("utf-8"))

            if data.get("exp", 0) < time.time():
                return None

            return data
        except Exception:
            return None

    def get_user_by_id(self, user_id: int) -> Optional[Dict[str, Any]]:
        with self._get_conn() as conn:
            cursor = conn.execute(
                "SELECT id, email, username, full_name, role, created_at FROM users WHERE id = ?",
                (user_id,)
            )
            row = cursor.fetchone()
            return dict(row) if row else None


auth_service = AuthService()

