from slowapi import Limiter
from slowapi.util import get_remote_address

# Use the remote address (IP) for rate limiting. 
# In production with a load balancer, ensure `X-Forwarded-For` is configured correctly.
limiter = Limiter(key_func=get_remote_address, default_limits=["100/minute"])
