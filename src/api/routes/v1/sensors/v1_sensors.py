from components.ratelimit import ratelimit
from components.response import JSON
from components.argument import Argument, inputs
from components.auth import require_api_key
from models.responses import Sensors, Sensor
from models.exceptions import RateLimited, NotFound, Unauthorized
from sanic.response import JSONResponse
from sanic import Blueprint, Request
from sanic_ext import openapi


bp = Blueprint(name="Sensors", url_prefix="/sensors", version=1, version_prefix="v")


# POST /sensors/register
@bp.route("/register", methods=["POST"])
@openapi.definition(
    summary="Register or update a sensor",
    description=(
        "Registers a new sensor or updates an existing one (by sensor_id). "
        "Updates `last_connection` on every call. "
        "Requires a valid `Authorization: Bearer <API_KEY>` header."
    ),
    tag="Sensors",
)
@openapi.body(
    content={
        "application/json": {
            "schema": {
                "type": "object",
                "required": ["sensor_id", "latitude", "longitude"],
                "properties": {
                    "sensor_id": {"type": "string", "example": "sensor-001"},
                    "name": {"type": "string", "example": "Rooftop sensor A"},
                    "latitude": {
                        "type": "number",
                        "format": "double",
                        "example": 48.8566,
                    },
                    "longitude": {
                        "type": "number",
                        "format": "double",
                        "example": 2.3522,
                    },
                    "description": {
                        "type": "string",
                        "example": "East side rooftop mount",
                    },
                },
            }
        }
    },
    required=True,
    description="Sensor registration payload.",
)
@openapi.response(
    status=200,
    content={"application/json": Sensor},
    description="Sensor updated (already existed).",
)
@openapi.response(
    status=201,
    content={"application/json": Sensor},
    description="Sensor registered for the first time.",
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
@require_api_key
@ratelimit()
async def registerSensor(request: Request) -> JSONResponse:
    """
    Upserts a sensor record. On first registration sets first_registered;
    on subsequent calls updates last_connection (and lat/lon/name).

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

    sensor_id = body.get("sensor_id", "").strip()
    latitude = body.get("latitude")
    longitude = body.get("longitude")
    name = body.get("name", sensor_id).strip() or sensor_id
    description = body.get("description")

    if not sensor_id:
        return JSON(
            request=request,
            success=False,
            message="Missing required field: sensor_id.",
            status=400,
        ).generate()
    if latitude is None or longitude is None:
        return JSON(
            request=request,
            success=False,
            message="Missing required fields: latitude, longitude.",
            status=400,
        ).generate()
    if not isinstance(latitude, (int, float)) or not isinstance(
        longitude, (int, float)
    ):
        return JSON(
            request=request,
            success=False,
            message="latitude and longitude must be numbers.",
            status=400,
        ).generate()

    # Determine if this is a first registration or an update
    existing = await request.app.ctx.pool.fetchrow(
        "SELECT id FROM sensors WHERE sensor_id = $1", sensor_id
    )

    row = await request.app.ctx.pool.fetchrow(
        """
        INSERT INTO sensors (sensor_id, name, latitude, longitude, description, api_key_id,
                             first_registered, last_connection)
        VALUES ($1, $2, $3, $4, $5, $6, NOW(), NOW())
        ON CONFLICT (sensor_id) DO UPDATE
            SET name            = EXCLUDED.name,
                latitude        = EXCLUDED.latitude,
                longitude       = EXCLUDED.longitude,
                description     = EXCLUDED.description,
                last_connection = NOW()
        RETURNING sensor_id, name, latitude, longitude, description, first_registered, last_connection
        """,
        sensor_id,
        name,
        float(latitude),
        float(longitude),
        description,
        request.ctx.api_key_id,
    )

    status = 200 if existing else 201
    return JSON(
        request=request,
        success=True,
        message="Sensor registered successfully."
        if status == 201
        else "Sensor updated successfully.",
        data={
            "sensor_id": row["sensor_id"],
            "name": row["name"],
            "latitude": row["latitude"],
            "longitude": row["longitude"],
            "description": row["description"],
            "first_registered": row["first_registered"].isoformat()
            if row["first_registered"]
            else None,
            "last_connection": row["last_connection"].isoformat()
            if row["last_connection"]
            else None,
        },
        status=status,
    ).generate()


# GET /sensors
@bp.route("/", methods=["GET"])
@openapi.definition(
    summary="List all sensors",
    description="Returns all registered sensors along with their metadata and detection statistics.",
    tag="Sensors",
)
@openapi.response(
    status=200,
    content={"application/json": Sensors},
    description="List of sensors.",
)
@openapi.response(
    status=429,
    content={"application/json": RateLimited},
    description="You have sent too many requests. Please try again later.",
)
@ratelimit()
async def getSensors(request: Request) -> JSONResponse:
    """
    Returns all registered sensors with their metadata and detection counts.

    :return: JSONResponse
    """
    rows = await request.app.ctx.pool.fetch(
        """
        SELECT
            s.sensor_id,
            s.name,
            s.latitude,
            s.longitude,
            s.description,
            s.first_registered,
            s.last_connection,
            COUNT(d.id)       AS total_detections,
            MAX(d.timestamp)  AS last_detection
        FROM sensors s
        LEFT JOIN detections d ON d.sensor_id = s.id
        GROUP BY s.id
        ORDER BY total_detections DESC
        """
    )

    return JSON(
        request=request,
        success=True,
        data=[
            {
                "sensor_id": row["sensor_id"],
                "name": row["name"],
                "latitude": row["latitude"],
                "longitude": row["longitude"],
                "description": row["description"],
                "first_registered": row["first_registered"].isoformat()
                if row["first_registered"]
                else None,
                "last_connection": row["last_connection"].isoformat()
                if row["last_connection"]
                else None,
                "total_detections": row["total_detections"],
                "last_detection": row["last_detection"],
            }
            for row in rows
        ],
        status=200,
    ).generate()


# GET /sensors/<sensor_id>
@bp.route("/<sensor_id:str>", methods=["GET"])
@openapi.definition(
    summary="Get a sensor by ID",
    description="Returns the metadata and statistics for a single sensor.",
    tag="Sensors",
)
@openapi.response(
    status=200,
    content={"application/json": Sensor},
    description="Sensor details.",
)
@openapi.response(
    status=404,
    content={"application/json": NotFound},
    description="The sensor was not found.",
)
@openapi.response(
    status=429,
    content={"application/json": RateLimited},
    description="You have sent too many requests. Please try again later.",
)
@openapi.parameter(
    name="sensor_id",
    description="Sensor ID",
    required=True,
    schema=str,
    location="path",
    example="sensor-001",
)
@inputs(
    Argument(
        name="sensor_id",
        description="Sensor ID",
        methods={"sensor_id": None},
        call=str,
        required=True,
        headers=False,
        allow_multiple=False,
        deprecated=False,
    ),
)
@ratelimit()
async def getSensor(request: Request, sensor_id: str) -> JSONResponse:
    """
    Returns the metadata and detection statistics of a single sensor.

    :param sensor_id: Sensor ID
    :return: JSONResponse
    """
    row = await request.app.ctx.pool.fetchrow(
        """
        SELECT
            s.sensor_id,
            s.name,
            s.latitude,
            s.longitude,
            s.description,
            s.first_registered,
            s.last_connection,
            COUNT(d.id)       AS total_detections,
            MAX(d.timestamp)  AS last_detection
        FROM sensors s
        LEFT JOIN detections d ON d.sensor_id = s.id
        WHERE s.sensor_id = $1
        GROUP BY s.id
        """,
        sensor_id,
    )

    if row is None:
        return JSON(
            request=request,
            success=False,
            message="The sensor was not found.",
            status=404,
        ).generate()

    return JSON(
        request=request,
        success=True,
        data={
            "sensor_id": row["sensor_id"],
            "name": row["name"],
            "latitude": row["latitude"],
            "longitude": row["longitude"],
            "description": row["description"],
            "first_registered": row["first_registered"].isoformat()
            if row["first_registered"]
            else None,
            "last_connection": row["last_connection"].isoformat()
            if row["last_connection"]
            else None,
            "total_detections": row["total_detections"],
            "last_detection": row["last_detection"],
        },
        status=200,
    ).generate()
