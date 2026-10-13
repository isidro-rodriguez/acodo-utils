"""Genera API.md a partir de los docstrings de `irg_utils`.

Uso:
    uv run python scripts/gen_api.py          # reescribe API.md
    uv run python scripts/gen_api.py --check  # falla si API.md está desactualizado
"""

import ast
import re
import sys
import textwrap
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SOURCES = (
    ROOT / "src" / "irg_utils" / "converters.py",
    ROOT / "src" / "irg_utils" / "checkers.py",
    ROOT / "src" / "irg_utils" / "parsers.py",
    ROOT / "src" / "irg_utils" / "validation.py",
)
TARGET = ROOT / "API.md"

CATEGORIES = (
    ("to_", "Conversores", "Transforman tipos de datos."),
    ("has_", "Comprobaciones", "Verifican que los objetos cumplan los requisitos."),
    ("parse_", "Parsers", "Transforman tipos de datos a strings legibles."),
    ("valid_", "Validaciones", "Verifican que un string tenga el formato requerido."),
)

HEADER = """\
# API de irg_utils

Referencia de uso del paquete. Se genera a partir de los docstrings con
`scripts/gen_api.py`: no editar a mano.

```python
from irg_utils import to_bool, valid_email
```

## Convenciones

- `to_*`: nunca lanzan excepciones por valores inválidos; devuelven `None`.
- `has_*` y `valid_*`: devuelven `bool`.
- `parse_*`: devuelven `str`, salvo `parse_duration`, que devuelve `timedelta | None`.
- `ValueError` solo se lanza ante argumentos de configuración incorrectos
  (código de lenguaje, rango de longitud...), nunca por el dato evaluado.
- Dentro de cada categoría, las funciones están en orden alfabético.
"""

SECTION_RE = re.compile(r"^(Args|Returns|Raises|Examples):\s*$", re.MULTILINE)


def split_docstring(doc: str) -> tuple[str, dict[str, str]]:
    """Separa un docstring estilo Google en descripción y secciones."""
    parts = SECTION_RE.split(doc)
    sections = {
        name: textwrap.dedent(body).strip("\n")
        for name, body in zip(parts[1::2], parts[2::2], strict=True)
    }
    return parts[0].strip(), sections


def parse_items(body: str) -> list[tuple[str, str]]:
    """Convierte una sección `nombre: texto` (con continuaciones) en pares."""
    items: list[tuple[str, str]] = []
    for line in body.splitlines():
        if not line.strip():
            continue
        if line[0].isspace() and items:
            name, text = items[-1]
            items[-1] = (name, f"{text} {line.strip()}")
        else:
            name, _, text = line.partition(":")
            items.append((name.strip(), text.strip()))
    return items


def signature(node: ast.FunctionDef) -> str:
    """Devuelve la firma de la función, en varias líneas si es larga."""
    args = node.args
    positional = args.posonlyargs + args.args
    defaults = [None] * (len(positional) - len(args.defaults)) + list(args.defaults)
    params = [
        ast.unparse(arg)
        if default is None
        else f"{ast.unparse(arg)} = {ast.unparse(default)}"
        for arg, default in zip(positional, defaults, strict=True)
    ]
    returns = f" -> {ast.unparse(node.returns)}" if node.returns else ""

    one_line = f"{node.name}({', '.join(params)}){returns}"
    if len(one_line) <= 79:
        return one_line
    body = "".join(f"    {param},\n" for param in params)
    return f"{node.name}(\n{body}){returns}"


def render_function(node: ast.FunctionDef, doc: str) -> str:
    """Genera la sección Markdown de una función."""
    description, sections = split_docstring(doc)
    out = [
        f"### `{node.name}`",
        "",
        f"```python\n{signature(node)}\n```",
        "",
        description,
    ]

    if "Args" in sections:
        out += ["", "**Parámetros**", ""]
        out += [f"- `{name}`: {text}" for name, text in parse_items(sections["Args"])]
    if "Returns" in sections:
        returns = " ".join(sections["Returns"].split())
        out += ["", f"**Devuelve:** {returns}"]
    if "Raises" in sections:
        out += ["", "**Lanza**", ""]
        out += [f"- `{name}`: {text}" for name, text in parse_items(sections["Raises"])]
    if "Examples" in sections:
        out += ["", "**Ejemplos**", "", f"```pycon\n{sections['Examples']}\n```"]
    return "\n".join(out)


def build() -> str:
    """Construye el contenido completo de API.md."""
    functions = [
        node
        for source in SOURCES
        for node in ast.parse(source.read_text(encoding="utf-8")).body
        if isinstance(node, ast.FunctionDef) and not node.name.startswith("_")
    ]

    index: list[str] = []
    body: list[str] = []
    for prefix, title, summary in CATEGORIES:
        nodes = [node for node in functions if node.name.startswith(prefix)]
        index += ["", f"**{title}**", ""]
        body += [f"## {title}", "", summary]
        for node in nodes:
            doc = ast.get_docstring(node) or ""
            first_line = doc.split("\n", 1)[0]
            index.append(f"- [`{node.name}`](#{node.name}): {first_line}")
            body += ["", render_function(node, doc)]
        body.append("")

    parts = [HEADER, "## Índice", *index, "", *body]
    return "\n".join(parts).rstrip("\n") + "\n"


def main() -> int:
    """Escribe API.md, o lo comprueba con `--check`."""
    content = build()
    if "--check" in sys.argv[1:]:
        current = TARGET.read_text(encoding="utf-8") if TARGET.exists() else ""
        if current != content:
            print("API.md desactualizado: ejecuta `uv run python scripts/gen_api.py`.")
            return 1
        return 0
    TARGET.write_text(content, encoding="utf-8", newline="\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
