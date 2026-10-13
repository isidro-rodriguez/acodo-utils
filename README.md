# irg_utils

Utilidades de uso compartido entre proyectos. Python >= 3.11, sin dependencias.

## Instalación

```bash
uv add git+https://github.com/isidro-rodriguez/irg-utils --tag v0.1.0
```

Para actualizar a una versión nueva:

```bash
uv add git+https://github.com/isidro-rodriguez/irg-utils --tag vX.Y.Z
```

## Uso

```python
from irg_utils import to_bool, valid_email

to_bool("sí")  # True
valid_email("hola")  # False
```

Referencia completa en [API.md](API.md).

## Desarrollo

```bash
uv sync
uv run pre-commit install             # instala los hooks en .git (una vez por clon)
uv run ruff format
uv run ruff check
uv run ty check
uv run pytest                         # cobertura exigida: 100 %
uv run py scripts/gen_api.py          # regenera API.md tras cambiar docstrings
uv run py scripts/gh_token.py         # obtiene un token de Github App
uv run pre-commit run --all-files     # verificación manual de todos los hooks
```

## Licencia

MIT — ver [LICENSE](LICENSE).
