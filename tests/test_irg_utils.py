"""Tests de irg_utils."""

import ast
import pathlib
from datetime import date, datetime, timedelta
from decimal import Decimal
from fractions import Fraction

import pytest

import irg_utils as iu

# =============================================================================
# Estructura del módulo
# =============================================================================


def test_all_is_sorted_and_complete() -> None:
    assert iu.__all__ == sorted(iu.__all__)
    assert all(callable(getattr(iu, name)) for name in iu.__all__)


def test_public_functions_are_alphabetical_per_prefix() -> None:
    tree = ast.parse(pathlib.Path(iu.__file__).read_text(encoding="utf-8"))
    public = [
        node.name
        for node in tree.body
        if isinstance(node, ast.FunctionDef) and not node.name.startswith("_")
    ]
    assert sorted(public) == sorted(iu.__all__)
    for prefix in ("to_", "has_", "parse_", "valid_"):
        names = [name for name in public if name.startswith(prefix)]
        assert names == sorted(names), prefix


# =============================================================================
# Conversores
# =============================================================================


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        (True, True),
        (False, False),
        (1, True),
        (0, False),
        (2, None),
        (-1, None),
        ("Sí", True),
        ("1", True),
        (" OFF ", False),
        ("no", False),
        ("quizá", None),
        ("", None),
        (None, None),
    ],
)
def test_to_bool(raw: object, expected: bool | None) -> None:
    assert iu.to_bool(raw) is expected  # type: ignore[arg-type]


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("1,5 GiB", 1610612736),
        ("1.5 MiB", 1572864),
        ("2 kB", 2000),
        ("2 KB", 2000),
        ("512", 512),
        ("512 bytes", 512),
        ("1.234,5 KB", 1234500),
        ("1,234.5 kB", 1234500),
        (" 1 PiB ", 1024**5),
        ("1 furlong", None),
        ("abc", None),
        ("", None),
        ("-1 KiB", None),
        ("1.2.3 KiB", None),
        ("9" * 400, None),
        (None, None),
    ],
)
def test_to_bytes(raw: str | None, expected: int | None) -> None:
    assert iu.to_bytes(raw) == expected


def test_to_date() -> None:
    assert iu.to_date("31/01/2024") == date(2024, 1, 31)
    assert iu.to_date("basura") is None


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        # ISO 8601
        ("2024-01-31", datetime(2024, 1, 31)),
        ("2024-01-31T10:30:00", datetime(2024, 1, 31)),
        ("2024-01-31T10:30:00Z", datetime(2024, 1, 31)),
        ("2024-01-31T10:30:00z", datetime(2024, 1, 31)),
        ("2024-01-31T10:30:00+02:00", datetime(2024, 1, 31)),
        (" 2024-01-31 ", datetime(2024, 1, 31)),
        # Unix timestamp
        ("1700000000", datetime(2023, 11, 14)),
        ("100000000", datetime(1973, 3, 3)),
        ("99999999999", None),
        # Nombres de mes
        ("Wed Jan 31 10:30:00 2024", datetime(2024, 1, 31)),
        ("Jan 31 10:30:00 2024", datetime(2024, 1, 31)),
        ("Jan 31 2024", datetime(2024, 1, 31)),
        ("31 Jan 2024", datetime(2024, 1, 31)),
        ("31 January 2024", datetime(2024, 1, 31)),
        ("January 31 2024", datetime(2024, 1, 31)),
        # Numéricos no ISO (día primero)
        ("2024/01/31", datetime(2024, 1, 31)),
        ("2024.01.31", datetime(2024, 1, 31)),
        ("31-01-2024", datetime(2024, 1, 31)),
        ("31/01/2024", datetime(2024, 1, 31)),
        ("31.01.2024", datetime(2024, 1, 31)),
        # RFC 2822
        ("Wed, 31 Jan 2024 10:30:00 +0000", datetime(2024, 1, 31)),
        # Inválidos
        ("basura", None),
        ("", None),
        ("32/01/2024", None),
    ],
)
def test_to_datetime(raw: str, expected: datetime | None) -> None:
    assert iu.to_datetime(raw) == expected


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("0.10", Decimal("0.10")),
        (0.1, Decimal("0.1")),
        (1, Decimal(1)),
        (" 1.5 ", Decimal("1.5")),
        ("nan", None),
        ("inf", None),
        (float("nan"), None),
        ("1_0", None),
        ("", None),
        ("abc", None),
        (True, None),
        (None, None),
    ],
)
def test_to_decimal(raw: object, expected: Decimal | None) -> None:
    assert iu.to_decimal(raw) == expected  # type: ignore[arg-type]


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("1.5", 1.5),
        (" 2 ", 2.0),
        (2, 2.0),
        ("nan", None),
        ("inf", None),
        ("1_000", None),
        ("abc", None),
        (10**400, None),
        ([], None),
        (True, None),
        (None, None),
    ],
)
def test_to_float(raw: object, expected: float | None) -> None:
    assert iu.to_float(raw) == expected  # type: ignore[arg-type]


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("42", 42),
        (42, 42),
        (3.0, 3),
        (3.7, None),
        (float("inf"), None),
        (float("nan"), None),
        ("1_000", None),
        ("3.0", None),
        ("abc", None),
        ([], None),
        (True, None),
        (None, None),
    ],
)
def test_to_int(raw: object, expected: int | None) -> None:
    assert iu.to_int(raw) == expected  # type: ignore[arg-type]


