from sanic_ext import openapi
from ..components import SpeciesComponent


class SpeciesList:
    success = openapi.Boolean(
        description="Request status",
        example=True,
    )
    data = openapi.Array(
        items=SpeciesComponent,
        description="List of species",
    )


class SpeciesItem:
    success = openapi.Boolean(
        description="Request status",
        example=True,
    )
    data = SpeciesComponent
