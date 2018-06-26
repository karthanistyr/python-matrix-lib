import traceback

def format_exception(exception):
    """Formats an exception's trace for printing"""
    return "".join(
        traceback.format_exception(
            etype=exception.__class__,
            value=exception,
            tb=exception.__traceback__
            )
        )

class ApplicationError(Exception):
    """General application failure"""
    def __init__(self, message):
        super().__init__(message)

class ClientError(Exception):
    """Speclialised exception class for all errors thrown when using
    the Client class"""
    def __init__(self, message):
        super().__init__(message)

class ArgumentValidationError(Exception):
    """Exception raised when an error occurs while validating the endpoint
    arguments"""

    def __init__(self, message, argument_name):
        super().__init__(message)
        self.argument_name = argument_name

class DatasourceError(Exception):
    """Speclialised exception class for all errors thrown when using
    the Client class"""

    def __init__(self, message):
        super().__init__(message)
