"""Exceptions of the PPP modules."""

class ClientError(Exception):
    """Exception raised by the module for showing an error to the
    client."""
    pass

class BadGateway(Exception):
    """Exception raised by the router when an error from a called
    module has been detected."""
    pass

class InvalidConfig(Exception):
    """Exception raised when there is an error in the config."""
    pass
