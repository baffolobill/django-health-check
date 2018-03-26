import logging
from django.core.cache import CacheKeyWarning, cache

from health_check.backends import BaseHealthCheckBackend
from health_check.exceptions import (
    ServiceReturnedUnexpectedResult, ServiceUnavailable
)

logger = logging.getLogger(__name__)


class CacheBackend(BaseHealthCheckBackend):
    def check_status(self):
        try:
            cache.set('djangohealtcheck_test', 'itworks', 1)
            cache_get_value = cache.get("djangohealtcheck_test")
            if not cache_get_value == "itworks":
                logger.warning(
                    "Cache is unavailable, because cache value \"%r\" != \"itworks\".",
                    cache_get_value)
                raise ServiceUnavailable("Cache key does not match")
        except CacheKeyWarning as e:
            self.add_error(ServiceReturnedUnexpectedResult("Cache key warning"), e)
        except ValueError as e:
            self.add_error(ServiceReturnedUnexpectedResult("ValueError"), e)
