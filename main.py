from fastapi import FastAPI
from api.endpoints import chat
# YENİ İMPORTLAR
from exceptions.custom_exceptions import CustomAPIException
from exceptions.exception_handlers import custom_api_exception_handler, generic_exception_handler

app = FastAPI(
    title="LLM Orkestratör Projesi",
    description="Cohere AI ve araçları kullanarak çalışan bir FastAPI sunucusu.",
    version="1.0.0"
)

# YENİ HATA YÖNETİCİLERİNİ UYGULAMAYA EKLEME
app.add_exception_handler(CustomAPIException, custom_api_exception_handler)
app.add_exception_handler(Exception, generic_exception_handler) # Bunu en sona ekleyin

app.include_router(chat.router, prefix="/api", tags=["chat"])

@app.get("/", tags=["root"])
async def read_root():
    return {"message": "LLM Orkestratör API'sine hoş geldiniz! Test için /docs adresine gidin."}