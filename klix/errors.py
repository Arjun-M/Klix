class KlixError(Exception):
    """Base exception class for Klix."""
    pass

class CommandNotFoundError(KlixError):
    pass

class ArgValidationError(KlixError):
    def __init__(self, field: str, message: str):
        self.field = field
        self.message = message
        super().__init__(f"Validation failed for field '{field}': {message}")

class InputCancelledError(KlixError):
    pass

class SessionStateError(KlixError):
    pass

class MiddlewareAbortError(KlixError):
    pass

class RenderError(KlixError):
    pass

class CompatibilityError(KlixError):
    pass
