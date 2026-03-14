from sanic_ext import openapi
from ..components import DetectionComponent


class Detections:
    success = openapi.Boolean(
        description="Request status",
        example=True,
    )
    data = openapi.Array(
        items=DetectionComponent,
        description="List of detections (most recent first)",
    )
    total = openapi.Integer(
        description="Total number of detections matching the query",
        example=487,
    )
    limit = openapi.Integer(
        description="Maximum number of detections returned",
        example=50,
    )
    offset = openapi.Integer(
        description="Number of detections skipped",
        example=0,
    )


class Detection:
    success = openapi.Boolean(
        description="Request status",
        example=True,
    )
    data = DetectionComponent
