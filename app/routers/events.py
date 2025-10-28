from fastapi import APIRouter, Body, Response, status, HTTPException
from pymongo import ReturnDocument
from typing import List, Annotated
from uuid import UUID, uuid4

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

# 2. GET /events : Obtener una lista de todos los eventos
@router.get(
    "/",
    response_model=List[EventInDB],
    response_description="Listar todos los eventos",
)
async def list_events():
    """
    Devuelve una lista de todos los calendarios en la base de datos.
    """
    return list(database.eventos_collection.find({}))

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
