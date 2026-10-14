r"""Módulo de funciones utilitarias que pueden reutilizarse en cualquier
aplicación — CLI, lógica de negocio, scripts de infraestructura, etc.

Requiere **Python >= 3.11** y no introduce dependencias.


Convenio de nombrado
--------------------
Las funciones se agrupan por categoría: cada categoría empieza por un
prefijo, y dentro de cada una van en orden alfabético.

| Categoría    | Prefijo   | Utilidades |
|--------------|-----------|------------|
| Getters      | `get_*`   | Obtención de un valor, generalmente del entorno o de una credencial/ID aleatoria. |
| Comprobación | `has_*`   | Comprobación de presencia de una clave, campo o estructura. <br>Siempre devuelve un `bool`. |
| Parseo       | `parse_*` | Conversión con reglas. En error devuelve `None`.<br>Excepto `parse_duration`, que devuelve `timedelta \| None`. |
| Conversión   | `to_*`    | Conversión segura de un valor a otro tipo. Nunca lanza por el dato evaluado: si no puede convertirlo, devuelve `None`.<br>Las excepciones son `to_list` (devuelve `[]`) y `to_dict` (devuelve `{}`). |
| Validación   | `valid_*` | Validación de formato o de dominio de un valor. <br>Siempre devuelve un `bool`. |


Uso rápido
----------
```python
from irg_utils import get_hash, has_required_attrs, parse_slug, to_bytes, valid_email

get_hash("abc") # ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad
has_required_attrs("texto", ["upper", "lower"]) # True
parse_slug("¡Hola, Mundo! Ñandú") # hola-mundo-nandu
to_bytes("1,5 GiB") # 1610612736
valid_email("email_sin_punto@ejemplo-com") # False
```
"""  # noqa

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
