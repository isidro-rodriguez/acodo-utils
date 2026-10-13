"""Módulo de funciones utilitarias.

Requiere Python >= 3.11 (`datetime.UTC`).

Convenio: prefijos `to_*`, `has_*`, `parse_*` y `valid_*`. Dentro de cada
categoría, las funciones públicas van en orden alfabético.
"""

from .checkers import (
    has_required_attrs,
    has_required_fields,
    has_required_keys,
)
from .converters import (
    to_bool,
    to_bytes,
    to_date,
    to_datetime,
    to_decimal,
    to_float,
    to_int,
    to_path,
    to_str,
    to_timedelta,
)
from .parsers import (
    parse_amount,
    parse_datetime,
    parse_duration,
    parse_percent,
    parse_size,
    parse_slug,
    parse_timedelta,
)
from .validation import (
    valid_date,
    valid_dni,
    valid_email,
    valid_filename,
    valid_hex_color,
    valid_iban,
    valid_ip,
    valid_json,
    valid_nie,
    valid_password,
    valid_phone,
    valid_slug,
    valid_url,
    valid_uuid,
)

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
    "valid_date",
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
