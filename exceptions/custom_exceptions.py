from starlette import status

# Tüm özel hatalarımızın miras alacağı bir ana sınıf oluşturuyoruz.
class CustomAPIException(Exception):
    def __init__(
        self,
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail: str = "Sunucuda beklenmedik bir hata oluştu.",
    ):
        self.status_code = status_code
        self.detail = detail
        super().__init__(self.detail)

# Dış servislere (GitHub, Swagger URL) bağlanırken oluşacak hatalar için.
class ServiceConnectionError(CustomAPIException):
    def __init__(self, service_name: str, original_error: str):
        super().__init__(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"'{service_name}' servisine bağlanırken bir hata oluştu: {original_error}",
        )

# Bir aracın çalışması sırasında mantıksal bir hata oluşursa.
class ToolExecutionError(CustomAPIException):
    def __init__(self, tool_name: str, reason: str):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"'{tool_name}' aracı çalıştırılırken hata: {reason}",
        )