class TestToPath:
    def test_valid(self) -> None:
        expected = pathlib.Path("carpeta/fichero.txt")
        assert iu.to_path("carpeta/fichero.txt") == expected
        assert iu.to_path(expected) == expected

    def test_expands_user(self) -> None:
        assert iu.to_path("~") == pathlib.Path.home()

    @pytest.mark.parametrize("raw", [None, "", "   ", "a\0b", 123, b"abc"])
    def test_invalid(self, raw: object) -> None:
        assert iu.to_path(raw) is None  # type: ignore[arg-type]

    def test_expanduser_failure(self, monkeypatch: pytest.MonkeyPatch) -> None:
        def boom(self: pathlib.Path) -> pathlib.Path:
            raise RuntimeError("sin home")

        monkeypatch.setattr(pathlib.Path, "expanduser", boom)
        assert iu.to_path("~") is None


@pytest.mark.parametrize(
    ("raw", "expected"),
    [("a", "a"), (" a ", " a "), ("", None), ("   ", None), (1, None), (None, None)],
)
def test_to_str(raw: object, expected: str | None) -> None:
    assert iu.to_str(raw) == expected


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        (90, timedelta(seconds=90)),
        (-5, timedelta(seconds=-5)),
        (1.5, timedelta(seconds=1.5)),
        (None, None),
        (float("nan"), None),
        (float("inf"), None),
        (1e13, None),
        (-1e13, None),
    ],
)
def test_to_timedelta(raw: float | None, expected: timedelta | None) -> None:
    assert iu.to_timedelta(raw) == expected


# =============================================================================
# Comprobaciones
# =============================================================================


def test_has_required_attrs() -> None:
    assert iu.has_required_attrs("texto", ["upper", "lower"])
    assert iu.has_required_attrs("texto", [])
    assert not iu.has_required_attrs("texto", ["upper", "append"])


def test_has_required_fields() -> None:
    assert iu.has_required_fields([1, 2, 3], [1, 3])
    assert iu.has_required_fields([1], [])
    assert not iu.has_required_fields([1, 2], [1, 5])


def test_has_required_keys() -> None:
    assert iu.has_required_keys({"a": 1, "b": 2}, ["a", "b"])
    assert iu.has_required_keys({}, [])
    assert not iu.has_required_keys({"a": 1}, ["a", "b"])


