from components.ratelimit import ratelimit
from components.response import JSON
from components.argument import Argument, inputs
from components.rules import Rules
from models.exceptions import RateLimited, NotFound
from sanic.response import JSONResponse
from sanic import Blueprint, Request
from sanic_ext import openapi
from urllib.parse import unquote


bp = Blueprint(name="Translations", url_prefix="/translations", version=1, version_prefix="v")


# GET /translations
@bp.route("/", methods=["GET"])
@openapi.definition(
    summary="List bird name translations",
    description=(
        "Returns the EN/FR translation table for BirdNET species labels. "
        "Supports pagination and optional full-text search across scientific name, "
        "English common name and French common name."
    ),
    tag="Translations",
)
@openapi.response(
    status=200,
    content={"application/json": {"schema": {"type": "object"}}},
    description="Paginated list of translations.",
)
@openapi.response(
    status=429,
    content={"application/json": RateLimited},
    description="You have sent too many requests. Please try again later.",
)
@openapi.parameter(
    name="q",
    description="Search across scientific name, English name and French name",
    required=False,
    schema=str,
    location="query",
    example="merle",
)
@openapi.parameter(
    name="limit",
    description="Maximum number of results to return (1–200, default 50)",
    required=False,
    schema=int,
    location="query",
    example=50,
)
@openapi.parameter(
    name="offset",
    description="Number of results to skip (default 0)",
    required=False,
    schema=int,
    location="query",
    example=0,
)
@inputs(
    Argument(
        name="q",
        description="Search query",
        methods={"q": None},
        call=str,
        required=False,
        headers=False,
        allow_multiple=False,
        deprecated=False,
    ),
    Argument(
        name="limit",
        description="Maximum number of results",
        methods={"limit": Rules.integer},
        call=int,
        required=False,
        headers=False,
        allow_multiple=False,
        deprecated=False,
    ),
    Argument(
        name="offset",
        description="Number of results to skip",
        methods={"offset": Rules.integer},
        call=int,
        required=False,
        headers=False,
        allow_multiple=False,
        deprecated=False,
    ),
)
@ratelimit()
async def getTranslations(
    request: Request,
    q: str = None,
    limit: int = None,
    offset: int = None,
) -> JSONResponse:
    """
    Returns a paginated list of EN/FR bird name translations.

    :return: JSONResponse
    """
    limit = min(limit or 50, 200)
    offset = offset or 0

    if q:
        pattern = f"%{q}%"
        count_row = await request.app.ctx.pool.fetchrow(
            """
            SELECT COUNT(*) AS total FROM bird_name_translations
            WHERE scientific_name ILIKE $1
               OR common_name_en  ILIKE $1
               OR common_name_fr  ILIKE $1
            """,
            pattern,
        )
        rows = await request.app.ctx.pool.fetch(
            """
            SELECT scientific_name, common_name_en, common_name_fr
            FROM bird_name_translations
            WHERE scientific_name ILIKE $1
               OR common_name_en  ILIKE $1
               OR common_name_fr  ILIKE $1
            ORDER BY scientific_name
            LIMIT $2 OFFSET $3
            """,
            pattern,
            limit,
            offset,
        )
    else:
        count_row = await request.app.ctx.pool.fetchrow(
            "SELECT COUNT(*) AS total FROM bird_name_translations"
        )
        rows = await request.app.ctx.pool.fetch(
            """
            SELECT scientific_name, common_name_en, common_name_fr
            FROM bird_name_translations
            ORDER BY scientific_name
            LIMIT $1 OFFSET $2
            """,
            limit,
            offset,
        )

    return JSON(
        request=request,
        success=True,
        data={
            "total": count_row["total"],
            "limit": limit,
            "offset": offset,
            "translations": [
                {
                    "scientific_name": row["scientific_name"],
                    "common_name_en": row["common_name_en"],
                    "common_name_fr": row["common_name_fr"],
                }
                for row in rows
            ],
        },
        status=200,
    ).generate()


# GET /translations/<scientific_name>
@bp.route("/<scientific_name:str>", methods=["GET"])
@openapi.definition(
    summary="Get translation for a species",
    description=(
        "Returns the English and French common names for a given scientific name. "
        "The scientific name is URL-encoded (e.g. Turdus%20merula)."
    ),
    tag="Translations",
)
@openapi.response(
    status=200,
    content={"application/json": {"schema": {"type": "object"}}},
    description="Translation entry.",
)
@openapi.response(
    status=404,
    content={"application/json": NotFound},
    description="No translation found for this scientific name.",
)
@openapi.response(
    status=429,
    content={"application/json": RateLimited},
    description="You have sent too many requests. Please try again later.",
)
@openapi.parameter(
    name="scientific_name",
    description="Scientific name of the species (URL-encoded)",
    required=True,
    schema=str,
    location="path",
    example="Turdus merula",
)
@inputs(
    Argument(
        name="scientific_name",
        description="Scientific name",
        methods={"scientific_name": None},
        call=str,
        required=True,
        headers=False,
        allow_multiple=False,
        deprecated=False,
    ),
)
@ratelimit()
async def getTranslation(request: Request, scientific_name: str) -> JSONResponse:
    """
    Returns the EN/FR translation for a single species.

    :param scientific_name: Scientific name (URL-encoded)
    :return: JSONResponse
    """
    scientific_name = unquote(scientific_name)

    row = await request.app.ctx.pool.fetchrow(
        """
        SELECT scientific_name, common_name_en, common_name_fr
        FROM bird_name_translations
        WHERE scientific_name = $1
        """,
        scientific_name,
    )

    if row is None:
        return JSON(
            request=request,
            success=False,
            message="No translation found for this species.",
            status=404,
        ).generate()

    return JSON(
        request=request,
        success=True,
        data={
            "scientific_name": row["scientific_name"],
            "common_name_en": row["common_name_en"],
            "common_name_fr": row["common_name_fr"],
        },
        status=200,
    ).generate()
