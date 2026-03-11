from sanic_ext import openapi


class Unauthorized:
    success = openapi.Boolean(
        description="Request status",
        example=False,
    )
    message = openapi.String(
        description="Error message",
        example="The requested resource requires valid authentication.",
    )
