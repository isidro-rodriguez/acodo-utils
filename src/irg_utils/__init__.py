"""Módulo de funciones utilitarias.

Requiere Python >= 3.11 (`datetime.UTC`).

Convenio: prefijos `to_*`, `has_*`, `parse_*` y `valid_*`. Dentro de cada
categoría, las funciones públicas van en orden alfabético.

# Tabla de contenidos:
# -----------------------------------------------------------------------------
- Conversores: Transforman tipos de datos.
  - to_bool: Texto/entero -> bool (`"sí"`, `"off"`, `1`...).
  - to_bytes: Texto de tamaño (`"1,5 GiB"`) -> bytes.
  - to_date: String con fecha habitual -> date.
  - to_datetime: String con fecha habitual -> datetime (a medianoche, sin zona).
  - to_decimal: Valor numérico -> Decimal finito.
  - to_float: Valor numérico -> float finito.
  - to_int: Valor numérico -> int (solo si es entero exacto).
  - to_path: Texto/ruta -> Path (expande `~`).
  - to_str: Valor -> str con contenido.
  - to_timedelta: Segundos -> timedelta.
- Comprobaciones: Verifican que los objetos cumplan los requisitos.
  - has_required_attrs: Un objeto tiene todos los atributos requeridos.
  - has_required_fields: Una colección contiene todos los campos requeridos.
  - has_required_keys: Un diccionario contiene todas las llaves requeridas.
- Parsers: Transforman tipos de datos a strings legibles.
  - parse_amount: Número -> string con separadores de miles y decimales.
  - parse_datetime: date/datetime -> string legible.
  - parse_duration: Texto de duración (`"1h 30m"`) -> timedelta (camino inverso).
  - parse_percent: Fracción/número -> porcentaje legible.
  - parse_size: Bytes -> string con unidad ISO/IEC 80000-13.
  - parse_slug: Texto -> slug (`"hola-mundo"`).
  - parse_timedelta: timedelta -> `H:MM:SS` o `M:SS`.
- Validaciones: Verifican que un string tenga el formato requerido.
  - valid_dni: DNI español con letra de control.
  - valid_email: Formato de email.
  - valid_filename: Nombre de fichero válido en los sistemas habituales.
  - valid_hex_color: Color hexadecimal (`#rgb`, `#rrggbb`, con alfa opcional).
  - valid_iban: IBAN con dígitos de control (mod 97).
  - valid_ip: Dirección IPv4/IPv6.
  - valid_json: Texto JSON bien formado.
  - valid_nie: NIE español con letra de control.
  - valid_password: Formato de contraseña.
  - valid_phone: Teléfono en formato internacional básico.
  - valid_slug: Slug en minúsculas separado por guiones.
  - valid_url: Formato de URL http/https.
  - valid_uuid: UUID en forma canónica.
"""

from __future__ import annotations

import math
import re
import string
from datetime import UTC, date, datetime, timedelta
from functools import cache
from os import fspath
from typing import TYPE_CHECKING
from urllib.parse import urlparse

if TYPE_CHECKING:
    from collections.abc import Collection, Hashable, Iterable, Mapping
    from decimal import Decimal
    from fractions import Fraction
    from os import PathLike
    from pathlib import Path
    from typing import Any, NoReturn

__all__ = [
    "has_required_attrs",
    "has_required_fields",
    "has_required_keys",
    "parse_amount",
    "parse_datetime",
    "parse_duration",
    "parse_percent",
    "parse_size",
    "parse_slug",
    "parse_timedelta",
    "to_bool",
    "to_bytes",
    "to_date",
    "to_datetime",
    "to_decimal",
    "to_float",
    "to_int",
    "to_path",
    "to_str",
    "to_timedelta",
    "valid_dni",
    "valid_email",
    "valid_filename",
    "valid_hex_color",
    "valid_iban",
    "valid_ip",
    "valid_json",
    "valid_nie",
    "valid_password",
    "valid_phone",
    "valid_slug",
    "valid_url",
    "valid_uuid",
]

# =============================================================================
# Constantes
# =============================================================================

# Intercambia separadores: 1,234.50 <-> 1.234,50
_SWAP_SEPARATORS = str.maketrans(",.", ".,")

