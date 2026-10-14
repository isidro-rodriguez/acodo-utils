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
