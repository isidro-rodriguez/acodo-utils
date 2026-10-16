"""Tests estructurales del paquete acodo_utils."""

import ast
import pathlib

import acodo_utils as iu
from acodo_utils import checkers, converters, getters, logger, parsers, validators

MODULES = (converters, checkers, parsers, validators, getters, logger)


def test_all_is_sorted_and_complete() -> None:
    assert iu.__all__ == sorted(iu.__all__)
    assert all(callable(getattr(iu, name)) for name in iu.__all__)


def test_public_functions_are_alphabetical_per_prefix() -> None:
    # `dict.fromkeys` elimina duplicados conservando el orden: las sobrecargas
    # (`@overload`) repiten el nombre de la función.
    public = list(
        dict.fromkeys(
            node.name
            for module in MODULES
            for node in ast.parse(
                pathlib.Path(str(module.__file__)).read_text(encoding="utf-8")
            ).body
            if isinstance(node, ast.FunctionDef) and not node.name.startswith("_")
        )
    )
    assert sorted(public) == sorted(iu.__all__)
