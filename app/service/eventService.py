from typing import List, Optional
from uuid import UUID, uuid4
from datetime import datetime

# Importaciones de tu proyecto
from ..models.event_models import EventCreate, EventInDB
from ..crud.event_crud import EventCRUD # Usamos el CRUD inyectado

class EventService:
    """
    Capa de Servicio para Eventos. Maneja la lógica de negocio.
    """
    def __init__(self, crud_repository: EventCRUD):
        """Inyección de Dependencia del CRUD/Repository."""
        self.crud = crud_repository

    
    async def create_event(self, event: EventCreate) -> EventInDB:
        """
        Lógica: Asigna el ID (UUID) y llama al CRUD para la inserción.
        """
        event_dict = event.model_dump(by_alias=True)
        event_dict["_id"] = uuid4() 
        
        # Aquí se podría poner lógica de negocio avanzada (ej. notificaciones, validaciones cruzadas)
        
        return await self.crud.create(event_dict)


    async def get_event_by_id(self, event_id: UUID) -> Optional[EventInDB]:
        """Obtiene un evento por ID."""
        return await self.crud.get_by_id(event_id)


    async def list_events(
        self,
        fecha_inicio: Optional[datetime],
        fecha_fin: Optional[datetime],
        lugar: Optional[str],
        organizador: Optional[str],
        titulo: Optional[str],
        duration_minima: Optional[int],
        duration_maxima: Optional[int],
    ) -> List[EventInDB]:
        """
        Lógica: Construye el filtro de MongoDB con los parámetros de la API.
        """
        filtro = {}
        
        # Lógica de construcción de filtros (es lógica de consulta, va en el Service)
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

        return await self.crud.list_by_filter(filtro)


    async def update_event(self, event_id: UUID, event_update: EventCreate) -> Optional[EventInDB]:
        """Actualiza un evento."""
        update_data = event_update.model_dump(by_alias=True, exclude_unset=True)
        return await self.crud.update(event_id, update_data)


    async def delete_event(self, event_id: UUID) -> bool:
        """Elimina un evento y devuelve si la operación fue exitosa."""
        deleted_count = await self.crud.delete(event_id)
        return deleted_count > 0