# =============================================================================
# Parsers
# =============================================================================


@pytest.mark.parametrize(
    ("raw", "lang", "decimals", "expected"),
    [
        (1234.5, None, 2, "1.234,50"),
        (1234.5, "en", 2, "1,234.50"),
        (1234.5, "ENG", 2, "1,234.50"),
        (1234.5678, "es", 3, "1.234,568"),
        (1234, None, 2, "1.234"),
        (1234, "en", 2, "1,234"),
        (Fraction(3), None, 2, "3"),
        (Fraction(1, 4), "en", 2, "0.25"),
    ],
)
def test_parse_amount(
    raw: float | Fraction, lang: str | None, decimals: int, expected: str
) -> None:
    assert iu.parse_amount(raw, lang, decimals) == expected


@pytest.mark.parametrize("lang", ["e", "english", "e1", ""])
def test_invalid_lang(lang: str) -> None:
    with pytest.raises(ValueError, match="lenguaje"):
        iu.parse_amount(1, lang)
    with pytest.raises(ValueError, match="lenguaje"):
        iu.parse_datetime(date(2024, 1, 31), lang)
    with pytest.raises(ValueError, match="lenguaje"):
        iu.parse_percent(1, lang)


@pytest.mark.parametrize(
    ("raw", "lang", "expected"),
    [
        (date(2024, 1, 31), None, "31/01/2024"),
        (datetime(2024, 1, 31), None, "31/01/2024"),
        (datetime(2024, 1, 31, 10, 30), None, "31/01/2024 10:30"),
        (datetime(2024, 1, 31, 10, 30, 5), None, "31/01/2024 10:30:05"),
        (datetime(2024, 1, 31, 0, 0, 5), None, "31/01/2024 00:00:05"),
        (datetime(2024, 1, 31, 10, 30), "en", "2024-01-31 10:30"),
        (date(2024, 1, 31), "eng", "2024-01-31"),
    ],
)
def test_parse_datetime(raw: date, lang: str | None, expected: str) -> None:
    assert iu.parse_datetime(raw, lang) == expected


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("1h 30m", timedelta(hours=1, minutes=30)),
        ("1 min 30 s", timedelta(seconds=90)),
        ("2d", timedelta(days=2)),
        ("45s", timedelta(seconds=45)),
        ("1,5h", timedelta(minutes=90)),
        (" 1H ", timedelta(hours=1)),
        ("1h30x", None),
        ("1m30", None),
        ("5", None),
        ("", None),
        ("99999999999999d", None),
    ],
)
def test_parse_duration(raw: str, expected: timedelta | None) -> None:
    assert iu.parse_duration(raw) == expected


@pytest.mark.parametrize(
    ("raw", "lang", "decimals", "expected"),
    [
        (0.256, None, 1, "25,6 %"),
        (Fraction(1, 4), None, 1, "25 %"),
        (0.5, "en", 1, "50%"),
        (1 / 3, None, 2, "33,33 %"),
        (1, None, 0, "100 %"),
        (0, "en", 1, "0%"),
        (12.345, None, 1, "1.234,5 %"),
    ],
)
def test_parse_percent(
    raw: float | Fraction, lang: str | None, decimals: int, expected: str
) -> None:
    assert iu.parse_percent(raw, lang, decimals) == expected


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        (0, "0 bytes"),
        (1, "1 byte"),
        (1023, "1023 bytes"),
        (1024, "1,000 KiB"),
        (1536, "1,500 KiB"),
        (1048575, "1023,999 KiB"),
        (1048576, "1,000 MiB"),
        (1024**3, "1,000 GiB"),
        (1024**4, "1,000 TiB"),
        (1024**5, "1,000 PiB"),
        (1024**6, "1024,000 PiB"),
    ],
)
def test_parse_size(raw: int, expected: str) -> None:
    assert iu.parse_size(raw) == expected


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("¡Hola, Mundo! Ñandú", "hola-mundo-nandu"),
        ("  --Foo__Bar--  ", "foo-bar"),
        ("Straße 5", "strae-5"),
        ("€€€", ""),
        ("", ""),
    ],
)
def test_parse_slug(raw: str, expected: str) -> None:
    assert iu.parse_slug(raw) == expected


