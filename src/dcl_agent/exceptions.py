class DCLConfigurationError(Exception):
    """Base class for fatal configuration errors in DCL Agent."""
    pass

class InvalidAliasError(DCLConfigurationError):
    """Raised when an alias points to a non-existent resource."""
    pass

class DCLConfigurationWarning(Warning):
    """Base class for non-fatal configuration warnings.
    These are typically caught by the Loader to implement fallback or precedence strategies.
    """
    pass

class AliasAlreadyExistsWarning(DCLConfigurationWarning):
    """
    Raised when attempting to register an alias that already exists.
    Caught by Loader to implement 'First-Wins' strategy.
    """
    pass

class DuplicateIdWarning(DCLConfigurationWarning):
    """
    Raised when attempting to register a resource with an ID that already exists.
    Caught by Loader to implement 'First-Wins' strategy.
    """
    pass
