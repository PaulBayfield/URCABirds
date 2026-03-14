from components.ratelimit import ratelimit
from components.response import JSON
from models.responses import Status, Stats
from models.exceptions import RateLimited
from sanic.response import JSONResponse
from sanic import Blueprint, Request
from sanic_ext import openapi


bp = Blueprint(name="Service", url_prefix="/", version=1, version_prefix="v")


# /status
@bp.route("/status", methods=["GET"])
@openapi.definition(
    summary="API Status",
    description="Returns the current status of the API.",
    tag="Service",
)
@openapi.response(
    status=200, content={"application/json": Status}, description="The API is online."
)
@openapi.response(
    status=429,
    content={"application/json": RateLimited},
    description="You have sent too many requests. Please try again later.",
)
@ratelimit()
async def getStatus(request: Request) -> JSONResponse:
    """
    Returns the API status.

    :return: JSONResponse
    """
    return JSON(
        request=request,
        success=True,
        message="The API is online.",
        status=200,
    ).generate()


# /stats
@bp.route("/stats", methods=["GET"])
@openapi.definition(
    summary="API Statistics",
    description="Returns global statistics about recorded bird detections.",
    tag="Service",
)
@openapi.response(
    status=200, content={"application/json": Stats}, description="Global detection statistics."
)
@openapi.response(
    status=429,
    content={"application/json": RateLimited},
    description="You have sent too many requests. Please try again later.",
)
@ratelimit()
async def getStats(request: Request) -> JSONResponse:
    """
    Returns global statistics about the bird detection database.

    :return: JSONResponse
    """
    row = await request.app.ctx.pool.fetchrow(
        """
        SELECT
            COUNT(*) AS total_detections,
            COUNT(DISTINCT sensor_id) AS total_sensors,
            COUNT(DISTINCT species) AS total_species
        FROM detections
        """
    )

    return JSON(
        request=request,
        success=True,
        data={
            "total_detections": row["total_detections"],
            "total_sensors": row["total_sensors"],
            "total_species": row["total_species"],
        },
        status=200,
    ).generate()
