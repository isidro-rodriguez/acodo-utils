"""Conversores: transforman valores en otros tipos.

Las funciones `to_*` nunca lanzan excepciones por valores inválidos y
casi todas devuelven `None` en ese caso. Las excepciones son `to_list` y
`to_dict`, que devuelven `[]` y `{}` respectivamente.
"""

from __future__ import annotations

import math
import re
from collections.abc import Iterable, Mapping
from datetime import UTC, date, datetime, timedelta
from os import fspath
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from decimal import Decimal
    from os import PathLike
    from pathlib import Path
    from typing import Any


# =============================================================================
#  Constantes
# =============================================================================

_TRUE_STRINGS = frozenset({"1", "on", "si", "sí", "t", "true", "verdadero", "y", "yes"})

_FALSE_STRINGS = frozenset({"0", "f", "false", "falso", "n", "no", "off"})

_BYTE_UNITS = {
    "": 1,
    "b": 1,
    "byte": 1,
    "bytes": 1,
    "kib": 1024,
    "mib": 1024**2,
    "gib": 1024**3,
    "tib": 1024**4,
    "pib": 1024**5,
    "kb": 1000,
    "mb": 1000**2,
    "gb": 1000**3,
    "tb": 1000**4,
    "pb": 1000**5,
}

_MAX_TIMESTAMP = 4_133_980_799  # 2100-12-31T23:59:59Z

_MAX_TIMEDELTA_SECONDS = 1e12

# Los nombres de mes/día (%a %b %B) dependen del locale activo.
_NAMED_MONTH_FORMATS = (
    "%a %b %d %H:%M:%S %Y",
    "%b %d %H:%M:%S %Y",
    "%b %d %Y",
    "%d %b %Y",
    "%d %B %Y",
    "%B %d %Y",
)

# Formatos numéricos no ISO. Se asume día primero (convención europea);
# se evitan deliberadamente los formatos mes-primero.
_NUMERIC_FORMATS = (
    "%Y/%m/%d",
    "%Y.%m.%d",
    "%d-%m-%Y",
    "%d/%m/%Y",
    "%d.%m.%Y",
)


# =============================================================================
#  Conversores
# =============================================================================


def to_bool(raw: str | int | None) -> bool | None:
    """Convierte textos habituales (`"sí"`, `"off"`, `"1"`...) a bool.

    Args:
        raw: Valor a convertir. Los enteros solo pueden ser 0 o 1.

    Returns:
        El booleano, o `None` si el valor no es reconocible.

    Examples:
        >>> to_bool("Sí")
        True
        >>> to_bool(" OFF ")
        False
        >>> to_bool("quizá") is None
        True
        >>> to_bool(2) is None
        True
    """
    if isinstance(raw, bool):
        return raw
    if isinstance(raw, int):
        return bool(raw) if raw in (0, 1) else None
    if isinstance(raw, str):
        text = raw.strip().casefold()
        if text in _TRUE_STRINGS:
            return True
        if text in _FALSE_STRINGS:
            return False
    return None


def to_bytes(raw: str | None) -> int | None:
    """Convierte un texto de tamaño (`"1,5 GiB"`) a bytes.

    Unidades binarias (KiB, MiB...) en base 1024 y decimales (kB, MB...) en
    base 1000. Admite coma o punto decimal. Sin unidad se asumen bytes. Es el
    camino inverso, aproximado, de `parse_size`.

    Args:
        raw: Texto a convertir.

    Returns:
        Cantidad de bytes, o `None` si el texto no es válido.

    Examples:
        >>> to_bytes("1,5 GiB")
        1610612736
        >>> to_bytes("2 kB")
        2000
        >>> to_bytes("512")
        512
        >>> to_bytes("1 furlong") is None
        True
    """

    def _normalize_number(text: str) -> str:
        # Unifica separadores: el último que aparezca es el decimal.
        if text.rfind(",") > text.rfind("."):
            return text.replace(".", "").replace(",", ".")
        return text.replace(",", "")

    if raw is None:
        return None

    match = re.fullmatch(r"(\d[\d.,]*)\s*([a-z]*)", raw.strip().casefold())
    if match is None:
        return None

    factor = _BYTE_UNITS.get(match[2])
    if factor is None:
        return None

    try:
        return round(float(_normalize_number(match[1])) * factor)
    except (ValueError, OverflowError):
        return None


