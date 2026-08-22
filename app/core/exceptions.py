class NotFoundError(Exception):
    def __init__(self, detail: str):
        self.detail = detail


class ConflictError(Exception):
    def __init__(self, detail: str):
        self.detail = detail


class ValidationError(Exception):
    def __init__(self, detail: str):
        self.detail = detail


class ExternalServiceError(Exception):
    def __init__(self, detail: str):
        self.detail = detail