_ENGLISH_CODES = frozenset({"en", "eng"})

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
_SIZE_UNITS = ("KiB", "MiB", "GiB", "TiB", "PiB")

_DURATION_PATTERN = r"(\d+(?:[.,]\d+)?)\s*(d|h|min|m|s)"
_DURATION_UNITS = {"d": 86400, "h": 3600, "min": 60, "m": 60, "s": 1}
_MAX_TIMEDELTA_SECONDS = 1e12
_MAX_TIMESTAMP = 4_133_980_799  # 2100-12-31T23:59:59Z

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

_EMAIL_RE = re.compile(
    r"[a-zA-Z0-9.!#$%&'*+/=?^_`{|}~-]+"
    r"@[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?"
    r"(?:\.[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)+"
)

_LOWER_LETTERS = string.ascii_lowercase + "ñ"
_HEX_DIGITS = frozenset(string.hexdigits)
_DNI_LETTERS = "TRWAGMYFPDXBNJZSQVHLCKE"

_INVALID_FILENAME_CHARS = frozenset('<>:"/\\|?*') | frozenset(map(chr, range(32)))
_WINDOWS_RESERVED_NAMES = frozenset(
    {
        "aux",
        "con",
        "nul",
        "prn",
        *(f"com{n}" for n in range(1, 10)),
        *(f"lpt{n}" for n in range(1, 10)),
    }
)

# =============================================================================
# Conversores
# =============================================================================


def _midnight(dt: datetime) -> datetime:
    # Descarta hora y zona horaria.
    return datetime(dt.year, dt.month, dt.day)


def _normalize_number(text: str) -> str:
    # Unifica separadores: el último que aparezca es el decimal.
    if text.rfind(",") > text.rfind("."):
        return text.replace(".", "").replace(",", ".")
    return text.replace(",", "")


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


# =============================================================================
#  Comprobaciones
# =============================================================================


def has_required_attrs(raw: object, required_attrs: Iterable[str]) -> bool:
    """Comprueba que el objeto tiene todos los atributos requeridos.

    Args:
        raw: Objeto a verificar.
        required_attrs: Nombres de los atributos requeridos.

    Returns:
        `True` si el objeto tiene todos los atributos requeridos.

    Examples:
        >>> has_required_attrs("texto", ["upper", "lower"])
        True
        >>> has_required_attrs("texto", ["append"])
        False
    """
    return all(hasattr(raw, attr) for attr in required_attrs)


def has_required_fields(
    raw: Collection[Any],
    required_fields: Iterable[Any],
) -> bool:
    """Comprueba que la colección tiene todos los campos requeridos.

    Args:
        raw: Colección a verificar.
        required_fields: Campos requeridos.

    Returns:
        `True` si la colección tiene todos los campos requeridos.
    """
    return all(field in raw for field in required_fields)


def has_required_keys(
    raw: Mapping[Hashable, Any],
    required_keys: Iterable[Hashable],
) -> bool:
    """Comprueba que el diccionario tiene todas las llaves requeridas.

    Args:
        raw: Diccionario a verificar.
        required_keys: Llaves requeridas.

    Returns:
        `True` si el diccionario tiene todas las llaves requeridas.
    """
    return all(key in raw for key in required_keys)


# =============================================================================
#  Parsers
# =============================================================================


def _check_lang(lang: str | None) -> str | None:
    # Normaliza el código de lenguaje y lanza ValueError si es inválido.
    if lang is None:
        return None

    lang = lang.lower()
    if not (lang.isalpha() and 2 <= len(lang) <= 3):
        raise ValueError(
            "Código de lenguaje incorrecto. Consultar: "
            "https://www.loc.gov/standards/iso639-2/php/code_list.php"
        )
    return lang


