"""Validaciones: verifican que un string tenga el formato requerido.

Las funciones `valid_*` devuelven `bool`.
"""

from __future__ import annotations

import re
import string
from functools import cache
from typing import TYPE_CHECKING
from urllib.parse import urlparse

if TYPE_CHECKING:
    from typing import NoReturn


# =============================================================================
#  Constantes
# =============================================================================


_EMAIL_RE = re.compile(
    r"[a-zA-Z0-9.!#$%&'*+/=?^_`{|}~-]+"
    r"@[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?"
    r"(?:\.[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)+"
)

# Etiqueta DNS: 1-63 caracteres, empieza y termina en alfanumérico,
# con guiones solo en el interior.
_LABEL = r"[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?"

_DOMAIN_RE = re.compile(rf"{_LABEL}(?:\.{_LABEL})+")

_TLD_RE = re.compile(r"[a-zA-Z]{2,}")

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
#  Validaciones
# =============================================================================


def _dni_letter(number: int) -> str:
    # Letra de control de DNI/NIE.
    return _DNI_LETTERS[number % 23]


def valid_bool(raw: str) -> bool:
    """Comprueba si el string lo aceptaría `to_bool`.

    Args:
        raw: String a validar.

    Returns:
        `True` si el string representa un booleano reconocible.

    Examples:
        >>> valid_bool("Sí")
        True
        >>> valid_bool("off")
        True
        >>> valid_bool("basura")
        False
    """
    from .converters import to_bool

    return to_bool(raw) is not None


def valid_date(raw: str) -> bool:
    """Comprueba si el string lo aceptaría `to_date`.

    Args:
        raw: String a validar.

    Returns:
        `True` si el string representa una fecha habitual.

    Examples:
        >>> valid_date("31/01/2024")
        True
        >>> valid_date("basura")
        False
    """
    from .converters import to_date

    return to_date(raw) is not None


def valid_datetime(raw: str) -> bool:
    """Comprueba si el string lo aceptaría `to_datetime`.

    Args:
        raw: String a validar.

    Returns:
        `True` si el string representa una fecha habitual.

    Examples:
        >>> valid_datetime("2024-01-31")
        True
        >>> valid_datetime("basura")
        False
    """
    from .converters import to_datetime

    return to_datetime(raw) is not None


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


def valid_domain(raw: str) -> bool:
    """Comprueba si el string es un nombre de dominio (DNS) bien formado.

    Exige al menos dos etiquetas separadas por puntos, cada una de 1-63
    caracteres que empiece y termine en alfanumérico (guiones solo en el
    interior), un TLD final solo de letras de longitud ≥ 2 y una longitud
    total ≤ 253. No se admiten espacios ni puntos finales; no valida IDN.

    Args:
        raw: String a validar.

    Returns:
        `True` si el string es un dominio válido.

    Examples:
        >>> valid_domain("example.com")
        True
        >>> valid_domain("sub.dominio.example.com")
        True
        >>> valid_domain("example")
        False
        >>> valid_domain("example.123")
        False
        >>> valid_domain("-example.com")
        False
    """
    if len(raw) > 253 or _DOMAIN_RE.fullmatch(raw) is None:
        return False
    return _TLD_RE.fullmatch(raw.rsplit(".", 1)[-1]) is not None


def valid_duration(raw: str) -> bool:
    """Comprueba si el string es aceptado por `parse_duration`.

    Args:
        raw: String a validar.

    Returns:
        `True` si el string representa una duración (`"1h 30m"`, `"2d"`...).

    Examples:
        >>> valid_duration("1h 30m")
        True
        >>> valid_duration("abc")
        False
    """
    from .parsers import parse_duration

    return parse_duration(raw) is not None


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


def valid_port(raw: str) -> bool:
    """Comprueba si el string lo aceptaría `to_port`.

    Args:
        raw: String a validar.

    Returns:
        `True` si el string representa un puerto en el rango 1-65535.

    Examples:
        >>> valid_port("8080")
        True
        >>> valid_port("0")
        False
        >>> valid_port("70000")
        False
        >>> valid_port("abc")
        False
    """
    from .converters import to_port

    return to_port(raw) is not None


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
        >>> valid_url("https://[::1")
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
