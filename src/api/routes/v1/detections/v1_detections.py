from components.ratelimit import ratelimit
from components.response import JSON
from components.argument import Argument, inputs
from components.auth import require_api_key
from components.rules import Rules
from models.responses import Detections, Detection
from models.exceptions import RateLimited, BadRequest, NotFound, Unauthorized
from sanic.response import JSONResponse
from sanic import Blueprint, Request
from sanic_ext import openapi


bp = Blueprint(name="Detections", url_prefix="/detections", version=1, version_prefix="v")


# POST /detections
@bp.route("/", methods=["POST"])
@openapi.definition(
    summary="Submit a bird detection",
    description=(
        "Receives a bird detection from a sensor worker and stores it in the database. "
        "Requires a valid `Authorization: Bearer <API_KEY>` header. "
        "The `sensor_id` must match a registered sensor."
    ),
    tag="Detections",
)
@openapi.body(
    content={
        "application/json": {
            "schema": {
                "type": "object",
                "required": ["sensor_id", "timestamp", "species", "confidence"],
                "properties": {
                    "sensor_id": {"type": "string", "example": "sensor-001"},
                    "timestamp": {"type": "string", "example": "2024-01-15T10:30:00+00:00"},
                    "species": {"type": "string", "example": "Turdus merula"},
                    "confidence": {"type": "number", "format": "float", "example": 0.87},
                },
            }
        }
    },
    required=True,
    description="Detection payload from the sensor worker.",
)
@openapi.response(
    status=201,
    content={"application/json": {"schema": {"type": "object"}}},
    description="Detection successfully recorded.",
)
@openapi.response(
    status=400,
    content={"application/json": BadRequest},
    description="Invalid or missing fields in the request body.",
)
@openapi.response(
    status=401,
    content={"application/json": Unauthorized},
    description="Missing or invalid API key.",
)
@openapi.response(
    status=404,
    content={"application/json": NotFound},
    description="The sensor_id does not match any registered sensor.",
)
@openapi.response(
    status=429,
    content={"application/json": RateLimited},
    description="You have sent too many requests. Please try again later.",
)
@openapi.secured("token")
@require_api_key
@ratelimit()
async def postDetection(request: Request) -> JSONResponse:
    """
    Receives a detection from a sensor worker.

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

    sensor_id = body.get("sensor_id")
    timestamp = body.get("timestamp")
    species = body.get("species")
    confidence = body.get("confidence")

    if not all([sensor_id, timestamp, species, confidence is not None]):
        return JSON(
            request=request,
            success=False,
            message="Missing required fields: sensor_id, timestamp, species, confidence.",
            status=400,
        ).generate()

    if not isinstance(confidence, (int, float)) or not (0.0 <= float(confidence) <= 1.0):
        return JSON(
            request=request,
            success=False,
            message="Field 'confidence' must be a float between 0.0 and 1.0.",
            status=400,
        ).generate()

    # Resolve text sensor_id -> sensors.id (FK)
    sensor_row = await request.app.ctx.pool.fetchrow(
        "SELECT id FROM sensors WHERE sensor_id = $1",
        sensor_id,
    )
    if sensor_row is None:
        return JSON(
            request=request,
            success=False,
            message=f"Sensor '{sensor_id}' is not registered.",
            status=404,
        ).generate()

    await request.app.ctx.pool.execute(
        """
        INSERT INTO detections (sensor_id, timestamp, species, confidence)
        VALUES ($1, $2, $3, $4)
        """,
        sensor_row["id"],
        timestamp,
        species,
        float(confidence),
    )

    return JSON(
        request=request,
        success=True,
        message="Detection recorded successfully.",
        status=201,
    ).generate()


# GET /detections
@bp.route("/", methods=["GET"])
@openapi.definition(
    summary="List detections",
    description=(
        "Returns a paginated list of bird detections, ordered from most recent to oldest. "
        "Supports filtering by species and sensor ID."
    ),
    tag="Detections",
)
@openapi.response(
    status=200,
    content={"application/json": Detections},
    description="Paginated list of detections.",
)
@openapi.response(
    status=400,
    content={"application/json": BadRequest},
    description="Invalid query parameters.",
)
@openapi.response(
    status=429,
    content={"application/json": RateLimited},
    description="You have sent too many requests. Please try again later.",
)
@openapi.parameter(
    name="limit",
    description="Maximum number of detections to return (1–100, default 50)",
    required=False,
    schema=int,
    location="query",
    example=50,
)
@openapi.parameter(
    name="offset",
    description="Number of detections to skip (default 0)",
    required=False,
    schema=int,
    location="query",
    example=0,
)
@openapi.parameter(
    name="species",
    description="Filter by bird species (scientific name)",
    required=False,
    schema=str,
    location="query",
    example="Turdus merula",
)
@openapi.parameter(
    name="sensor_id",
    description="Filter by sensor ID",
    required=False,
    schema=str,
    location="query",
    example="sensor-001",
)
@inputs(
    Argument(
        name="limit",
        description="Maximum number of detections to return",
        methods={"limit": Rules.integer},
        call=int,
        required=False,
        headers=False,
        allow_multiple=False,
        deprecated=False,
    ),
    Argument(
        name="offset",
        description="Number of detections to skip",
        methods={"offset": Rules.integer},
        call=int,
        required=False,
        headers=False,
        allow_multiple=False,
        deprecated=False,
    ),
    Argument(
        name="species",
        description="Filter by bird species (scientific name)",
        methods={"species": None},
        call=str,
        required=False,
        headers=False,
        allow_multiple=False,
        deprecated=False,
    ),
    Argument(
        name="sensor_id",
        description="Filter by sensor ID",
        methods={"sensor_id": None},
        call=str,
        required=False,
        headers=False,
        allow_multiple=False,
        deprecated=False,
    ),
)
@ratelimit()
async def getDetections(request: Request, limit: int = None, offset: int = None, species: str = None, sensor_id: str = None) -> JSONResponse:
    """
    Returns a paginated list of detections in descending timestamp order.

    :return: JSONResponse
    """
    limit = min(limit or 50, 100)
    offset = offset or 0

    # Build conditions dynamically
    conditions = []
    params = []

    if species:
        params.append(species)
        conditions.append(f"d.species = ${len(params)}")

    if sensor_id:
        params.append(sensor_id)
        conditions.append(f"s.sensor_id = ${len(params)}")

    where_clause = f"WHERE {' AND '.join(conditions)}" if conditions else ""

    count_row = await request.app.ctx.pool.fetchrow(
        f"""
        SELECT COUNT(*) AS total
        FROM detections d
        JOIN sensors s ON d.sensor_id = s.id
        {where_clause}
        """,
        *params,
    )
    total = count_row["total"]

    params_with_pagination = params + [limit, offset]
    rows = await request.app.ctx.pool.fetch(
        f"""
        SELECT d.id, s.sensor_id, d.timestamp, d.species, d.confidence
        FROM detections d
        JOIN sensors s ON d.sensor_id = s.id
        {where_clause}
        ORDER BY d.timestamp DESC
        LIMIT ${len(params_with_pagination) - 1} OFFSET ${len(params_with_pagination)}
        """,
        *params_with_pagination,
    )

    return JSON(
        request=request,
        success=True,
        data={
            "total": total,
            "limit": limit,
            "offset": offset,
            "detections": [
                {
                    "id": row["id"],
                    "sensor_id": row["sensor_id"],
                    "timestamp": row["timestamp"],
                    "species": row["species"],
                    "confidence": row["confidence"],
                }
                for row in rows
            ],
        },
        status=200,
    ).generate()


# GET /detections/<id>
@bp.route("/<id:int>", methods=["GET"])
@openapi.definition(
    summary="Get a detection by ID",
    description="Returns the details of a single detection by its unique identifier.",
    tag="Detections",
)
@openapi.response(
    status=200,
    content={"application/json": Detection},
    description="Detection details.",
)
@openapi.response(
    status=400,
    content={"application/json": BadRequest},
    description="The detection ID must be a positive integer.",
)
@openapi.response(
    status=404,
    content={"application/json": NotFound},
    description="The detection was not found.",
)
@openapi.response(
    status=429,
    content={"application/json": RateLimited},
    description="You have sent too many requests. Please try again later.",
)
@openapi.parameter(
    name="id",
    description="Detection ID",
    required=True,
    schema=int,
    location="path",
    example=1,
)
@inputs(
    Argument(
        name="id",
        description="Detection ID",
        methods={"id": Rules.integer},
        call=int,
        required=True,
        headers=False,
        allow_multiple=False,
        deprecated=False,
    ),
)
@ratelimit()
async def getDetection(request: Request, id: int) -> JSONResponse:
    """
    Returns the details of a single detection.

    :param id: Detection ID
    :return: JSONResponse
    """
    row = await request.app.ctx.pool.fetchrow(
        """
        SELECT d.id, s.sensor_id, d.timestamp, d.species, d.confidence
        FROM detections d
        JOIN sensors s ON d.sensor_id = s.id
        WHERE d.id = $1
        """,
        id,
    )

    if row is None:
        return JSON(
            request=request,
            success=False,
            message="The detection was not found.",
            status=404,
        ).generate()

    return JSON(
        request=request,
        success=True,
        data={
            "id": row["id"],
            "sensor_id": row["sensor_id"],
            "timestamp": row["timestamp"],
            "species": row["species"],
            "confidence": row["confidence"],
        },
        status=200,
    ).generate()