@pytest.mark.parametrize(
    ("seconds", "expected"),
    [
        (0, "0:00"),
        (65, "1:05"),
        (3725, "1:02:05"),
        (90061, "25:01:01"),
        (-65, "-1:05"),
        (-3725, "-1:02:05"),
    ],
)
def test_parse_timedelta(seconds: int, expected: str) -> None:
    assert iu.parse_timedelta(timedelta(seconds=seconds)) == expected


# =============================================================================
# Validaciones
# =============================================================================


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("12345678Z", True),
        ("12345678z", True),
        ("00000000T", True),
        ("12345678A", False),
        ("1234567Z", False),
        ("ABCDEFGHZ", False),
        ("", False),
    ],
)
def test_valid_dni(raw: str, expected: bool) -> None:
    assert iu.valid_dni(raw) is expected


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("a@b.com", True),
        ("user.name+tag@example.co.uk", True),
        ("hola", False),
        ("a@b", False),
        ("@b.com", False),
        ("a b@c.com", False),
        ("a@b.com basura", False),
        ("a@b.com\n", False),
        ("x" * 250 + "@b.com", False),
        ("", False),
    ],
)
def test_valid_email(raw: str, expected: bool) -> None:
    assert iu.valid_email(raw) is expected


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("informe.pdf", True),
        ("a b.txt", True),
        (".gitignore", True),
        ("console.txt", True),
        ("a" * 255, True),
        ("", False),
        ("a" * 256, False),
        ("a/b", False),
        ("a\\b", False),
        ("a:b", False),
        ("a\x00b", False),
        ("a\tb", False),
        ("archivo.", False),
        ("archivo ", False),
        ("..", False),
        ("CON", False),
        ("con.txt", False),
        ("COM1.tar.gz", False),
        ("lpt9", False),
        ("con .txt", False),
    ],
)
def test_valid_filename(raw: str, expected: bool) -> None:
    assert iu.valid_filename(raw) is expected


@pytest.mark.parametrize(
    ("raw", "allow_alpha", "expected"),
    [
        ("#fff", True, True),
        ("#FFFF", True, True),
        ("#ff00cc", True, True),
        ("#ff00cc80", True, True),
        ("#fff", False, True),
        ("#ff00cc", False, True),
        ("#ffff", False, False),
        ("#ff00cc80", False, False),
        ("fff", True, False),
        ("#ggg", True, False),
        ("#12345", True, False),
        ("", True, False),
    ],
)
def test_valid_hex_color(raw: str, allow_alpha: bool, expected: bool) -> None:
    assert iu.valid_hex_color(raw, allow_alpha) is expected


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("ES91 2100 0418 4502 0005 1332", True),
        ("es9121000418450200051332", True),
        ("GB82 WEST 1234 5698 7654 32", True),
        ("DE89 3704 0044 0532 0130 00", True),
        ("ES91 2100 0418 4502 0005 1333", False),
        ("ES9", False),
        ("1234 5678 9012 3456", False),
        ("ES91-2100", False),
        ("", False),
    ],
)
def test_valid_iban(raw: str, expected: bool) -> None:
    assert iu.valid_iban(raw) is expected


@pytest.mark.parametrize(
    ("raw", "version", "expected"),
    [
        ("192.168.1.1", None, True),
        ("::1", None, True),
        ("1.2.3.4", 4, True),
        ("::1", 6, True),
        ("::1", 4, False),
        ("1.2.3.4", 6, False),
        ("999.1.1.1", None, False),
        ("1.2.3.4 ", None, False),
        ("", None, False),
    ],
)
def test_valid_ip(raw: str, version: int | None, expected: bool) -> None:
    assert iu.valid_ip(raw, version) is expected


