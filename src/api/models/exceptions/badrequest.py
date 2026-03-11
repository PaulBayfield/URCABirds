from sanic_ext import openapi


class BadRequest:
    success = openapi.Boolean(
        description="Request status",
        example=False,
    )
    message = openapi.String(
        description="Error message",
        example="The request is invalid.",
    )
