from sanic_ext import openapi


@openapi.component
class Sensor:
    sensor_id = openapi.String(
        description="Unique text identifier of the sensor",
        example="sensor-001",
    )
    name = openapi.String(
        description="Human-readable name of the sensor",
        example="Rooftop sensor A",
    )
    latitude = openapi.Float(
        description="Latitude of the sensor location",
        example=48.8566,
    )
    longitude = openapi.Float(
        description="Longitude of the sensor location",
        example=2.3522,
    )
    description = openapi.String(
        description="Optional description of the sensor",
        example="Mounted on the east side of the rooftop",
    )
    total_detections = openapi.Integer(
        description="Total number of detections recorded by this sensor",
        example=142,
    )
    last_detection = openapi.String(
        description="ISO 8601 UTC timestamp of the most recent detection from this sensor",
        example="2024-01-15T10:30:00+00:00",
    )
    first_registered = openapi.String(
        description="ISO 8601 UTC timestamp of the sensor's first registration",
        example="2024-01-01T00:00:00+00:00",
    )
    last_connection = openapi.String(
        description="ISO 8601 UTC timestamp of the sensor's most recent connection",
        example="2024-01-15T10:30:00+00:00",
    )