def test_valid_ip_invalid_version() -> None:
    with pytest.raises(ValueError, match="version"):
        iu.valid_ip("1.2.3.4", 5)


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ('{"a": [1, 2]}', True),
        ("123", True),
        ("null", True),
        ("{'a': 1}", False),
        ("NaN", False),
        ("Infinity", False),
        ("-Infinity", False),
        ("[1,", False),
        ("", False),
        ("[" * 100_000, False),
    ],
)
def test_valid_json(raw: str, expected: bool) -> None:
    assert iu.valid_json(raw) is expected


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("X1234567L", True),
        ("x1234567l", True),
        ("Y1234567X", True),
        ("Z1234567R", True),
        ("X1234567A", False),
        ("A1234567L", False),
        ("12345678Z", False),
        ("", False),
    ],
)
def test_valid_nie(raw: str, expected: bool) -> None:
    assert iu.valid_nie(raw) is expected


class TestValidPassword:
    @pytest.mark.parametrize(
        ("raw", "kwargs", "expected"),
        [
            ("abc123", {}, True),
            ("Abc123", {}, True),
            ("Abc123", {"allow_uppercase": False}, False),
            ("abc#1", {"special_characters": "#"}, True),
            ("abc#1", {}, False),
            ("añb1", {}, True),
            ("abc", {}, False),
            ("a" * 11, {}, False),
            ("1234", {"only_digits": True}, True),
            ("12a4", {"only_digits": True}, False),
        ],
    )
    def test_validation(
        self, raw: str, kwargs: dict[str, object], expected: bool
    ) -> None:
        assert iu.valid_password(raw, (4, 10), **kwargs) is expected  # type: ignore[arg-type]

    def test_ambiguous_arguments(self) -> None:
        with pytest.raises(ValueError, match="ambiguos"):
            iu.valid_password("1234", (4, 10), special_characters="#", only_digits=True)

    def test_inconsistent_length(self) -> None:
        with pytest.raises(ValueError, match="incoherente"):
            iu.valid_password("abcd", (10, 4))


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("+34 612 345 678", True),
        (" +34612345678 ", True),
        ("(91) 123-4567", True),
        ("612.345.678", True),
        ("12345", False),
        ("+34 612 345 678 901 234", False),
        ("+(34", False),
        ("612 345 67a", False),
        ("abc", False),
        ("", False),
    ],
)
def test_valid_phone(raw: str, expected: bool) -> None:
    assert iu.valid_phone(raw) is expected


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("hola-mundo", True),
        ("a", True),
        ("a1-b2", True),
        ("Hola Mundo", False),
        ("hola--mundo", False),
        ("-hola", False),
        ("hola-", False),
        ("", False),
    ],
)
def test_valid_slug(raw: str, expected: bool) -> None:
    assert iu.valid_slug(raw) is expected


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("https://example.com/x", True),
        ("http://localhost:8000", True),
        ("HTTP://EXAMPLE.COM", True),
        ("ftp://example.com", False),
        ("example.com", False),
        ("http://", False),
        ("http://@", False),
        ("http://exa mple.com", False),
        ("http://[::1", False),
        ("http://a:99999999", False),
        ("", False),
    ],
)
def test_valid_url(raw: str, expected: bool) -> None:
    assert iu.valid_url(raw) is expected


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("123e4567-e89b-12d3-a456-426614174000", True),
        ("123E4567-E89B-12D3-A456-426614174000", True),
        ("123e4567", False),
        ("123e4567e89b12d3a456426614174000", False),
        ("123e4567-e89b-12d3-a456-42661417400g", False),
        ("", False),
    ],
)
def test_valid_uuid(raw: str, expected: bool) -> None:
    assert iu.valid_uuid(raw) is expected
