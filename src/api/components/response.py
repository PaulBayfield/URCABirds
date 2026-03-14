from sanic.request import Request
from sanic.response import JSONResponse, json


class Response:
    """
    Class for responses
    """

    def __init__(self, request: Request) -> None:
        """
        Class initialization

        :param request: Request
        :type request: Request
        """
        self.request = request

    def generate(self) -> None:
        """
        Generates the response
        """
        raise NotImplementedError


class JSON(Response):
    """
    Class for JSON responses
    """

    def __init__(
        self,
        request: Request,
        success: bool = True,
        data: dict = None,
        status: int = 200,
        message: str = None,
    ) -> None:
        """
        Class initialization

        :param request: Request
        :type request: Request
        :param data: dict
        :type data: dict
        :param success: bool
        :type success: bool
        :param status: int
        :type status: int
        :param message: str
        :type message: str
        """
        super().__init__(request)
        self.data = data
        self.success = success
        self.status = status
        self.message = message

    def generate(self) -> JSONResponse:
        """
        Generates the response

        :return: JSONResponse
        :rtype: JSONResponse
        """
        if self.data is None and self.message is None:
            return json(
                {
                    "success": self.success,
                    "message": "Something went wrong... Please try again later. If the problem persists, contact us!",
                },
                status=500,
            )

        if self.message:
            return json(
                {"success": self.success, "message": self.message}, status=self.status
            )

        return json({"success": self.success, "data": self.data}, status=self.status)
