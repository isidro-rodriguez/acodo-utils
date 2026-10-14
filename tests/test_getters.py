"""Tests de los getters (`get_*`)."""

import pathlib

import pytest

import irg_utils as iu
from irg_utils import to_bool, to_float


def test_get_env_converts_with_to_int(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("IRG_PORT", "8080")
    assert iu.get_env("IRG_PORT") == 8080


def test_get_env_with_custom_cast(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("IRG_RATIO", "0.5")
    assert iu.get_env("IRG_RATIO", cast=to_float) == 0.5
    monkeypatch.setenv("IRG_FLAG", "1")
    assert iu.get_env("IRG_FLAG", cast=to_bool) is True


def test_get_env_missing_returns_default(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("IRG_AUSENTE", raising=False)
    assert iu.get_env("IRG_AUSENTE", default=7) == 7
    assert iu.get_env("IRG_AUSENTE", cast=to_bool, default=False) is False


def test_get_env_unconvertible_returns_default(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("IRG_PORT", "no-es-numero")
    assert iu.get_env("IRG_PORT", default=-1) == -1
    assert iu.get_env("IRG_PORT", cast=to_bool, default=False) is False


def test_get_hash_text() -> None:
    assert iu.get_hash("abc") == (
        "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad"
    )


def test_get_hash_bytes_and_algorithm() -> None:
    assert iu.get_hash(b"abc", "sha1") == "a9993e364706816aba3e25717850c26c9cd0d89d"
    assert iu.get_hash("abc", "sha256") == iu.get_hash(b"abc")


def test_get_hash_matches_bytes_for_file(tmp_path: pathlib.Path) -> None:
    file = tmp_path / "datos.bin"
    content = b"contenido de prueba " * 5000  # Varios bloques de 64 KiB.
    file.write_bytes(content)
    assert iu.get_hash(file) == iu.get_hash(content)


def test_get_hash_invalid_algorithm() -> None:
    with pytest.raises(ValueError, match="no soportado"):
        iu.get_hash("abc", "algoritmo-inexistente")