def to_date(raw: str) -> date | None:
    """Convierte un string con fechas habituales a date.

    Acepta los mismos formatos que `to_datetime`.

    Args:
        raw: String a ser parseado como fecha.

    Returns:
        La fecha, o `None` si la conversión falla.

    Examples:
        >>> to_date("31/01/2024")
        datetime.date(2024, 1, 31)
    """
    dt = to_datetime(raw)
    return None if dt is None else dt.date()


def to_datetime(raw: str) -> datetime | None:
    """Convierte un string con fechas habituales a datetime.

    Solo se conserva la fecha: el resultado es siempre medianoche y sin zona
    horaria. En los formatos con día y mes numéricos se asume día primero.

    Args:
        raw: String a ser parseado como fecha.

    Returns:
        El datetime a medianoche, o `None` si la conversión falla.

    Examples:
        >>> to_datetime("2024-01-31")
        datetime.datetime(2024, 1, 31, 0, 0)
        >>> to_datetime("31/01/2024")
        datetime.datetime(2024, 1, 31, 0, 0)
        >>> to_datetime("1700000000")
        datetime.datetime(2023, 11, 14, 0, 0)
        >>> to_datetime("basura") is None
        True
    """

    def _midnight(dt: datetime) -> datetime:
        # Descarta hora y zona horaria.
        return datetime(dt.year, dt.month, dt.day)

    raw = raw.strip()

    # ISO 8601 (C puro, el camino más rápido). `fromisoformat` acepta "Z".
    if raw[-1:] == "z":
        raw = raw[:-1] + "Z"
    try:
        return _midnight(datetime.fromisoformat(raw))
    except ValueError:
        pass

    # Unix timestamp en segundos (barato: se descarta antes que `strptime`).
    if raw.isascii() and raw.isdigit() and 9 <= len(raw) <= 11:
        timestamp = int(raw)
        if timestamp <= _MAX_TIMESTAMP:
            return _midnight(datetime.fromtimestamp(timestamp, tz=UTC))

    # Formatos con nombres de mes y formatos numéricos no ISO.
    for fmt in _NAMED_MONTH_FORMATS + _NUMERIC_FORMATS:
        try:
            return _midnight(datetime.strptime(raw, fmt))
        except ValueError:
            pass

    # RFC 2822 / RFC 5322. Import perezoso: `email.utils` es pesado.
    from email.utils import parsedate_to_datetime

    try:
        return _midnight(parsedate_to_datetime(raw))
    except (TypeError, ValueError, OverflowError):
        return None


def to_decimal(raw: str | float | None) -> Decimal | None:
    """Convierte strings numéricos a Decimal (apto para importes).

    Los `float` se convierten a través de su representación en texto
    (`0.1` -> `Decimal("0.1")`). Se rechazan `bool`, `nan`, `inf` y los
    guiones bajos (`"1_000"`).

    Args:
        raw: Valor a convertir (texto numérico, entero o flotante).

    Returns:
        El número convertido, o `None` si la conversión falla.

    Examples:
        >>> to_decimal("0.10")
        Decimal('0.10')
        >>> to_decimal(0.1)
        Decimal('0.1')
        >>> to_decimal("nan") is None
        True
    """
    from decimal import Decimal, InvalidOperation  # Import perezoso: pesado.

    if raw is None or isinstance(raw, bool):
        return None
    if isinstance(raw, str) and "_" in raw:
        return None

    try:
        value = Decimal(str(raw))
    except (InvalidOperation, ValueError):
        return None
    return value if value.is_finite() else None


def to_dict(raw: object) -> dict[Any, Any]:
    """Convierte un valor a dict, convirtiendo también los anidados.

    `None` produce `{}`. Se aceptan mappings, dataclasses y pares
    `("k", v)`; los valores anidados que sean mappings o dataclasses se
    convierten recursivamente. Cualquier otro valor produce `{}`.

    Args:
        raw: Valor a convertir.

    Returns:
        El dict resultante; `{}` si el valor no es convertible.

    Examples:
        >>> to_dict({"a": 1})
        {'a': 1}
        >>> to_dict([("a", 1), ("b", 2)])
        {'a': 1, 'b': 2}
        >>> to_dict(None)
        {}
    """
    from dataclasses import asdict, is_dataclass

    def _convert(value: object) -> object:
        if is_dataclass(value) and not isinstance(value, type):
            return asdict(value)
        if isinstance(value, Mapping):
            return {key: _convert(item) for key, item in value.items()}
        return value

    if raw is None:
        return {}
    if is_dataclass(raw) and not isinstance(raw, type):
        return asdict(raw)
    if isinstance(raw, Mapping):
        return {key: _convert(value) for key, value in raw.items()}
    if isinstance(raw, Iterable):
        try:
            return {key: _convert(value) for key, value in raw}
        except (TypeError, ValueError):
            return {}
    return {}


