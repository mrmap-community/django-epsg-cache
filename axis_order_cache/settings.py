from django.conf import settings
from django.core.cache import DEFAULT_CACHE_ALIAS

CACHE_BACKEND = getattr(settings,
                        "AXIS_ORDER_CACHE_BACKEND", DEFAULT_CACHE_ALIAS)
KEY_PREFIX = getattr(settings,
                     "AXIS_ORDER_CACHE_KEY_PREFIX", "axis_order_cache")
EPSG_API_URL = getattr(settings,
                       "AXIS_ORDER_CACHE_EPSG_API_URL", "https://apps.epsg.org/api/v1/")


TTL = getattr(settings, "AXIS_ORDER_CACHE_TTL_FALLBACK", 86400)  # 1 day
TTL_FALLBACK = getattr(settings,
                       "AXIS_ORDER_CACHE_TTL_FALLBACK", 300)  # 5 minutes
