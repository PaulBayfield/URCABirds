from components.ratelimit import ratelimit
from components.response import JSON
from components.argument import Argument, inputs
from models.responses import SpeciesList, SpeciesItem
from models.exceptions import RateLimited, NotFound
from sanic.response import JSONResponse
from sanic import Blueprint, Request
from sanic_ext import openapi
from urllib.parse import unquote


bp = Blueprint(name="Species", url_prefix="/species", version=1, version_prefix="v")


# GET /species
@bp.route("/", methods=["GET"])
@openapi.definition(
    summary="List all observed species",
    description="Returns all bird species that have been detected at least once, along with their detection statistics.",
    tag="Species",
)
@openapi.response(
    status=200,
    content={"application/json": SpeciesList},
    description="List of species.",
)
@openapi.response(
    status=429,
    content={"application/json": RateLimited},
    description="You have sent too many requests. Please try again later.",
)
@ratelimit()
async def getSpeciesList(request: Request) -> JSONResponse:
    """
    Returns all observed species with their detection counts.

    :return: JSONResponse
    """
    rows = await request.app.ctx.pool.fetch(
        """
        SELECT
            species AS name,
            COUNT(*) AS total_detections,
            MAX(timestamp) AS last_detection
        FROM detections
        GROUP BY species
        ORDER BY total_detections DESC
        """
    )

    return JSON(
        request=request,
        success=True,
        data=[
            {
                "name": row["name"],
                "total_detections": row["total_detections"],
                "last_detection": row["last_detection"],
            }
            for row in rows
        ],
        status=200,
    ).generate()


# GET /species/<name>
@bp.route("/<name:str>", methods=["GET"])
@openapi.definition(
    summary="Get a species by name",
    description="Returns statistics for a single bird species identified by its scientific name.",
    tag="Species",
)
@openapi.response(
    status=200,
    content={"application/json": SpeciesItem},
    description="Species statistics.",
)
@openapi.response(
    status=404,
    content={"application/json": NotFound},
    description="The species was not found.",
)
@openapi.response(
    status=429,
    content={"application/json": RateLimited},
    description="You have sent too many requests. Please try again later.",
)
@openapi.parameter(
    name="name",
    description="Scientific name of the species",
    required=True,
    schema=str,
    location="path",
    example="Turdus merula",
)
@inputs(
    Argument(
        name="name",
        description="Scientific name of the species",
        methods={"name": None},
        call=str,
        required=True,
        headers=False,
        allow_multiple=False,
        deprecated=False,
    ),
)
@ratelimit()
async def getSpecies(request: Request, name: str) -> JSONResponse:
    """
    Returns the statistics of a single bird species.

    :param name: Scientific name of the species
    :return: JSONResponse
    """
    name = unquote(name)

    row = await request.app.ctx.pool.fetchrow(
        """
        SELECT
            species AS name,
            COUNT(*) AS total_detections,
            MAX(timestamp) AS last_detection
        FROM detections
        WHERE species = $1
        GROUP BY species
        """,
        name,
    )

    if row is None:
        return JSON(
            request=request,
            success=False,
            message="The species was not found.",
            status=404,
        ).generate()

    return JSON(
        request=request,
        success=True,
        data={
            "name": row["name"],
            "total_detections": row["total_detections"],
            "last_detection": row["last_detection"],
        },
        status=200,
    ).generate()
