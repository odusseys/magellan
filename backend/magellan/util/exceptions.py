class APIError(Exception):
    def __init__(self, message: str, status_code: int, error_code: str = None):
        super(APIError, self).__init__(message)
        self.message = message
        self.status_code = status_code
        self.error_code = error_code


class BadRequest(APIError):
    def __init__(self, message: str, error_code: str = None):
        super(BadRequest, self).__init__(message, 400, error_code)


class Unauthorized(APIError):
    def __init__(self, error_code: str = None):
        super(Unauthorized, self).__init__(
            "Unauthorized", 401, error_code)


class Forbidden(APIError):
    def __init__(self, error_code: str = None):
        super(Forbidden, self).__init__("Forbidden", 403, error_code)


class NotFound(APIError):
    def __init__(self, error_code: str = None):
        super(NotFound, self).__init__("Conflict", 404, error_code)


class Conflict(APIError):
    def __init__(self, error_code: str = None):
        super(Conflict, self).__init__("Conflict", 409, error_code)
