from fastapi import APIRouter, Body, Response, status, HTTPException, Query
from pymongo import ReturnDocument
from typing import List, Annotated, Optional
from uuid import UUID, uuid4

from ..models.calendar_models import CalendarCreate, CalendarInDB
from .. import database

# Router que agrupará todos los endpoints de calendarios.
router = APIRouter(
    prefix="/calendars",
    tags=["Calendarios"]
)

# --- Endpoints ---

# 1. POST /calendars : Crear un nuevo calendario
@router.post(
    "/",
    response_model=CalendarInDB,
    status_code=status.HTTP_201_CREATED,
    response_description="Añadir nuevo calendario",
)
async def create_calendar(
    calendar: Annotated[CalendarCreate, Body(
        examples=[{
            "titulo": "Actividades Deportivas UMA",
            "organizador": "Universidad de Málaga",
            "palabras_clave": ["deporte", "universidad"],
            "es_publico": True,
            "idCalendarioPadre": None,
        }]
    )]
):
    """
    Crea un nuevo calendario en la base de datos.
    """
    calendar_dict = calendar.model_dump(by_alias=True)
    calendar_dict["_id"] = uuid4()
    new_calendar = database.calendarios_collection.insert_one(calendar_dict)
    created_calendar = database.calendarios_collection.find_one({"_id": new_calendar.inserted_id})
    return created_calendar


# 2. GET /calendars : Obtener una lista de todos los calendarios
@router.get(
    "/",
    response_model=List[CalendarInDB],
    response_description="Listar todos los calendarios",
)
async def list_calendars(
    titulo: Optional[str] = Query(None, description="Filtrar por título"),
    organizador: Optional[str] = Query(None, description="Filtrar por organizador"),
    palabras_clave: Optional[List[str]] = Query(None, description="Filtrar por palabras clave"),
    es_publico: Optional[bool] = Query(None, description="Filtrar por visibilidad pública"),
):
    """
    Devuelve una lista de todos los calendarios en la base de datos.
    """
    filtro = {}

    if titulo:
        filtro["titulo"] = {"$regex": titulo, "$options": "i"}

    if organizador:
        filtro["organizador"] = {"$regex": organizador, "$options": "i"}

    if palabras_clave:
        filtro["palabras_clave"] = {"$in": palabras_clave}

    if es_publico is not None:
        filtro["es_publico"] = es_publico

    return list(database.calendarios_collection.find(filtro))


# 3. GET /calendars/{id} : Obtener un calendario específico por su ID
@router.get(
    "/{id}",
    response_model=CalendarInDB,
    response_description="Obtener un calendario por su ID",
)
async def get_calendar(id: UUID):
    """
    Busca un calendario por su ID. Devuelve 404 si no lo encuentra.
    """
    calendar = database.calendarios_collection.find_one({"_id": id})
    if calendar:
        return calendar

    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Calendario con ID {id} no encontrado")


# 4. PUT /calendars/{id} : Actualizar un calendario existente
@router.put(
    "/{id}",
    response_model=CalendarInDB,
    response_description="Actualizar un calendario por su ID",
)
async def update_calendar(
    id: UUID, 
    calendar_update: Annotated[CalendarCreate, Body(...)]
):
    """
    Actualiza un calendario existente. Devuelve 404 si no lo encuentra.
    """
    updated_calendar = database.calendarios_collection.find_one_and_update(
        {"_id": id},
        {"$set": calendar_update.model_dump(by_alias=True, exclude_unset=True)},
        return_document=ReturnDocument.AFTER
    )

    if updated_calendar:
        return updated_calendar

    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"No se pudo actualizar, calendario con ID {id} no encontrado")


# 5. DELETE /calendars/{id} : Eliminar un calendario
@router.delete(
    "/{id}",
    status_code=status.HTTP_204_NO_CONTENT,
    response_description="Eliminar un calendario por su ID",
)
async def delete_calendar(id: UUID):
    """
    Elimina un calendario por su ID. Devuelve 204 si tiene éxito o 404 si no lo encuentra.
    """
    delete_result = database.calendarios_collection.delete_one({"_id": id})

    if delete_result.deleted_count == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Calendario con ID {id} no encontrado")

    return Response(status_code=status.HTTP_204_NO_CONTENT)