def parse_amount(
    raw: int | float | Fraction,
    lang: str | None = None,
    decimals: int = 2,
) -> str:
    """Parsea un tipo numérico a string numérico de legibilidad cómoda.

    Los enteros (y las fracciones de denominador 1) se muestran sin decimales.
    Con `lang` `en`/`eng` se usa `1,234.50`; en cualquier otro caso
    (incluido `None`), `1.234,50`.

    Args:
        raw: Número a parsear.
        lang: Código del lenguaje al que se va a formatear el número.
        decimals: Cantidad de dígitos decimales a mostrar.

    Returns:
        String numérico de legibilidad cómoda.

    Raises:
        ValueError: Si se ha indicado código de lenguaje inválido.

    Examples:
        >>> parse_amount(1234.5)
        '1.234,50'
        >>> parse_amount(1234.5, "en")
        '1,234.50'
        >>> parse_amount(1234)
        '1.234'
    """
    lang = _check_lang(lang)

    if not isinstance(raw, (int, float)):  # Fraction, sin importarlo
        raw = raw.numerator if raw.denominator == 1 else float(raw)

    text = f"{raw:,}" if isinstance(raw, int) else f"{raw:,.{decimals}f}"

    return text if lang in _ENGLISH_CODES else text.translate(_SWAP_SEPARATORS)


def parse_datetime(raw: date | datetime, lang: str | None = None) -> str:
    """Parsea una fecha o fecha-hora a string legible.

    La hora solo se muestra si no es medianoche, y los segundos solo si no
    son cero. La zona horaria se ignora. Con `lang` `en`/`eng` se usa
    `2024-01-31`; en cualquier otro caso (incluido `None`), `31/01/2024`.

    Args:
        raw: Fecha o fecha-hora a parsear.
        lang: Código del lenguaje al que se va a formatear la fecha.

    Returns:
        String de fecha de legibilidad cómoda.

    Raises:
        ValueError: Si se ha indicado código de lenguaje inválido.

    Examples:
        >>> parse_datetime(datetime(2024, 1, 31))
        '31/01/2024'
        >>> parse_datetime(datetime(2024, 1, 31, 10, 30))
        '31/01/2024 10:30'
        >>> parse_datetime(datetime(2024, 1, 31, 10, 30), "en")
        '2024-01-31 10:30'
    """
    lang = _check_lang(lang)

    text = raw.strftime("%Y-%m-%d" if lang in _ENGLISH_CODES else "%d/%m/%Y")
    if isinstance(raw, datetime) and (raw.hour or raw.minute or raw.second):
        text += raw.strftime(" %H:%M:%S" if raw.second else " %H:%M")
    return text


def parse_duration(raw: str) -> timedelta | None:
    """Parsea un texto de duración (`"1h 30m"`) a timedelta.

    Es el camino inverso a `parse_timedelta`, y la única función de esta
    sección que devuelve un valor en lugar de un texto. Unidades admitidas:
    `d`, `h`, `min`/`m` y `s`; admite decimales (`"1,5h"`).

    Args:
        raw: Texto a parsear.

    Returns:
        La duración, o `None` si el texto no es válido.

    Examples:
        >>> parse_duration("1h 30m")
        datetime.timedelta(seconds=5400)
        >>> parse_duration("2d")
        datetime.timedelta(days=2)
        >>> parse_duration("1h30x") is None
        True
    """
    text = raw.strip().casefold()

    tokens = re.findall(_DURATION_PATTERN, text)
    if not tokens or re.sub(_DURATION_PATTERN, "", text).strip():
        return None

    total = sum(
        float(number.replace(",", ".")) * _DURATION_UNITS[unit]
        for number, unit in tokens
    )
    return to_timedelta(total)


def parse_percent(
    raw: int | float | Fraction,
    lang: str | None = None,
    decimals: int = 1,
) -> str:
    """Parsea un número o fracción (`0.256`, `Fraction(1, 4)`) a porcentaje.

    Se eliminan los ceros decimales sobrantes. Con `lang` `en`/`eng` se usa
    `25.6%`; en cualquier otro caso (incluido `None`), `25,6 %`.

    Args:
        raw: Proporción a parsear (`1` equivale a 100 %).
        lang: Código del lenguaje al que se va a formatear el número.
        decimals: Máximo de dígitos decimales a mostrar.

    Returns:
        String de porcentaje de legibilidad cómoda.

    Raises:
        ValueError: Si se ha indicado código de lenguaje inválido.

    Examples:
        >>> from fractions import Fraction
        >>> parse_percent(0.256)
        '25,6 %'
        >>> parse_percent(Fraction(1, 4))
        '25 %'
        >>> parse_percent(0.5, "en")
        '50%'
        >>> parse_percent(1 / 3, decimals=2)
        '33,33 %'
    """
    lang = _check_lang(lang)

    text = f"{float(raw) * 100:,.{decimals}f}"
    if decimals > 0:
        text = text.rstrip("0").rstrip(".")

    if lang in _ENGLISH_CODES:
        return f"{text}%"
    return f"{text.translate(_SWAP_SEPARATORS)} %"


