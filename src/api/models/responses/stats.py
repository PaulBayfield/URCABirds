from sanic_ext import openapi


class Stats:
    success = openapi.Boolean(
        description="Request status",
        example=True,
    )

    class Data:
        total_detections = openapi.Integer(
            description="Total number of detections recorded",
            example=1243,
        )
        total_sensors = openapi.Integer(
            description="Total number of distinct sensors",
            example=5,
        )
        total_species = openapi.Integer(
            description="Total number of distinct species observed",
            example=34,
        )

    data = Data
