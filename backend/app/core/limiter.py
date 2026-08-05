from slowapi import Limiter
from slowapi.util import get_remote_address

# Global default limit: 100 requests per minute per IP address
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["100/minute"],
)