def parse_size(raw: int) -> str:
    """Parsea el tamaño de fichero a su unidad ISO/IEC 80000-13 correspondiente.

    Args:
        raw: Tamaño de fichero, en bytes, a parsear.

    Returns:
        String de tamaño de fichero con legibilidad cómoda.

    Examples:
        >>> parse_size(1)
        '1 byte'
        >>> parse_size(1536)
        '1,500 KiB'
        >>> parse_size(1048575)
        '1023,999 KiB'
    """
    if raw < 1024:
        return f"{raw} {'byte' if raw == 1 else 'bytes'}"

    value = raw / 1024
    unit = _SIZE_UNITS[0]
    for next_unit in _SIZE_UNITS[1:]:
        # Se compara el valor ya redondeado para no mostrar "1024,000 KiB".
        if round(value, 3) < 1024:
            break
        value /= 1024
        unit = next_unit

    return f"{value:.3f} {unit}".translate(_SWAP_SEPARATORS)


def parse_slug(raw: str) -> str:
    """Parsea un texto a slug: minúsculas, sin acentos y separado por guiones.

    Los caracteres sin equivalente ASCII (`ß`, `€`, emojis...) se descartan.

    Args:
        raw: Texto a parsear.

    Returns:
        El slug; cadena vacía si no queda ningún carácter válido.

    Examples:
        >>> parse_slug("¡Hola, Mundo! Ñandú")
        'hola-mundo-nandu'
    """
    import unicodedata  # Import perezoso.

    text = unicodedata.normalize("NFKD", raw).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")


def parse_timedelta(duration: timedelta) -> str:
    """Formatea un timedelta a una cadena con formato `H:MM:SS` o `M:SS`.

    Args:
        duration: Duración a formatear.

    Returns:
        Texto en formato `H:MM:SS` o `M:SS` (con `-` delante si es negativa).

    Examples:
        >>> parse_timedelta(timedelta(seconds=3725))
        '1:02:05'
        >>> parse_timedelta(timedelta(seconds=65))
        '1:05'
        >>> parse_timedelta(timedelta(seconds=-65))
        '-1:05'
    """
    total = int(duration.total_seconds())
    sign = "-" if total < 0 else ""
    hours, remainder = divmod(abs(total), 3600)
    minutes, secs = divmod(remainder, 60)

    if hours > 0:
        return f"{sign}{hours}:{minutes:02d}:{secs:02d}"
    return f"{sign}{minutes}:{secs:02d}"


# =============================================================================
#  Validaciones
# =============================================================================


def _dni_letter(number: int) -> str:
    # Letra de control de DNI/NIE.
    return _DNI_LETTERS[number % 23]


def valid_dni(raw: str) -> bool:
    """Comprueba si el string es un DNI español válido (8 dígitos y letra).

    Args:
        raw: String a validar.

    Returns:
        `True` si el formato y la letra de control son correctos.

    Examples:
        >>> valid_dni("12345678Z")
        True
        >>> valid_dni("12345678A")
        False
    """
    text = raw.upper()
    if not re.fullmatch(r"[0-9]{8}[A-Z]", text):
        return False
    return text[8] == _dni_letter(int(text[:8]))


def valid_email(raw: str) -> bool:
    """Comprueba si el string presenta un formato de email válido.

    Args:
        raw: String a validar.

    Returns:
        `True` si el string presenta formato de email válido.

    Examples:
        >>> valid_email("a@b.com")
        True
        >>> valid_email("hola")
        False
    """
    return len(raw) <= 254 and _EMAIL_RE.fullmatch(raw) is not None


def valid_filename(raw: str) -> bool:
    r"""Comprueba si el string es un nombre de fichero válido en cualquier SO.

    Rechaza nombres vacíos o de más de 255 caracteres, caracteres
    `<>:"/\|?*` y de control, nombres que terminan en punto o espacio, y los
    nombres reservados de Windows (`CON`, `NUL`, `COM1`...) con cualquier
    extensión.

    Args:
        raw: Nombre de fichero (sin ruta) a validar.

    Returns:
        `True` si el nombre es válido.

    Examples:
        >>> valid_filename("informe.pdf")
        True
        >>> valid_filename("a/b.txt")
        False
        >>> valid_filename("CON.txt")
        False
        >>> valid_filename("archivo.")
        False
    """
    if not raw or len(raw) > 255 or raw[-1] in " .":
        return False
    if not _INVALID_FILENAME_CHARS.isdisjoint(raw):
        return False
    return raw.split(".", 1)[0].rstrip(" ").casefold() not in _WINDOWS_RESERVED_NAMES


