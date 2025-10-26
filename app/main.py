from fastapi import FastAPI
from .routers import calendars # Importamos nuestro nuevo router


app = FastAPI(
    title="API de Kalendas",
    description="API para la gestión de calendarios y eventos.",
    version="1.0.0"
)

# Incluimos el router de calendarios en la aplicación principal.
app.include_router(calendars.router)

@app.get("/")
async def root():
    return {"message": "Bienvenido a la API de Kalendas. Visita /docs para ver la documentación."}
