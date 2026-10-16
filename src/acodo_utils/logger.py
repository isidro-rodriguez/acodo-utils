"""Servicio de registro de mensajes de pyMedia.

Envuelve el módulo estándar ``logging`` y lo configura con un handler de consola
y, opcionalmente, un handler de fichero en el directorio de configuración del
usuario o en una ruta explícita.

Este módulo no introduce dependencias externas: solo utiliza la biblioteca
estándar de Python.
"""

from __future__ import annotations

import logging
import os
import pprint
import sys
from logging.handlers import TimedRotatingFileHandler
from pathlib import Path
from typing import Any

# valid_filename only used inside get_logger; local import avoids circular import.
# (import moved inside get_logger to avoid circular import)

# =============================================================================
# Estado global
# =============================================================================

_configured = False
_logger_name = "acodo"

# =============================================================================
# Helpers
# =============================================================================


def _get_config_dir(app_name: str) -> Path:
    r"""Devuelve el directorio de configuración del usuario para una aplicación.

    La ubicación depende del sistema operativo:

    - **Linux/BSD**: ``~/.config/<app_name>``
    - **macOS**: ``~/Library/Application Support/<app_name>``
    - **Windows**: ``%APPDATA%\\<app_name>``

    Args:
        app_name: Nombre de la aplicación.

    Returns:
        Ruta al directorio de configuración (puede no existir todavía).
    """
    if sys.platform == "win32":
        base = Path(os.environ.get("APPDATA", Path.home() / "AppData" / "Roaming"))
        return base / app_name
    if sys.platform == "darwin":
        return Path.home() / "Library" / "Application Support" / app_name
    # Linux y otros sistemas tipo Unix
    base = Path(os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config"))
    return base / app_name


def _prettify(value: Any) -> str:
    """Convierte un valor en una representación legible de varias líneas.

    Args:
        value: Valor a formatear.

    Returns:
        Cadena formateada con ``pprint`` para contenedores o ``str`` para el
        resto.
    """
    if isinstance(value, (dict, list, tuple, set)):
        return pprint.pformat(value, indent=4, width=120)
    return str(value)


class _DestinationFilter(logging.Filter):
    """Filtra registros según el destino solicitado (consola o fichero)."""

    def __init__(self, key: str) -> None:
        super().__init__()
        self._key = key

    def filter(self, record: logging.LogRecord) -> bool:
        # Si el registro no lleva el flag, se deja pasar por defecto.
        return getattr(record, self._key, True)


# =============================================================================
# Logger
# =============================================================================


class Logger:
    """Wrapper sobre ``logging`` estándar con plantillas de locales."""

    def __init__(self, logger: logging.Logger) -> None:
        """Inicializa el wrapper sobre un logger estándar.

        Args:
            logger: Interfaz principal de la aplicación para generar mensajes.
        """
        self._logger = logger

    def error(
        self,
        msg: str,
        exc_info: bool = False,
        console: bool = True,
        file: bool = True,
        **kwargs: object,
    ) -> None:
        """Muestra log de nivel error.

        Args:
            msg: Mensaje ya traducido a mostrar.
            exc_info: Si ``True``, añade la traza de la excepción activa.
            console: Si ``True``, se muestra por consola.
            file: Si ``True``, se escribe en el fichero de log.
            **kwargs: Valores para interpolar en ``msg`` vía ``%``.
        """
        self._log(
            level=logging.ERROR,
            msg=msg,
            console=console,
            file=file,
            exc_info=exc_info,
            values=kwargs,
        )

    def warning(
        self,
        msg: str,
        console: bool = True,
        file: bool = True,
        **kwargs: object,
    ) -> None:
        """Muestra log de nivel aviso (mensaje ya traducido).

        Args:
            msg: Mensaje ya traducido a mostrar.
            console: Si ``True``, se muestra por consola.
            file: Si ``True``, se escribe en el fichero de log.
            **kwargs: Valores para interpolar en ``msg`` vía ``%``.
        """
        self._log(
            level=logging.WARNING,
            msg=msg,
            console=console,
            file=file,
            values=kwargs,
        )

    def info(
        self,
        msg: str,
        console: bool = True,
        file: bool = True,
        **kwargs: object,
    ) -> None:
        """Muestra log de nivel información (mensaje ya traducido).

        Args:
            msg: Mensaje ya traducido a mostrar.
            console: Si ``True``, se muestra por consola.
            file: Si ``True``, se escribe en el fichero de log.
            **kwargs: Valores para interpolar en ``msg`` vía ``%``.
        """
        self._log(
            level=logging.INFO,
            msg=msg,
            console=console,
            file=file,
            values=kwargs,
        )

    def debug(
        self,
        msg: str,
        console: bool = True,
        file: bool = True,
        **kwargs: object,
    ) -> None:
        """Muestra log de nivel depuración (mensaje ya traducido).

        Args:
            msg: Mensaje ya traducido a mostrar.
            console: Si ``True``, se muestra por consola.
            file: Si ``True``, se escribe en el fichero de log.
            **kwargs: Valores para interpolar en ``msg`` vía ``%``.
        """
        kwargs = {name: _prettify(value) for name, value in kwargs.items()}
        self._log(
            level=logging.DEBUG,
            msg=msg,
            console=console,
            file=file,
            values=kwargs,
        )

    @staticmethod
    def print(*args: Any, **kwargs: Any) -> None:
        """Imprime un objeto por consola (equivalente a ``print``).

        Args:
            *args: Argumentos posicionales para ``print``.
            **kwargs: Argumentos adicionales para ``print``.
        """
        print(*args, **kwargs)

    # Implementación interna
    def _log(
        self,
        level: int,
        msg: str,
        console: bool,
        file: bool,
        *,
        exc_info: bool = False,
        values: dict[str, object] | None = None,
    ) -> None:
        """Envía el registro al logger interno filtrado por destino."""
        self._logger.log(
            level=level,
            msg=self._render(msg=msg, kwargs=values or {}),
            exc_info=exc_info,
            extra={"to_console": console, "to_file": file},
        )

    @staticmethod
    def _render(msg: str, kwargs: dict[str, object]) -> str:
        """Aplica ``%(name)s`` a ``msg`` si hay valores que sustituir."""
        if kwargs:
            return msg % kwargs
        return msg


# =============================================================================
# API pública
# =============================================================================


def get_logger(
    debug: bool = False,
    app_name: str | None = None,
    file: Path | None = None,
) -> Logger | None:
    """Configura y devuelve un :class:`Logger`.

    La configuración es idempotente: solo se realiza la primera vez que se
    invoca. En llamadas posteriores se devuelve el logger ya configurado.

    Args:
        debug: Si ``True``, activa el nivel ``DEBUG``.
        app_name: Si no es ``None``, crea el directorio de configuración del
            sistema para esa aplicación y aloja el fichero de log allí.
        file: Si no es ``None``, crea el fichero de log en la ruta indicada.
            Tiene precedencia sobre ``app_name``.

    Returns:
        Instancia de :class:`Logger` lista para usar.
    """
    from acodo_utils.validators import valid_filename

    if (app_name is not None and not valid_filename(app_name)) or (
        file is not None and not valid_filename(str(file.name))
    ):
        return None

    global _configured
    global _logger_name

    if _configured:
        return Logger(logging.getLogger(_logger_name))

    if app_name is not None:
        _logger_name = app_name

    level = logging.DEBUG if debug else logging.INFO
    root = logging.getLogger()
    root.setLevel(level)

    # Handler de consola
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(logging.Formatter("%(msg)s"))
    console_handler.addFilter(_DestinationFilter("to_console"))
    root.addHandler(console_handler)

    # Handler de fichero (opcional)
    log_path: Path | None = None
    if file is not None:
        log_path = file
    elif app_name is not None:
        log_path = _get_config_dir(app_name) / f"{app_name}.log"

    if log_path is not None:
        log_path.parent.mkdir(parents=True, exist_ok=True)
        file_handler = TimedRotatingFileHandler(
            filename=log_path,
            when="midnight",
            interval=1,
            backupCount=7,
            encoding="utf-8",
        )
        file_handler.suffix = "%Y-%m-%d"
        file_handler.setFormatter(
            logging.Formatter(
                fmt="%(asctime)s %(levelname)-8s %(msg)s",
                datefmt="%Y-%m-%d %H:%M:%S",
            )
        )
        file_handler.addFilter(_DestinationFilter("to_file"))
        root.addHandler(file_handler)

    _configured = True
    return Logger(logging.getLogger(_logger_name))