def to_float(raw: str | float | None) -> float | None:
    """Convierte strings numéricos a float.

    Se rechazan `bool`, `nan`, `inf` y los guiones bajos (`"1_000"`).

    Args:
        raw: Valor a convertir (texto numérico o flotante).

    Returns:
        El número convertido, o `None` si la conversión falla.

    Examples:
        >>> to_float("1.5")
        1.5
        >>> to_float("nan") is None
        True
    """
    if raw is None or isinstance(raw, bool):
        return None
    if isinstance(raw, str) and "_" in raw:
        return None

    try:
        value = float(raw)
    except (ValueError, TypeError, OverflowError):
        return None
    return value if math.isfinite(value) else None


def to_int(raw: str | float | int | None) -> int | None:
    """Convierte strings numéricos a int.

    Un `float` solo se convierte si es entero exacto (`3.0` sí, `3.7` no).
    Se rechazan `bool` y los guiones bajos (`"1_000"`).

    Args:
        raw: Valor a convertir (texto numérico o entero).

    Returns:
        El número convertido, o `None` si la conversión falla.

    Examples:
        >>> to_int("42")
        42
        >>> to_int(3.7) is None
        True
        >>> to_int(float("inf")) is None
        True
    """
    if raw is None or isinstance(raw, bool):
        return None
    if isinstance(raw, float):
        return int(raw) if raw.is_integer() else None  # nan/inf -> None
    if isinstance(raw, str) and "_" in raw:
        return None

    try:
        return int(raw)
    except (ValueError, TypeError):
        return None


def to_list(raw: object) -> list[Any]:
    """Convierte un valor a lista, aplanando las anidadas.

    `None` produce `[]`; un escalar (o un `str`/`bytes`) produce una lista
    de un elemento; un iterable se aplanan recursivamente.

    Args:
        raw: Valor a convertir.

    Returns:
        La lista aplanada.

    Examples:
        >>> to_list([1, [2, 3]])
        [1, 2, 3]
        >>> to_list("abc")
        ['abc']
        >>> to_list(None)
        []
    """
    if raw is None:
        return []
    if isinstance(raw, (str, bytes)) or not isinstance(raw, Iterable):
        return [raw]
    return [item for value in raw for item in to_list(value)]


def to_path(raw: str | PathLike[str] | None) -> Path | None:
    """Convierte un texto o ruta a Path, expandiendo `~`.

    Args:
        raw: Texto o ruta a convertir.

    Returns:
        La ruta, o `None` si el valor falta, está en blanco o no es válido.

    Examples:
        >>> to_path("carpeta/fichero.txt").name
        'fichero.txt'
        >>> to_path("   ") is None
        True
    """
    from pathlib import Path  # Import perezoso: pesado.

    if raw is None:
        return None

    try:
        text = fspath(raw)
    except TypeError:
        return None

    if not isinstance(text, str) or not text.strip() or "\0" in text:
        return None

    try:
        return Path(text).expanduser()
    except (RuntimeError, ValueError):
        return None


def to_port(raw: str | int | None) -> int | None:
    """Convierte un texto o entero a número de puerto TCP/UDP (1-65535).

    Args:
        raw: Valor a convertir (texto numérico o entero).

    Returns:
        El puerto, o `None` si el valor falta o está fuera del rango 1-65535.

    Examples:
        >>> to_port("8080")
        8080
        >>> to_port(80)
        80
        >>> to_port("0") is None
        True
        >>> to_port(70000) is None
        True
    """
    value = to_int(raw)
    return value if value is not None and 1 <= value <= 65535 else None


def to_str(raw: object) -> str | None:
    """Devuelve el valor si es un texto con contenido.

    Args:
        raw: Valor a comprobar.

    Returns:
        El propio `raw` si es un `str` que no está vacío ni es solo espacios;
        `None` en otro caso.
    """
    return raw if isinstance(raw, str) and raw.strip() else None


def to_timedelta(raw: float | None) -> timedelta | None:
    """Convierte una cantidad numérica de segundos a timedelta.

    Args:
        raw: Cantidad de segundos a convertir.

    Returns:
        La duración, o `None` si el valor falta, no es finito o es desmesurado.

    Examples:
        >>> to_timedelta(90)
        datetime.timedelta(seconds=90)
    """
    if raw is None or not math.isfinite(raw) or abs(raw) > _MAX_TIMEDELTA_SECONDS:
        return None
    return timedelta(seconds=raw)
