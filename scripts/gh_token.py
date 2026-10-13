"""Obtiene un token de instalación para una GitHub App.

Uso:
    uv run python scripts/gh_token.py
    TOKEN=$(uv run python scripts/gh_token.py)

El script imprime solo el token (`ghs_...`) por stdout; los errores van
por stderr con código de salida distinto de cero.

Lee `.local/gh_app.json` (claves `app-id`, `private-key`,
`installation-id` y `api-url` opcional). `private-key` admite ruta
relativa a `.local/`, ruta absoluta o contenido PEM.

Requiere PyJWT con extra `crypto` (grupo `dev` de `pyproject.toml`).
"""

from __future__ import annotations

import json
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

DEFAULT_API_URL = "https://api.github.com"
CONFIG_FILE = Path(__file__).resolve().parent.parent / ".local" / "gh_app.json"
JWT_LIFETIME = 480  # 8 min: margen bajo el máximo de 10 min de GitHub.


def _config() -> dict:
    """Lee `.local/gh_app.json`."""
    try:
        return json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
    except OSError as exc:
        raise ValueError(f"No se pudo leer {CONFIG_FILE}: {exc.strerror}") from exc
    except json.JSONDecodeError as exc:
        raise ValueError(f"{CONFIG_FILE} no es un JSON válido: {exc}") from exc


def _load_private_key(raw: str) -> str:
    """Acepta la ruta a un `.pem` o el contenido PEM directamente."""
    candidate = Path(raw).expanduser()
    if candidate.is_file():
        return candidate.read_text(encoding="utf-8")
    local_candidate = CONFIG_FILE.parent / raw
    if local_candidate.is_file():
        return local_candidate.read_text(encoding="utf-8")
    if "BEGIN" in raw and "PRIVATE KEY" in raw:
        return raw.replace("\\n", "\n")
    raise ValueError("La clave privada no es un fichero legible ni un PEM válido.")


def _build_jwt(app_id: str, private_key: str) -> str:
    """Construye el JWT de la App (RS256)."""
    import jwt

    now = int(time.time())
    try:
        return jwt.encode(
            {"iss": app_id, "iat": now - 60, "exp": now + JWT_LIFETIME},
            private_key,
            algorithm="RS256",
        )
    except Exception as exc:
        raise ValueError(f"No se pudo firmar el JWT: {exc}") from exc


def _request(
    method: str, url: str, token: str | None = None, payload: dict | None = None
) -> dict:
    """Realiza una petición JSON a la API de GitHub."""
    data = json.dumps(payload).encode() if payload is not None else None
    request = urllib.request.Request(url, data=data, method=method)
    request.add_header("Accept", "application/vnd.github+json")
    request.add_header("X-GitHub-Api-Version", "2022-11-28")
    if token is not None:
        request.add_header("Authorization", f"Bearer {token}")
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            return json.load(response)
    except urllib.error.HTTPError as exc:
        try:
            detail = json.load(exc).get("message", "")
        except (json.JSONDecodeError, UnicodeDecodeError):
            detail = ""
        raise ValueError(f"GitHub devolvió {exc.code}: {detail or exc.reason}") from exc
    except urllib.error.URLError as exc:
        raise ValueError(f"No se pudo contactar con GitHub: {exc.reason}") from exc


def main() -> int:
    """Genera el token y lo imprime por stdout."""
    try:
        cfg = _config()
        for key in ("app-id", "private-key", "installation-id"):
            if not cfg.get(key):
                raise ValueError(f"Falta {key} en {CONFIG_FILE}.")
        api_url = cfg.get("api-url") or DEFAULT_API_URL
        key = _load_private_key(str(cfg["private-key"]))
        jwt_token = _build_jwt(str(cfg["app-id"]), key)
        body = _request(
            "POST",
            f"{api_url}/app/installations/{cfg['installation-id']}/access_tokens",
            jwt_token,
        )
        print(body["token"])
    except (ValueError, KeyError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
