"""Tests estructurales del paquete irg_utils."""

import ast
import pathlib

import irg_utils as iu
from irg_utils import checkers, converters, parsers, validation

MODULES = (converters, checkers, parsers, validation)


def test_all_is_sorted_and_complete() -> None:
    assert iu.__all__ == sorted(iu.__all__)
    assert all(callable(getattr(iu, name)) for name in iu.__all__)


def test_public_functions_are_alphabetical_per_prefix() -> None:
    public = [
        node.name
        for module in MODULES
        for node in ast.parse(
            pathlib.Path(str(module.__file__)).read_text(encoding="utf-8")
        ).body
        if isinstance(node, ast.FunctionDef) and not node.name.startswith("_")
    ]
    assert sorted(public) == sorted(iu.__all__)
    for prefix in ("to_", "has_", "parse_", "valid_"):
        names = [name for name in public if name.startswith(prefix)]
        assert names == sorted(names), prefix
