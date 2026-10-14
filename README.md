# irg_utils

Utilidades de uso compartido entre proyectos. Python >= 3.11, sin dependencias.

## Instalación

Para instalar o actualizar el paquete.

```bash
uv add git+https://github.com/isidro-rodriguez/irg-utils
```

## Uso

```python
from irg_utils import to_bool, valid_email

to_bool("sí")  # True
valid_email("hola")  # False
```

[API web](https://isidro-rodriguez.github.io/irg-utils/)

## Desarrollo

```bash
# Actualización ante cambios de versión.
uv sync

# Comprobación de calidad (formatos, tipos y testeo)
uv run ruff format
uv run ruff check
uv run ty check
uv run pytest

# Instalación de los hooks en .git
uv run pre-commit install

# Verificación manual de todos los hooks
uv run pre-commit run --all-files

# Generador de tokens para commits de agente
uv run py scripts/gh_token.py

# Consulta offline de la API en <http://localhost:8080>
uv run pdoc .\src\irg_utils\ -d google 
```

## Licencia

MIT — ver [LICENSE](LICENSE).
