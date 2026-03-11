import time

from sanic import Sanic, Request
from uuid import uuid1


class Middleware:
    """
    Class for middlewares
    """

    def __init__(self, app: Sanic) -> None:
        """
        Class initialization

        :param app: Sanic
        :type app: Sanic
        """

        @app.on_request(priority=999)
        async def before_request(request: Request):
            """
            Middleware to track incoming requests

            :param request: Request
            :type request: Request
            """
            request.ctx.request_id = str(uuid1())
            request.ctx.process_time_start = time.perf_counter()

        @app.on_response
        async def after_request(request: Request, response):
            """
            Middleware to track responses

            :param request: Request
            :type request: Request
            :param response: Response
            :type response: Response
            """
            request.ctx.process_time_end = time.perf_counter()

            # In very rare cases, the processing time might not be set
            # (e.g., if the request fails before reaching the response middleware)
            # In this case, we set the processing time to -999 to indicate an error and highlight the issue
            if hasattr(request.ctx, "process_time_start"):
                request.ctx.process_time = int(
                    (request.ctx.process_time_end - request.ctx.process_time_start)
                    * 1000
                )
            else:
                app.ctx.logs.warning(
                    f"Processing time is not set for request {request.ctx.request_id} ({request.method} {request.path})"
                )

                request.ctx.process_time = -999

            response.headers["X-Request-ID"] = request.ctx.request_id
            response.headers["X-Processing-Time"] = f"{request.ctx.process_time}ms"
            response.headers["X-API"] = "URCABirdsAPI"
            response.headers["X-API-Version"] = f"v{app.config.API_VERSION}"
            response.headers["Content-Language"] = "en-US"
