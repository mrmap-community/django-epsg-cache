from django.conf import settings
from django.core.cache import DEFAULT_CACHE_ALIAS

CACHE_BACKEND = getattr(settings,
                        "EPSG_CACHE_BACKEND", DEFAULT_CACHE_ALIAS)
KEY_PREFIX = getattr(settings,
                     "EPSG_CACHE_KEY_PREFIX", "EPSG_CACHE")
EPSG_API_URL = getattr(settings,
                       "EPSG_CACHE_EPSG_API_URL", "https://apps.epsg.org/api/v1/")


TTL = getattr(settings, "EPSG_CACHE_TTL_FALLBACK", 86400)  # 1 day
TTL_FALLBACK = getattr(settings,
                       "EPSG_CACHE_TTL_FALLBACK", 300)  # 5 minutes
