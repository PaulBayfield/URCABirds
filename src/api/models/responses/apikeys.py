from sanic_ext import openapi


class ApiKeyItem:
    id = openapi.Integer(
        description="API key unique ID",
        example=1,
    )
    name = openapi.String(
        description="API key label",
        example="Rooftop sensor A",
    )
    created_at = openapi.String(
        description="ISO 8601 creation timestamp",
        example="2024-01-15T10:30:00+00:00",
    )


class ApiKeys:
    success = openapi.Boolean(
        description="Request status",
        example=True,
    )
    data = openapi.Array(
        items=ApiKeyItem,
        description="List of API keys (key value hidden)",
    )


class ApiKeyCreated:
    success = openapi.Boolean(
        description="Request status",
        example=True,
    )
    data = ApiKeyItem


class ApiKeyDeleted:
    success = openapi.Boolean(
        description="Request status",
        example=True,
    )
    message = openapi.String(
        description="Confirmation message",
        example="API key deleted successfully.",
    )
