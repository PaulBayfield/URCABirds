from .ratelimit import ratelimit
from .response import JSON
from exceptions.ratelimit import RatelimitException
from exceptions.forbidden import ForbiddenException
from sanic import Sanic, Request
from sanic.response import JSONResponse
from sanic.exceptions import NotFound, SanicException
from asyncpg.exceptions import ConnectionDoesNotExistError


class ErrorHandler:
    """
    Class to handle errors
    """

    def __init__(self, app: Sanic) -> None:
        """
        Class constructor

        :param app: Sanic
        :type app: Sanic
        """
        self.app = app

        @app.exception(NotFound)
        @ratelimit()
        async def handle_not_found(request: Request, exception: NotFound) -> JSONResponse:
            """
            Handles not found errors

            :param request: Request
            :type request: Request
            :param exception: NotFound
            :type exception: NotFound
            :return: JSONResponse
            :rtype: JSONResponse
            """
            return JSON(
                request=request,
                success=False,
                message="The requested resource does not exist.",
                status=exception.status_code,
            ).generate()

        @app.exception(ForbiddenException)
        async def handle_forbidden(request: Request, exception: ForbiddenException) -> JSONResponse:
            """
            Handles forbidden errors

            :param request: Request
            :type request: Request
            :param exception: ForbiddenException
            :type exception: ForbiddenException
            :return: JSONResponse
            :rtype: JSONResponse
            """
            return JSON(
                request=request,
                success=False,
                message=exception.message,
                status=exception.status_code,
            ).generate()

        @app.exception(RatelimitException)
        async def handle_ratelimit(request: Request, exception: RatelimitException) -> JSONResponse:
            """
            Handles ratelimit errors

            :param request: Request
            :type request: Request
            :param exception: RatelimitException
            :type exception: RatelimitException
            :return: JSONResponse
            :rtype: JSONResponse
            """
            return JSON(
                request=request,
                success=False,
                message=exception.message,
                status=exception.status_code,
            ).generate()

        @app.exception(ConnectionDoesNotExistError, ConnectionRefusedError)
        @ratelimit()
        async def handle_db_connection_error(request: Request, exception: Exception) -> JSONResponse:
            """
            Handles database connection errors

            :param request: Request
            :type request: Request
            :param exception: Exception
            :type exception: Exception
            :return: JSONResponse
            :rtype: JSONResponse
            """
            self.app.ctx.logs.error(
                f"Error: {exception}"
            )

            return JSON(
                request=request,
                success=False,
                message="The service is temporarily unavailable due to database connection problems. Please try again later.",
                status=503,
            ).generate()

        @app.exception(Exception, SanicException)
        @ratelimit()
        async def handle_exception(request: Request, exception: Exception) -> JSONResponse:
            """
            Handles general exceptions

            :param request: Request
            :type request: Request
            :param exception: Exception
            :type exception: Exception
            :return: JSONResponse
            :rtype: JSONResponse
            """
            self.app.ctx.logs.error(f"Error: {exception}")

            return JSON(
                request=request,
                success=False,
                message=exception.message
                if hasattr(exception, "message")
                else "An error occurred while processing your request. We apologize for the inconvenience, our team is on it!",
                status=500,
            ).generate()
