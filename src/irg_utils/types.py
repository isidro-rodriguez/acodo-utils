"""Tipos compartidos del paquete: enumeraciones de redes sociales."""

from __future__ import annotations

import re
from enum import StrEnum, auto
from functools import cache

# Usuario de GitHub: 1-39 caracteres, sin guiones al inicio ni al final.
_GITHUB_USER = r"[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,37}[a-zA-Z0-9])?"

_FACEBOOK_HOSTS = r"facebook\.com|fb\.com"


def _social_pattern(hosts: str, path: str) -> re.Pattern[str]:
    # Esquema y `www.` opcionales; admite barra final, query y fragmento.
    return re.compile(
        rf"(?:https?://)?(?:www\.)?(?:{hosts})/{path}/?(?:[?#]\S*)?",
        re.IGNORECASE,
    )


class SocialVariant(StrEnum):
    """Tipos de enlace de red social.

    Examples:
        >>> SocialVariant.REEL
        <SocialVariant.REEL: 'reel'>
        >>> SocialVariant("page") is SocialVariant.PAGE
        True
    """

    PROFILE = auto()
    PAGE = auto()
    REEL = auto()


class SocialPlatform(StrEnum):
    """Redes sociales soportadas por `valid_social_url`.

    Examples:
        >>> SocialPlatform.GITHUB
        <SocialPlatform.GITHUB: 'github'>
        >>> SocialPlatform("x") is SocialPlatform.X
        True
    """

    GITHUB = auto()
    FACEBOOK = auto()
    X = auto()
    INSTAGRAM = auto()
    TIKTOK = auto()
    LINKEDIN = auto()

    @cache
    def pattern(self, variant: SocialVariant) -> re.Pattern[str] | None:
        """Devuelve la expresión regular de un tipo de enlace de la plataforma.

        Solo existen las combinaciones plataforma/variante que tienen sentido.
        En GitHub, `PAGE` es un repositorio; en TikTok, `REEL` es un vídeo.

        Args:
            variant: Tipo de enlace (`SocialVariant`).

        Returns:
            El patrón compilado, o `None` si la plataforma no tiene esa variante.

        Examples:
            >>> SocialPlatform.GITHUB.pattern(SocialVariant.PROFILE) is not None
            True
            >>> SocialPlatform.GITHUB.pattern(SocialVariant.REEL) is None
            True
        """
        match self, variant:
            case SocialPlatform.GITHUB, SocialVariant.PROFILE:
                return _social_pattern(r"github\.com", _GITHUB_USER)
            case SocialPlatform.GITHUB, SocialVariant.PAGE:
                return _social_pattern(r"github\.com", rf"{_GITHUB_USER}/[\w.-]+")
            case SocialPlatform.FACEBOOK, SocialVariant.PROFILE:
                return _social_pattern(_FACEBOOK_HOSTS, r"[a-zA-Z0-9.]{5,50}")
            case SocialPlatform.FACEBOOK, SocialVariant.PAGE:
                return _social_pattern(_FACEBOOK_HOSTS, r"pages/[\w%-]+/\d+")
            case SocialPlatform.FACEBOOK, SocialVariant.REEL:
                return _social_pattern(_FACEBOOK_HOSTS, r"reel/\d+")
            case SocialPlatform.X, SocialVariant.PROFILE:
                return _social_pattern(r"x\.com|twitter\.com", r"\w{1,15}")
            case SocialPlatform.INSTAGRAM, SocialVariant.PROFILE:
                return _social_pattern(r"instagram\.com", r"[\w.]{1,30}")
            case SocialPlatform.INSTAGRAM, SocialVariant.REEL:
                return _social_pattern(r"instagram\.com", r"reels?/[\w-]+")
            case SocialPlatform.TIKTOK, SocialVariant.PROFILE:
                return _social_pattern(r"tiktok\.com", r"@[\w.]{2,24}")
            case SocialPlatform.TIKTOK, SocialVariant.REEL:
                return _social_pattern(r"tiktok\.com", r"@[\w.]{2,24}/video/\d+")
            case SocialPlatform.LINKEDIN, SocialVariant.PROFILE:
                return _social_pattern(r"linkedin\.com", r"in/[\w%-]{3,100}")
            case SocialPlatform.LINKEDIN, SocialVariant.PAGE:
                return _social_pattern(r"linkedin\.com", r"company/[\w%-]+")
            case _:
                return None
