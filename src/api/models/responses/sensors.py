from sanic_ext import openapi
from ..components import SensorComponent


class Sensors:
    success = openapi.Boolean(
        description="Request status",
        example=True,
    )
    data = openapi.Array(
        items=SensorComponent,
        description="List of sensors",
    )


class Sensor:
    success = openapi.Boolean(
        description="Request status",
        example=True,
    )
    data = SensorComponent
