from fastapi import Request
from fastapi.responses import JSONResponse
from .custom_exceptions import CustomAPIException

# CustomAPIException veya ondan türeyen bir hata yakalandığında bu fonksiyon çalışır.
async def custom_api_exception_handler(request: Request, exc: CustomAPIException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    )

# Beklenmedik, bizim tanımlamadığımız bir hata oluşursa bu fonksiyon çalışır.
# Bu, sunucunun çökmesini engeller ve kullanıcıya yine de anlamlı bir mesaj verir.
async def generic_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"detail": f"Sunucuda beklenmedik bir sistem hatası oluştu: {type(exc).__name__}"},
    )