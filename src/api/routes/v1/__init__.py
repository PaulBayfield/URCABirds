from .service.v1_service import bp as RouteService
from .detections.v1_detections import bp as RouteDetections
from .sensors.v1_sensors import bp as RouteSensors
from .species.v1_species import bp as RouteSpecies
from .misc.v1_misc import bp as RouteMisc
from .apikeys.v1_apikeys import bp as RouteApiKeys

# Version metadata
__version__ = "1.0.0"
__author__ = "Paul Bayfield (github.com/PaulBayfield)"
__description__ = "/v1 for the URCABirds API"
__routes__ = [
    RouteService,
    RouteDetections,
    RouteSensors,
    RouteSpecies,
    RouteMisc,
    RouteApiKeys,
]


__all__ = ["__version__", "__author__", "__description__", "__routes__"]
