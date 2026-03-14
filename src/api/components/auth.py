import time

from functools import wraps
from sanic import Request
from components.response import JSON


# Cache structure: token -> (api_key_id, is_admin, expires_at)
_TOKEN_CACHE: dict[str, tuple[int, bool, float]] = {}
_CACHE_TTL = 60  # seconds


async def _resolve_token(request: Request, token: str) -> dict | None:
    """
    Resolves a bearer token to its api_keys row, using the in-memory TTL cache.
    Returns a dict with 'api_key_id' and 'is_admin', or None if invalid.
    """
    now = time.monotonic()
    cached = _TOKEN_CACHE.get(token)

    if cached and cached[2] > now:
        return {"api_key_id": cached[0], "is_admin": cached[1]}

    row = await request.app.ctx.pool.fetchrow(
        "SELECT id, admin FROM api_keys WHERE key = $1", token
    )
    if not row:
        _TOKEN_CACHE.pop(token, None)
        return None

    _TOKEN_CACHE[token] = (row["id"], row["admin"], now + _CACHE_TTL)

    return {
        "api_key_id": row["id"],
        "is_admin": row["admin"],
    }


def require_api_key(f):
    """
    Decorator that validates the Authorization: Bearer <token> header against the
    api_keys table. Valid tokens are cached in memory for 60 seconds.

    Sets request.ctx.api_key_id and request.ctx.is_admin on success.
    Returns 401 if the token is missing or invalid.
    """

    @wraps(f)
    async def decorated(request: Request, *args, **kwargs):
        auth = request.headers.get("Authorization", "")
        token = auth[7:] if auth.startswith("Bearer ") else ""

        result = await _resolve_token(request, token)
        if result is None:
            return JSON(
                request=request,
                success=False,
                message="Missing or invalid API key.",
                status=401,
            ).generate()

        request.ctx.api_key_id = result["api_key_id"]
        request.ctx.is_admin = result["is_admin"]
        return await f(request, *args, **kwargs)

    return decorated


def require_admin_key(f):
    """
    Decorator that extends require_api_key, additionally requiring admin=true.
    Returns 403 if the key is valid but not an admin key.
    """

    @wraps(f)
    async def decorated(request: Request, *args, **kwargs):
        auth = request.headers.get("Authorization", "")
        token = auth[7:] if auth.startswith("Bearer ") else ""

        result = await _resolve_token(request, token)
        if result is None:
            return JSON(
                request=request,
                success=False,
                message="Missing or invalid API key.",
                status=401,
            ).generate()

        if not result["is_admin"]:
            return JSON(
                request=request,
                success=False,
                message="Admin privileges required.",
                status=403,
            ).generate()

        request.ctx.api_key_id = result["api_key_id"]
        request.ctx.is_admin = True
        return await f(request, *args, **kwargs)

    return decorated
