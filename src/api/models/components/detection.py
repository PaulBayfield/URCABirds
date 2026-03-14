from sanic_ext import openapi


@openapi.component
class Detection:
    id = openapi.Integer(
        description="Unique identifier of the detection",
        example=1,
    )
    sensor_id = openapi.String(
        description="Identifier of the sensor that captured the detection",
        example="sensor-001",
    )
    timestamp = openapi.String(
        description="ISO 8601 UTC timestamp of the detection",
        example="2024-01-15T10:30:00+00:00",
    )
    species = openapi.String(
        description="Scientific name of the detected bird species",
        example="Turdus merula",
    )
    confidence = openapi.Float(
        description="Confidence score of the detection (0.0 to 1.0)",
        example=0.87,
    )
