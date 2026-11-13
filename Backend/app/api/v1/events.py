"""
CLEARLY — Civic Events & Community Inclusion Endpoints
Implements:
- Hybrid search with pgvector/lexical & Haversine distance.
- Schema.org/Event standard representation.
- RFC 5545 iCalendar download.
- 6-Question plain language translation & readability audit.
"""

from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from loguru import logger

from app.db.repository import repository
from app.schemas.events import (
    EventSearchRequest,
    EventSearchResponse,
    PlainLanguageAnswers,
    SchemaOrgEvent,
)
from app.services.calendar_service import RFC5545CalendarGenerator
from app.services.civic_search import CivicSearchEngine
from app.services.plain_language_event import PlainLanguageEventTransformer

router = APIRouter()


@router.post(
    "/search",
    response_model=EventSearchResponse,
    summary="Búsqueda híbrida de eventos cívicos y comunitarios",
    description="Permite buscar eventos en lenguaje natural (ES, EN, PA), filtrar por municipio y distancia geodésica.",
)
async def search_events(request: EventSearchRequest) -> EventSearchResponse:
    # Retrieve all Schema.org events from repository
    events = await repository.list_schema_events()
    return CivicSearchEngine.search(events, request)


@router.get(
    "",
    response_model=List[SchemaOrgEvent],
    summary="Listar todos los eventos comunitarios en formato Schema.org/Event",
)
async def list_events(
    city: Optional[str] = Query(None, description="Filtrar por municipio del GTA"),
    is_free: Optional[bool] = Query(None, description="Filtrar solo eventos gratuitos"),
) -> List[SchemaOrgEvent]:
    events = await repository.list_schema_events()
    if city and city.lower() != "all":
        events = [e for e in events if e.municipality.lower() == city.lower()]
    if is_free is not None:
        events = [e for e in events if e.offers.is_free == is_free]
    return events


@router.get(
    "/{event_id}",
    response_model=SchemaOrgEvent,
    summary="Obtener detalle estructurado de un evento comunitario",
)
async def get_event(event_id: UUID) -> SchemaOrgEvent:
    event = await repository.get_schema_event(event_id)
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Evento con ID {event_id} no encontrado",
        )
    return event


@router.get(
    "/{event_id}/calendar.ics",
    summary="Descargar recordatorio de calendario RFC 5545 (.ics)",
    description="Genera un archivo iCalendar interoperable con Google Calendar, Apple Calendar y Outlook.",
)
async def download_calendar_ics(
    event_id: UUID,
    lang: str = Query("es", description="Idioma preferido para el título y descripción ('es', 'en', 'pa')"),
) -> Response:
    event = await repository.get_schema_event(event_id)
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Evento con ID {event_id} no encontrado",
        )

    # Pick plain description if available
    desc = event.description
    if lang in event.plain_language_qa:
        desc = event.plain_language_qa[lang].q1_what

    location_str = f"{event.location.name}, {event.location.address.streetAddress}, {event.location.address.addressLocality}, ON"
    ics_text = RFC5545CalendarGenerator.generate_event_ics(
        event_id=str(event.id),
        title=event.name,
        description=desc,
        location=location_str,
        start_datetime=event.startDate,
        end_datetime=event.endDate,
        organizer_name=event.organizer.name,
        organizer_email=event.organizer.email,
        url=str(event.offers.ticket_url) if event.offers.ticket_url else None,
    )

    filename = f"clearly-event-{event.id}.ics"
    return Response(
        content=ics_text,
        media_type="text/calendar; charset=utf-8",
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"',
            "Cache-Control": "no-cache",
        },
    )


@router.post(
    "/{event_id}/transform-plain-language",
    response_model=PlainLanguageAnswers,
    summary="Transformar evento a las 6 preguntas canónicas con auditoría de legibilidad",
)
async def transform_event_plain_language(
    event_id: UUID,
    lang: str = Query("es", description="Idioma de destino ('es', 'en', 'pa')"),
) -> PlainLanguageAnswers:
    event = await repository.get_schema_event(event_id)
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Evento con ID {event_id} no encontrado",
        )

    return PlainLanguageEventTransformer.transform(
        raw_title=event.name,
        description=event.description,
        start_time=event.startDate,
        end_time=event.endDate,
        venue_name=event.location.name,
        venue_address=f"{event.location.address.streetAddress}, {event.location.address.addressLocality}",
        is_free=event.offers.is_free,
        cost_amount=f"${event.offers.price:.2f} CAD" if event.offers.price > 0 else "Gratis",
        registration_required=event.offers.availability == "https://schema.org/PreOrder",
        registration_deadline=event.startDate,
        registration_url=str(event.offers.ticket_url) if event.offers.ticket_url else None,
        accessibility_notes="Rampas accesibles y baños adaptados",
        lang=lang,
    )

