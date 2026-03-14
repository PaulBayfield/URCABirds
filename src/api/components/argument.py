import functools

from .rules import Rules
from .response import JSON
from sanic.request import Request
from sanic.response import HTTPResponse


class Argument:
    """
    Represents an argument for a route.

    This class is used to define and validate the expected arguments
    in an HTTP request, whether in the URL, headers,
    or path parameters.
    """

    def __init__(
        self,
        name: str,
        description: str,
        methods: dict[str, Rules],
        call: callable = None,
        required: bool = True,
        headers: bool = False,
        allow_multiple: bool = False,
        deprecated: bool = False,
    ):
        """
        Initialises a new argument for a route.

        :param name: Name of the expected variable.
        :type name: str
        :param description: Description of the parameter.
        :type description: str
        :param methods: Dictionary of rules to apply {key: rule}.
        :type methods: dict[str, Rules]
        :param call: Transformation function to apply to the value (e.g., int, str).
        :type call: callable
        :param required: Indicates if the parameter is required.
        :type required: bool
        :param headers: If True, the search is done in the headers.
        :type headers: bool
        :param allow_multiple: Allows multiple values for a single parameter.
        :type allow_multiple: bool
        :param deprecated: Marks the parameter as deprecated.
        :type deprecated: bool
        """
        self.name = name
        self.description = description
        self.methods = methods
        self.call = call
        self.required = required
        self.headers = headers
        self.allow_multiple = allow_multiple
        self.deprecated = deprecated


def inputs(*args: Argument) -> callable:
    """
    Decorator to apply validation on the arguments of a route.

    This decorator adds parameter validation to a route function
    provided via the URL, headers, or path variables.

    :param args: List of Argument objects to validate.
    :type args: Argument
    :return: The decorated function with the validation logic.
    :rtype: callable
    """

    def wrapper(func: callable) -> callable:
        """
        Internal decorator applying the checks.

        :param func: The route function to decorate.
        :type func: callable
        :return: The function enriched with validation.
        :rtype: callable
        """

        @functools.wraps(func)
        async def wrapped(request: Request, **kwargs) -> HTTPResponse:
            """
            Function executed on each call of the route.

            :param request: The object representing the HTTP request.
            :type request: Request
            :param kwargs: The path parameters passed to the function.
            :type kwargs: dict
            :return: An HTTP response with or without error.
            :rtype: HTTPResponse
            """

            def input_handler(argument: Argument) -> HTTPResponse | None:
                """
                Handles the validation of a specific argument.

                :param argument: The argument to process.
                :type argument: Argument
                :return: An HTTP error response in case of invalidity, otherwise None.
                :rtype: HTTPResponse | None
                """
                nonlocal finished_kwargs

                # Choice of input source
                if argument.headers:
                    requests_inputs = dict(request.headers)
                else:
                    requests_inputs = dict(request.args)

                    # If not found in query params, look in path params
                    if argument.name not in requests_inputs and argument.name in kwargs:
                        requests_inputs[argument.name] = kwargs[argument.name]

                for input_name, input_rule in argument.methods.items():
                    if input_value := requests_inputs.get(input_name, None):
                        # Handle multiple values
                        if not argument.allow_multiple and isinstance(
                            input_value, (list, tuple)
                        ):
                            if len(input_value) > 1:
                                return JSON(
                                    request=request,
                                    success=False,
                                    message=(
                                        f"Invalid input for '{argument.name}'. "
                                        f"Only one value expected, multiple values received."
                                    ),
                                    status=400,
                                ).generate()
                            else:
                                input_value = input_value[0]

                        # Application of the rule
                        if callable(input_rule):
                            if input_rule(input_value):
                                finished_kwargs[argument.name] = (
                                    argument.call(input_value)
                                    if argument.call
                                    else input_value
                                )
                                break
                            else:
                                return JSON(
                                    request=request,
                                    success=False,
                                    message=(
                                        f"Invalid input for '{argument.name}'. "
                                        f"Expected: '{input_rule.__name__}', received: '{input_value}'. "
                                        f"Info: {input_rule.__doc__.strip()}"
                                    ),
                                    status=400,
                                ).generate()
                        else:
                            finished_kwargs[argument.name] = (
                                argument.call(input_value)
                                if argument.call
                                else input_value
                            )
                            break
                else:
                    if argument.required:
                        return JSON(
                            request=request,
                            success=False,
                            message=f"Missing required parameter: '{argument.name}'.",
                            status=400,
                        ).generate()
                    finished_kwargs[argument.name] = None

            finished_kwargs = kwargs.copy()

            for arg in args:
                if not isinstance(arg, Argument):
                    raise TypeError(
                        "All arguments must be of type Argument!"
                    )

                override_exit = input_handler(argument=arg)
                if override_exit:
                    return override_exit

            return await func(request=request, **finished_kwargs)

        return wrapped

    return wrapper
