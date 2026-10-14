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

T = TypeVar("T")


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
