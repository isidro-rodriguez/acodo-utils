# acodo_utils

Una simple librería de utilidades. Consulta
la [API web](https://isidro-rodriguez.github.io/irg-utils/).

> Requiere **Python >= 3.11** y no introduce dependencias.

## Instalación

Para instalar o actualizar el paquete.

```bash
uv add git+https://github.com/isidro-rodriguez/irg-utils
```

## Uso

```python
from acodo_utils import to_bool, valid_email

to_bool("sí")  # True
valid_email("hola")  # False
```

## Desarrollo

```bash
# Actualización ante cambios de versión.
uv sync

# Comprobación de calidad (formatos, tipos y testeo)
uv run ruff format
uv run ruff check
uv run ty check
uv run pytest --cov=src --cov-report=term-missing

# Consulta offline de la API en <http://localhost:8080>
uv run pdoc .\src\acodo_utils\ -d google 
```

## Licencia

MIT — ver [LICENSE](LICENSE).
