from sanic_ext import openapi


@openapi.component
class Species:
    name = openapi.String(
        description="Scientific name of the bird species",
        example="Turdus merula",
    )
    total_detections = openapi.Integer(
        description="Total number of detections recorded for this species",
        example=57,
    )
    last_detection = openapi.String(
        description="ISO 8601 UTC timestamp of the most recent detection of this species",
        example="2024-01-15T10:30:00+00:00",
    )
