"""Tipos compartidos del paquete: enumeraciones de redes sociales."""

from enum import StrEnum


class SocialPlatform(StrEnum):
    """Redes sociales soportadas por `valid_social_url`.

    Examples:
        >>> SocialPlatform.GITHUB
        <SocialPlatform.GITHUB: 'github'>
        >>> SocialPlatform("x") is SocialPlatform.X
        True
    """

    GITHUB = "github"
    FACEBOOK = "facebook"
    X = "x"
    INSTAGRAM = "instagram"
    TIKTOK = "tiktok"
    LINKEDIN = "linkedin"


class SocialVariant(StrEnum):
    """Tipos de enlace de red social.

    Examples:
        >>> SocialVariant.REEL
        <SocialVariant.REEL: 'reel'>
        >>> SocialVariant("page") is SocialVariant.PAGE
        True
    """

    PROFILE = "profile"
    PAGE = "page"
    REEL = "reel"
