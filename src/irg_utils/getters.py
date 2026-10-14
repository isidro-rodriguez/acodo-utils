"""Getters: obtienen valores del entorno del programa.

Las funciones `get_*` producen valores: leen variables de entorno, calculan
hashes o generan credenciales aleatorias seguras. A diferencia de `to_*`
(que transforman) o `valid_*` (que verifican), aquí el valor no existía
antes de llamarlas.
"""

from __future__ import annotations

import os
from typing import TYPE_CHECKING, TypeVar

from .converters import to_int

if TYPE_CHECKING:
    from collections.abc import Callable
    from os import PathLike

T = TypeVar("T")

_BLOCK_SIZE = 1 << 16  # 64 KiB: hashea por bloques sin cargar todo en memoria.


def get_env(
    name: str,
    cast: Callable[[str], T | None] = to_int,  # ty: ignore[invalid-parameter-default]
    default: T | None = None,
) -> T | None:
    """Lee una variable de entorno y la convierte con un conversor `to_*`.

    Args:
        name: Nombre de la variable de entorno.
        cast: Conversor a aplicar sobre el valor leído (por defecto `to_int`).
        default: Valor a devolver si la variable falta o el conversor falla.

    Returns:
        El valor convertido, o `default` si la variable no está definida o su
        valor no es convertible por `cast`.

    Examples:
        >>> import os
        >>> from irg_utils import to_str
        >>> os.environ["IRG_PORT"] = "8080"
        >>> get_env("IRG_PORT")
        8080
        >>> get_env("IRG_PORT", cast=to_str)
        '8080'
        >>> get_env("IRG_AUSENTE", default=7)
        7
        >>> del os.environ["IRG_PORT"]
    """
    raw = os.environ.get(name)
    if raw is None:
        return default
    value = cast(raw)
    return default if value is None else value


def get_hash(
    raw: str | bytes | PathLike[str],
    algorithm: str = "sha256",
) -> str:
    """Calcula el hash hexadecimal de un texto, bytes o fichero.

    Si `raw` es una ruta a un fichero existente, se hashea su contenido por
    bloques (sin cargarlo entero en memoria); en caso contrario se interpreta
    como texto o bytes y se codifica en UTF-8.

    Args:
        raw: Texto, bytes o ruta a un fichero cuyo hash se quiere calcular.
        algorithm: Algoritmo de `hashlib` (por ejemplo `sha256`, `sha1`).

    Returns:
        El hash en formato hexadecimal.

    Raises:
        ValueError: Si el algoritmo no está soportado por `hashlib`.

    Examples:
        >>> get_hash("abc")
        'ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad'
        >>> get_hash(b"abc", "sha1")
        'a9993e364706816aba3e25717850c26c9cd0d89d'
    """
    import hashlib  # Import perezoso.
    from pathlib import Path  # Import perezoso: pesado.

    try:
        digest = hashlib.new(algorithm)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"Algoritmo de hash no soportado: {algorithm!r}.") from exc

    if isinstance(raw, (str, os.PathLike)):
        path = Path(raw).expanduser()
        if path.is_file():
            with path.open("rb") as file:
                for block in iter(lambda: file.read(_BLOCK_SIZE), b""):
                    digest.update(block)
            return digest.hexdigest()
        raw = os.fspath(raw)  # Ruta inexistente: se trata como texto.

    data = raw.encode() if isinstance(raw, str) else raw
    digest.update(data)
    return digest.hexdigest()


def get_hmac(key: str | bytes, message: str | bytes, algorithm: str = "sha256") -> str:
    """Calcula el HMAC hexadecimal de un mensaje con una clave secreta.

    A diferencia de `get_hash`, usa una clave, lo que permite verificar la
    integridad y autenticidad de un mensaje, no solo su huella.

    Args:
        key: Clave secreta (texto o bytes).
        message: Mensaje a autenticar (texto o bytes).
        algorithm: Algoritmo de `hashlib` (por ejemplo `sha256`, `sha1`).

    Returns:
        El HMAC en formato hexadecimal.

    Raises:
        ValueError: Si el algoritmo no está soportado por `hashlib`.

    Examples:
        >>> get_hmac("clave", "mensaje", "sha1")
        '25dff5fc3efc225e6d8a520e32dec1c8f671b86f'
        >>> get_hmac("Jefe", "what do ya want for nothing?")
        '5bdcc146bf60754e6a042426089575c75a003f089d2739839dec58b964ec3843'
    """
    import hashlib
    import hmac

    try:
        hashlib.new(algorithm)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"Algoritmo de hash no soportado: {algorithm!r}.") from exc

    key_bytes = key.encode() if isinstance(key, str) else key
    message_bytes = message.encode() if isinstance(message, str) else message
    return hmac.new(key_bytes, message_bytes, algorithm).hexdigest()


def get_random_password(
    length: tuple[int, int] = (8, 16),
    special_characters: str = "",
    allow_uppercase: bool = True,
    only_digits: bool = False,
) -> str:
    """Genera una contraseña aleatoria que cumple los criterios de `valid_password`.

    Usa `secrets` (CSPRNG), nunca `random`. La longitud se elige al azar
    dentro del rango indicado y cada carácter se toma del mismo conjunto que
    admitiría `valid_password` con esos argumentos.

    Args:
        length: Rango (mínimo, máximo) de longitud, ambos inclusive.
        special_characters: Caracteres especiales permitidos.
        allow_uppercase: Mayúsculas permitidas.
        only_digits: Si solo se generan dígitos.

    Returns:
        La contraseña generada.

    Raises:
        ValueError: Si se han indicado argumentos ambiguos o incoherentes.
    """
    from .validators import _allowed_chars, _check_password_args

    _check_password_args(length, special_characters, only_digits)
    alphabet = sorted(_allowed_chars(special_characters, allow_uppercase, only_digits))

    import secrets  # Import perezoso.

    min_length, max_length = length
    size = secrets.randbelow(max_length - min_length + 1) + min_length
    return "".join(secrets.choice(alphabet) for _ in range(size))


def get_random_token(nbytes: int = 32, url_safe: bool = True) -> str:
    """Genera un token aleatorio criptográficamente seguro con `secrets`.

    Args:
        nbytes: Cantidad de bytes de entropía (por defecto 32).
        url_safe: Si es `True`, usa codificación URL-segura (`token_urlsafe`);
            si es `False`, genera hexadecimal (`token_hex`).

    Returns:
        El token generado.

    Raises:
        ValueError: Si `nbytes` no es un entero positivo.

    Examples:
        >>> token = get_random_token()
        >>> len(token) >= 40
        True
        >>> len(get_random_token(16, url_safe=False))
        32
    """
    import secrets  # Import perezoso.

    if not isinstance(nbytes, int) or isinstance(nbytes, bool) or nbytes < 1:
        raise ValueError("`nbytes` debe ser un entero positivo.")

    if url_safe:
        return secrets.token_urlsafe(nbytes)
    return secrets.token_hex(nbytes)