def valid_hex_color(raw: str, allow_alpha: bool = True) -> bool:
    """Comprueba si el string es un color hexadecimal (`#rgb`, `#rrggbb`...).

    Args:
        raw: String a validar.
        allow_alpha: Si se admiten las formas con canal alfa
            (`#rgba`, `#rrggbbaa`).

    Returns:
        `True` si el string es un color hexadecimal válido.

    Examples:
        >>> valid_hex_color("#fff")
        True
        >>> valid_hex_color("#ff00cc80")
        True
        >>> valid_hex_color("#ff00cc80", allow_alpha=False)
        False
        >>> valid_hex_color("fff")
        False
    """
    lengths = (4, 5, 7, 9) if allow_alpha else (4, 7)
    return len(raw) in lengths and raw[0] == "#" and set(raw[1:]) <= _HEX_DIGITS


def valid_iban(raw: str) -> bool:
    """Comprueba si el string es un IBAN con dígitos de control correctos.

    Admite espacios y minúsculas. Valida el formato general y el módulo 97,
    pero no la longitud específica de cada país.

    Args:
        raw: String a validar.

    Returns:
        `True` si el IBAN es válido.

    Examples:
        >>> valid_iban("ES91 2100 0418 4502 0005 1332")
        True
        >>> valid_iban("ES91 2100 0418 4502 0005 1333")
        False
    """
    text = raw.replace(" ", "").upper()
    if not re.fullmatch(r"[A-Z]{2}[0-9]{2}[A-Z0-9]{11,30}", text):
        return False

    rearranged = text[4:] + text[:4]
    return int("".join(str(int(char, 36)) for char in rearranged)) % 97 == 1


def valid_ip(raw: str, version: int | None = None) -> bool:
    """Comprueba si el string es una dirección IPv4 o IPv6 válida.

    Args:
        raw: String a validar.
        version: `4` o `6` para exigir esa versión; `None` admite ambas.

    Returns:
        `True` si es una dirección IP válida (de la versión indicada).

    Raises:
        ValueError: Si `version` no es `None`, `4` ni `6`.

    Examples:
        >>> valid_ip("192.168.1.1")
        True
        >>> valid_ip("::1", version=4)
        False
        >>> valid_ip("999.1.1.1")
        False
    """
    from ipaddress import ip_address  # Import perezoso.

    if version not in (None, 4, 6):
        raise ValueError("`version` debe ser None, 4 o 6.")

    try:
        ip = ip_address(raw)
    except ValueError:
        return False
    return version is None or ip.version == version


def _reject_constant(name: str) -> NoReturn:
    # Rechaza NaN, Infinity y -Infinity, que no son JSON estándar.
    raise ValueError(name)


def valid_json(raw: str) -> bool:
    """Comprueba si el string es JSON bien formado (RFC 8259).

    Se rechazan `NaN`, `Infinity` y `-Infinity`.

    Args:
        raw: String a validar.

    Returns:
        `True` si el string es JSON válido.

    Examples:
        >>> valid_json('{"a": [1, 2]}')
        True
        >>> valid_json("{'a': 1}")
        False
        >>> valid_json("NaN")
        False
    """
    from json import loads  # Import perezoso.

    try:
        loads(raw, parse_constant=_reject_constant)
    except (ValueError, RecursionError):  # JSONDecodeError es ValueError
        return False
    return True


def valid_nie(raw: str) -> bool:
    """Comprueba si el string es un NIE español válido (X/Y/Z, 7 dígitos, letra).

    Args:
        raw: String a validar.

    Returns:
        `True` si el formato y la letra de control son correctos.

    Examples:
        >>> valid_nie("X1234567L")
        True
        >>> valid_nie("X1234567A")
        False
    """
    text = raw.upper()
    if not re.fullmatch(r"[XYZ][0-9]{7}[A-Z]", text):
        return False
    number = int(f"{'XYZ'.index(text[0])}{text[1:8]}")
    return text[8] == _dni_letter(number)


