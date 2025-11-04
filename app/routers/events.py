from fastapi import APIRouter, Body, Response, status, HTTPException, Query
from pymongo import ReturnDocument
from typing import List, Annotated, Optional
from uuid import UUID, uuid4
from datetime import datetime

from ..models.event_models import EventCreate,EventInDB
from .. import database

# Router que agrupará todos los endpoints de eventos.
router = APIRouter(
    prefix="/events",
    tags=["Eventos"]
)

# --- Endpoints ---

# 1. POST /events : Crear un nuevo evento
@router.post(
    "/",
    response_model=EventInDB,
    status_code=status.HTTP_201_CREATED,
    response_description="Añadir nuevo evento",
)
async def create_event(
    event: Annotated[EventCreate, Body(
        examples=[{
            "idCalendario": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
            "titulo": "Concierto de Verano",
            "horaComienzo": "2025-08-15T21:30:00",
            "duracionMinutos": 150,
            "lugar": "Parque de la Ciudad",
            "organizador": "Concejalía de Cultura",
            "contenidoAdjunto": {
                "imagenes": [
                    "https://ejemplo.com/concierto.jpg",
                    "https://ejemplo.com/cartel.jpg"
                ],
                "archivos": [
                    "https://ejemplo.com/programa.pdf"
                ],
                "mapa": {
                    "latitud": 36.7188,
                    "longitud": -4.4332
                }
            }
        }]
    )]
):
    """
    Crea un nuevo evento en la base de datos.
    """
    event_dict = event.model_dump(by_alias=True)
    event_dict["_id"] = uuid4()
    new_event = database.eventos_collection.insert_one(event_dict)
    created_event = database.eventos_collection.find_one({"_id": new_event.inserted_id})
    return created_event

# 2. GET /events : Obtener una lista de todos los eventos (con filtros opcionales)
@router.get(
    "/",
    response_model=List[EventInDB],
    response_description="Listar todos los eventos con filtros opcionales",
)
async def list_events(
    fecha_inicio: Optional[datetime] = Query(
        None, 
        description="Fecha de inicio del rango (formato ISO: YYYY-MM-DDTHH:MM:SS)",
        example="2025-01-01T00:00:00"
    ),
    fecha_fin: Optional[datetime] = Query(
        None, 
        description="Fecha de fin del rango (formato ISO: YYYY-MM-DDTHH:MM:SS)",
        example="2025-12-31T23:59:59"
    ),
    lugar: Optional[str] = Query(None, description="Filtrar por lugar"),
    organizador: Optional[str] = Query(None, description="Filtrar por organizador"),
    titulo: Optional[str] = Query(None, description="Filtrar por título"),
    duration_minima: Optional[int] = Query(None, description="Filtrar por duración minima en minutos"),
    duration_maxima: Optional[int] = Query(None, description="Filtrar por duración maxima en minutos"),
):
    """
    Devuelve una lista de eventos filtrados por rango de fechas.
    
    - **fecha_inicio**: Filtra eventos que comiencen a partir de esta fecha (inclusive)
    - **fecha_fin**: Filtra eventos que comiencen hasta esta fecha (inclusive)
    - **lugar**: Filtra eventos que contengan este texto en el lugar (case insensitive)
    - **organizador**: Filtra eventos que contengan este texto en el organizador
    - **titulo**: Filtra eventos que contengan este texto en el título
    - **duration_minima**: Filtra eventos con duración mínima en minutos
    - **duration_maxima**: Filtra eventos con duración máxima en minutos
    
    Si no se proporciona ningún filtro, devuelve todos los eventos.
    """
    # Construir el filtro de MongoDB
    filtro = {}
    
    # Filtro de fechas
    if fecha_inicio or fecha_fin:
        filtro["horaComienzo"] = {}
        
        if fecha_inicio:
            filtro["horaComienzo"]["$gte"] = fecha_inicio
        
        if fecha_fin:
            filtro["horaComienzo"]["$lte"] = fecha_fin
    
    if lugar:
        filtro["lugar"] = {"$regex": lugar, "$options": "i"}
    
    if organizador:
        filtro["organizador"] = {"$regex": organizador, "$options": "i"}
    
    if titulo:
        filtro["titulo"] = {"$regex": titulo, "$options": "i"}
    
    if duration_minima or duration_maxima:
        filtro["duracionMinutos"] = {}

        if duration_minima:
            filtro["duracionMinutos"]["$gte"] = duration_minima

        if duration_maxima:
            filtro["duracionMinutos"]["$lte"] = duration_maxima

    return list(database.eventos_collection.find(filtro))

# 3. GET /events/{id} : Obtener un evento específico por su ID
@router.get(
    "/{id}",
    response_model=EventInDB,
    response_description="Obtener un evento por su ID",
)
async def get_event(id: UUID):
    """
    Busca un evento por su ID. Devuelve 404 si no lo encuentra.
    """
    event = database.eventos_collection.find_one({"_id": id})
    if event:
        return event

    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Evento con ID {id} no encontrado")

# 4. PUT /events/{id} : Actualizar un evento existente
@router.put(
    "/{id}",
    response_model=EventInDB,
    response_description="Actualizar un calendario por su ID",
)
async def update_event(
    id: UUID, 
    event_update: Annotated[EventCreate, Body(...)]
):
    """
    Actualiza un evento existente. Devuelve 404 si no lo encuentra.
    """
    updated_event = database.eventos_collection.find_one_and_update(
        {"_id": id},
        {"$set": event_update.model_dump(by_alias=True, exclude_unset=True)},
        return_document=ReturnDocument.AFTER
    )

    if event_update:
        return event_update

    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"No se pudo actualizar, evento con ID {id} no encontrado")

# 5. DELETE /events/{id} : Eliminar un evento
@router.delete(
    "/{id}",
    status_code=status.HTTP_204_NO_CONTENT,
    response_description="Eliminar un evento por su ID",
)
async def delete_event(id: UUID):
    """
    Elimina un evento por su ID. Devuelve 204 si tiene éxito o 404 si no lo encuentra.
    """
    delete_result = database.eventos_collection.delete_one({"_id": id})

    if delete_result.deleted_count == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Evento con ID {id} no encontrado")

    return Response(status_code=status.HTTP_204_NO_CONTENT)
