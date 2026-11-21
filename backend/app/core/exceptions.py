from fastapi import HTTPException, status

class CustomHTTPException(HTTPException):
    def __init__(self, status_code: int, detail: str):
        super().__init__(status_code=status_code, detail=detail)

class DatabaseTransactionError(CustomHTTPException):
    def __init__(self, detail: str = "Error en la transacción de la base de datos"):
        super().__init__(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=detail)

class ValidationError(CustomHTTPException):
    def __init__(self, detail: str = "Error de validación en los datos proporcionados"):
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)

class NotFoundError(CustomHTTPException):
    def __init__(self, detail: str = "Recurso no encontrado"):
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail=detail)

class UnauthorizedError(CustomHTTPException):
    def __init__(self, detail: str = "Credenciales o permisos inválidos"):
        super().__init__(status_code=status.HTTP_401_UNAUTHORIZED, detail=detail)

class ForbiddenError(CustomHTTPException):
    def __init__(self, detail: str = "No tienes permiso para realizar esta acción."):
        super().__init__(status_code=status.HTTP_403_FORBIDDEN, detail=detail)

class FileTooLargeError(CustomHTTPException):
    def __init__(self, detail: str = "El archivo supera el tamaño máximo permitido."):
        super().__init__(status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, detail=detail)
