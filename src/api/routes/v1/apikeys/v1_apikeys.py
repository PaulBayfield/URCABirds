from components.ratelimit import ratelimit
from components.response import JSON
from components.auth import require_admin_key
from models.exceptions import RateLimited, Unauthorized, NotFound
from sanic.response import JSONResponse
from sanic import Blueprint, Request
from sanic_ext import openapi
import secrets


bp = Blueprint(name="ApiKeys", url_prefix="/apikeys", version=1, version_prefix="v")


# GET /apikeys
@bp.route("/", methods=["GET"])
@openapi.definition(
    summary="List all API keys",
    description="Returns all API keys (key value is hidden). Requires a valid API key.",
    tag="API Keys",
)
@openapi.response(
    status=200,
    content={"application/json": {"schema": {"type": "object"}}},
    description="List of API keys.",
)
@openapi.response(
    status=401,
    content={"application/json": Unauthorized},
    description="Missing or invalid API key.",
)
@openapi.response(
    status=429,
    content={"application/json": RateLimited},
    description="You have sent too many requests. Please try again later.",
)
@openapi.secured("token")
@require_admin_key
@ratelimit()
async def getApiKeys(request: Request) -> JSONResponse:
    """
    Returns all API keys (without exposing the key value).

    :return: JSONResponse
    """
    rows = await request.app.ctx.pool.fetch(
        "SELECT id, name, created_at FROM api_keys ORDER BY created_at DESC"
    )

    return JSON(
        request=request,
        success=True,
        data=[
            {
                "id": row["id"],
                "name": row["name"],
                "created_at": row["created_at"].isoformat()
                if row["created_at"]
                else None,
            }
            for row in rows
        ],
        status=200,
    ).generate()


# POST /apikeys
@bp.route("/", methods=["POST"])
@openapi.definition(
    summary="Create an API key",
    description="Creates a new API key with an auto-generated token. Requires a valid API key.",
    tag="API Keys",
)
@openapi.body(
    content={
        "application/json": {
            "schema": {
                "type": "object",
                "required": ["name"],
                "properties": {
                    "name": {"type": "string", "example": "Rooftop sensor A"},
                },
            }
        }
    },
    required=True,
    description="API key payload.",
)
@openapi.response(
    status=201,
    content={"application/json": {"schema": {"type": "object"}}},
    description="API key created.",
)
@openapi.response(
    status=400,
    content={"application/json": {"schema": {"type": "object"}}},
    description="Missing or invalid fields.",
)
@openapi.response(
    status=401,
    content={"application/json": Unauthorized},
    description="Missing or invalid API key.",
)
@openapi.response(
    status=429,
    content={"application/json": RateLimited},
    description="You have sent too many requests. Please try again later.",
)
@openapi.secured("token")
@require_admin_key
@ratelimit()
async def postApiKey(request: Request) -> JSONResponse:
    """
    Creates a new API key with an auto-generated secure token.

    :return: JSONResponse
    """
    body = request.json
    if not body:
        return JSON(
            request=request,
            success=False,
            message="Request body is required.",
            status=400,
        ).generate()

    name = body.get("name", "").strip()
    if not name:
        return JSON(
            request=request,
            success=False,
            message="Missing required field: name.",
            status=400,
        ).generate()

    # Generate a secure random API key token
    token = secrets.token_hex(32)

    row = await request.app.ctx.pool.fetchrow(
        "INSERT INTO api_keys (key, name) VALUES ($1, $2) RETURNING id, name, created_at",
        token,
        name,
    )

    return JSON(
        request=request,
        success=True,
        message="API key created successfully.",
        data={
            "id": row["id"],
            "key": token,  # Only time the raw key is exposed — store it now!
            "name": row["name"],
            "created_at": row["created_at"].isoformat() if row["created_at"] else None,
        },
        status=201,
    ).generate()


# DELETE /apikeys/<id>
@bp.route("/<id:int>", methods=["DELETE"])
@openapi.definition(
    summary="Delete an API key",
    description="Deletes an API key by its ID. Requires a valid API key.",
    tag="API Keys",
)
@openapi.response(
    status=200,
    content={"application/json": {"schema": {"type": "object"}}},
    description="API key deleted.",
)
@openapi.response(
    status=404,
    content={"application/json": NotFound},
    description="API key not found.",
)
@openapi.response(
    status=401,
    content={"application/json": Unauthorized},
    description="Missing or invalid API key.",
)
@openapi.response(
    status=429,
    content={"application/json": RateLimited},
    description="You have sent too many requests. Please try again later.",
)
@openapi.parameter(
    name="id",
    description="API key ID",
    required=True,
    schema=int,
    location="path",
    example=1,
)
@openapi.secured("token")
@require_admin_key
@ratelimit()
async def deleteApiKey(request: Request, id: int) -> JSONResponse:
    """
    Deletes an API key by its ID.

    :param id: API key ID
    :return: JSONResponse
    """
    result = await request.app.ctx.pool.execute(
        "DELETE FROM api_keys WHERE id = $1", id
    )

    if result == "DELETE 0":
        return JSON(
            request=request,
            success=False,
            message="API key not found.",
            status=404,
        ).generate()

    return JSON(
        request=request,
        success=True,
        message="API key deleted successfully.",
        status=200,
    ).generate()
