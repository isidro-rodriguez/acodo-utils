"""Tests estructurales del paquete acodo_utils."""

import ast
import pathlib
from types import ModuleType

import acodo_utils as iu
from acodo_utils import checkers, converters, getters, logger, parsers, validators

MODULES = (converters, checkers, parsers, validators, getters, logger)
PREFIXES = ("to_", "has_", "parse_", "valid_", "get_")


def test_all_is_sorted_and_complete() -> None:
    assert iu.__all__ == sorted(iu.__all__)
    assert all(callable(getattr(iu, name)) for name in iu.__all__)


def _public_functions(module: ModuleType) -> list[str]:
    # `dict.fromkeys` elimina duplicados conservando el orden: las sobrecargas
    # (`@overload`) repiten el nombre de la función.
    tree = ast.parse(pathlib.Path(str(module.__file__)).read_text(encoding="utf-8"))
    return list(
        dict.fromkeys(
            node.name
            for node in tree.body
            if isinstance(node, ast.FunctionDef) and not node.name.startswith("_")
        )
    )


def test_public_functions_match_all() -> None:
    public = [name for module in MODULES for name in _public_functions(module)]
    assert sorted(public) == sorted(iu.__all__)


def test_public_functions_are_alphabetical_per_prefix() -> None:
    for module in MODULES:
        public = _public_functions(module)
        for prefix in PREFIXES:
            names = [name for name in public if name.startswith(prefix)]
            assert names == sorted(names), (module.__name__, prefix)
