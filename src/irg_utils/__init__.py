"""Funciones utilitarias compartidas entre proyectos.

Módulo con helpers, convertidores, validadores, parseos y getters que
pueden reutilizarse en cualquier aplicación — CLI, lógica de negocio o
scripts de infraestructura. Requiere Python >= 3.11 (`datetime.UTC`) y
no introduce dependencias.

Convenio de nombrado
--------------------
Las funciones se agrupan por categoría: cada categoría empieza por un
prefijo, y dentro de cada una van en orden alfabético.

- `to_*`     Conversión segura de un valor a otro tipo. Nunca lanza por el
             dato evaluado: si no puede convertirlo, devuelve `None`. Las
             excepciones son `to_list` (devuelve `[]`) y `to_dict`
             (devuelve `{}`).
- `has_*`    Comprobación de presencia de una clave, campo o estructura.
             Siempre devuelve un `bool`.
- `valid_*`  Validación de formato o de dominio de un valor.
             Siempre devuelve un `bool`.
- `parse_*`  Conversión a un tipo concreto. En error devuelve `None`,
             excepto `parse_duration`, que devuelve `timedelta | None`.
- `get_*`    Obtención de un valor, generalmente del entorno o de una
             credencial/ID aleatoria. No transforman ni verifican: son
             "productoras".

Uso rápido
----------
```python
from irg_utils import parse_amount, valid_email

amount = parse_amount(365346.32)
print(amount) # 365.346,32

if not valid_email("hola@ejemplo.com"):
    raise ValueError("Email no válido")
```
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
    to_dict,
    to_float,
    to_int,
    to_list,
    to_path,
    to_port,
    to_str,
    to_timedelta,
)
from .getters import (
    get_env,
    get_hash,
    get_hmac,
    get_now,
    get_otp,
    get_password_hash,
    get_random_choice,
    get_random_int,
    get_random_password,
    get_random_token,
    get_uuid,
)
from .parsers import (
    parse_amount,
    parse_bool,
    parse_datetime,
    parse_duration,
    parse_percent,
    parse_size,
    parse_slug,
    parse_timedelta,
)
from .validators import (
    valid_bic,
    valid_bool,
    valid_date,
    valid_datetime,
    valid_dni,
    valid_domain,
    valid_duration,
    valid_email,
    valid_filename,
    valid_hex_color,
    valid_iban,
    valid_ip,
    valid_json,
    valid_mac,
    valid_nie,
    valid_passport,
    valid_password,
    valid_phone,
    valid_port,
    valid_slug,
    valid_url,
    valid_uuid,
)

__all__ = [
    "get_env",
    "get_hash",
    "get_hmac",
    "get_now",
    "get_otp",
    "get_password_hash",
    "get_random_choice",
    "get_random_int",
    "get_random_password",
    "get_random_token",
    "get_uuid",
    "has_required_attrs",
    "has_required_fields",
    "has_required_keys",
    "parse_amount",
    "parse_bool",
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
    "to_dict",
    "to_float",
    "to_int",
    "to_list",
    "to_path",
    "to_port",
    "to_str",
    "to_timedelta",
    "valid_bic",
    "valid_bool",
    "valid_date",
    "valid_datetime",
    "valid_dni",
    "valid_domain",
    "valid_duration",
    "valid_email",
    "valid_filename",
    "valid_hex_color",
    "valid_iban",
    "valid_ip",
    "valid_json",
    "valid_mac",
    "valid_nie",
    "valid_passport",
    "valid_password",
    "valid_phone",
    "valid_port",
    "valid_slug",
    "valid_url",
    "valid_uuid",
]
