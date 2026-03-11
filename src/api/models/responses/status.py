from sanic_ext import openapi


class Status:
    success = openapi.Boolean(
        description="Request status",
        example=True,
    )
    message = openapi.String(
        description="Status message",
        example="The API is online.",
    )
