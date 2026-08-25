from __future__ import annotations

import hashlib
import json
from pathlib import Path

AUTH_PATH = Path(__file__).resolve().parent.parent / "users.json"


def _read_users() -> dict[str, str]:
    if not AUTH_PATH.exists():
        return {}
    try:
        return json.loads(AUTH_PATH.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}


def _write_users(users: dict[str, str]) -> None:
    AUTH_PATH.write_text(json.dumps(users, indent=2), encoding="utf-8")


def _hash_password(password: str) -> str:
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def signup(username: str, password: str) -> tuple[bool, str]:
    users = _read_users()
    if username in users:
        return False, "Username already exists."
    users[username] = _hash_password(password)
    _write_users(users)
    return True, "Signup successful."


def login(username: str, password: str) -> tuple[bool, str]:
    users = _read_users()
    if username not in users:
        return False, "User not found."
    if users[username] != _hash_password(password):
        return False, "Invalid password."
    return True, "Login successful."