@cache
def _allowed_chars(
    special_characters: str,
    allow_uppercase: bool,
    only_digits: bool,
) -> frozenset[str]:
    # Conjunto de caracteres permitidos (cacheado por combinación de argumentos).
    if only_digits:
        return frozenset(string.digits)

    letters = _LOWER_LETTERS + (_LOWER_LETTERS.upper() if allow_uppercase else "")
    return frozenset(string.digits + letters + special_characters)


def valid_password(
    raw: str,
    length: tuple[int, int],
    special_characters: str = "",
    allow_uppercase: bool = True,
    only_digits: bool = False,
) -> bool:
    """Comprueba si el string presenta el formato de contraseña requerido.

    Solo valida longitud y caracteres permitidos; no exige mínimos de cada
    tipo de carácter. Con `only_digits`, `allow_uppercase` carece de efecto.

    Args:
        raw: Contraseña a validar.
        length: Rango (mínimo, máximo) de longitud permitida, ambos inclusive.
        special_characters: Caracteres especiales permitidos.
        allow_uppercase: Mayúsculas permitidas.
        only_digits: Si solo se permiten dígitos.

    Returns:
        `True` si la contraseña cumple las condiciones.

    Raises:
        ValueError: Si se han indicado argumentos ambiguos o incoherentes.
    """
    min_length, max_length = length
    if min_length > max_length:
        raise ValueError("Rango de longitud incoherente: mínimo mayor que máximo.")
    if only_digits and special_characters:
        raise ValueError("Argumentos ambiguos: `only_digits` con `special_characters`.")

    if not min_length <= len(raw) <= max_length:
        return False

    return set(raw) <= _allowed_chars(special_characters, allow_uppercase, only_digits)


def valid_phone(raw: str) -> bool:
    """Comprueba si el string es un teléfono en formato internacional básico.

    Admite un `+` inicial y los separadores espacio, punto, guion y
    paréntesis; exige entre 7 y 15 dígitos (E.164). No valida por país.

    Args:
        raw: String a validar.

    Returns:
        `True` si el formato es válido.

    Examples:
        >>> valid_phone("+34 612 345 678")
        True
        >>> valid_phone("(91) 123-4567")
        True
        >>> valid_phone("12345")
        False
    """
    text = raw.strip()
    if not re.fullmatch(r"\+?[0-9 .()\-]+", text):
        return False
    if text.count("(") != text.count(")"):
        return False
    return 7 <= sum(char.isdigit() for char in text) <= 15


def valid_slug(raw: str) -> bool:
    """Comprueba si el string es un slug: minúsculas, dígitos y guiones simples.

    Args:
        raw: String a validar.

    Returns:
        `True` si el string es un slug válido (el que produce `parse_slug`).

    Examples:
        >>> valid_slug("hola-mundo")
        True
        >>> valid_slug("Hola Mundo")
        False
        >>> valid_slug("hola--mundo")
        False
    """
    return re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", raw) is not None


def valid_url(raw: str) -> bool:
    """Comprueba si el string presenta formato de URL http/https.

    Args:
        raw: String a validar.

    Returns:
        `True` si es una URL http/https con host y sin espacios.

    Examples:
        >>> valid_url("https://example.com/x")
        True
        >>> valid_url("http://[::1")
        False
    """
    if any(map(str.isspace, raw)):
        return False

    try:
        url = urlparse(raw)
        _ = url.port  # Lanza ValueError si el puerto es inválido.
    except ValueError:
        return False

    return url.scheme in ("http", "https") and bool(url.hostname)


def valid_uuid(raw: str) -> bool:
    """Comprueba si el string es un UUID en forma canónica (8-4-4-4-12).

    Args:
        raw: String a validar.

    Returns:
        `True` si el string es un UUID válido.

    Examples:
        >>> valid_uuid("123e4567-e89b-12d3-a456-426614174000")
        True
        >>> valid_uuid("123e4567")
        False
    """
    return (
        re.fullmatch(
            r"[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-"
            r"[0-9a-fA-F]{4}-[0-9a-fA-F]{12}",
            raw,
        )
        is not None
    )
