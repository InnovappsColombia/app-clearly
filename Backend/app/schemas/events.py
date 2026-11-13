"""
CLEARLY — Schema.org/Event Pydantic Schemas & Civic Event API Models
Implements standard Schema.org Event, Place, Offer, and Plain Language 6-Question representations.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID, uuid4
from pydantic import BaseModel, Field, HttpUrl


class GeoCoordinates(BaseModel):
    latitude: float = Field(..., ge=-90.0, le=90.0, description="WGS84 Latitude")
    longitude: float = Field(..., ge=-180.0, le=180.0, description="WGS84 Longitude")


class PostalAddress(BaseModel):
    streetAddress: str
    addressLocality: str = Field(..., description="Municipality (e.g. Brampton, Toronto, Mississauga)")
    postalCode: str = Field(..., description="Canadian Postal Code (e.g. L6T 1B4)")
    addressRegion: str = "ON"
    addressCountry: str = "CA"


class Place(BaseModel):
    name: str
    address: PostalAddress
    geo: Optional[GeoCoordinates] = None


class Offer(BaseModel):
    price: float = Field(default=0.0, ge=0.0)
    priceCurrency: str = "CAD"
    availability: str = "https://schema.org/InStock"
    is_free: bool = True
    ticket_url: Optional[str] = None


class Organizer(BaseModel):
    name: str
    url: Optional[str] = None
    email: Optional[str] = None
    telephone: Optional[str] = None


class PlainLanguageAnswers(BaseModel):
    """The 6 Canonical Plain Language Questions for cognitive accessibility."""
    q1_what: str = Field(..., description="1. ¿Qué es este evento? / What is this event?")
    q2_when_where: str = Field(..., description="2. ¿Cuándo y dónde? / When and where?")
    q3_cost: str = Field(..., description="3. ¿Cuesta dinero? / Does it cost money?")
    q4_registration: str = Field(..., description="4. ¿Necesito registrarme? / Do I need to register?")
    q5_what_to_do: str = Field(..., description="5. ¿Qué tengo que hacer al llegar? / What to do on arrival?")
    q6_what_to_check: str = Field(..., description="6. ¿Qué debo verificar antes de salir? / What to check before leaving?")
    readability_score_fh: Optional[float] = Field(None, description="Índice Fernández-Huerta (Español)")
    readability_score_fre: Optional[float] = Field(None, description="Flesch Reading Ease (Inglés)")


class TransitGuidance(BaseModel):
    transit_mode_url: str = Field(..., description="Enlace directo a Google Maps en modo transporte público")
    gtfs_accessible_stop_hint: str = Field(..., description="Detalles de plataforma accesible, ascensor o rampa de autobús")
    recommended_arrival_margin_minutes: int = Field(default=15, description="Minutos de anticipación recomendados")


class SchemaOrgEvent(BaseModel):
    """
    Standard Schema.org/Event compliant civic model with CLEARLY Plain Language extensions.
    """
    context: str = Field(default="https://schema.org", alias="@context")
    type: str = Field(default="Event", alias="@type")
    id: UUID = Field(default_factory=uuid4)
    name: str
    description: str
    startDate: datetime
    endDate: Optional[datetime] = None
    eventStatus: str = "https://schema.org/EventScheduled"
    eventAttendanceMode: str = "https://schema.org/OfflineEventAttendanceMode"
    location: Place
    offers: Offer
    organizer: Organizer
    image: Optional[str] = None
    
    # CLEARLY Civic & Gerontological Extensions
    category: str = Field(..., description="arts, community, health, education, seniors, newcomers")
    municipality: str = Field(..., description="toronto, brampton, mississauga, markham, vaughan, richmond_hill, oakville, burlington, hamilton")
    is_wheelchair_accessible: bool = True
    is_senior_friendly: bool = True
    supported_languages: List[str] = Field(default_factory=lambda: ["es", "en", "pa"])
    plain_language_qa: Dict[str, PlainLanguageAnswers] = Field(
        default_factory=dict,
        description="Plain language Q&A keyed by language code ('es', 'en', 'pa')"
    )
    transit_guidance: Optional[TransitGuidance] = None
    embedding: Optional[List[float]] = Field(None, description="1024-dim BGE-M3 embedding vector")

    class Config:
        populate_by_name = True


class EventSearchRequest(BaseModel):
    query: Optional[str] = Field(None, description="Búsqueda en lenguaje natural (Español, Inglés o Punyabí)")
    city: Optional[str] = Field(None, description="Municipio del GTA (e.g. brampton, toronto, mississauga)")
    postal_code: Optional[str] = Field(None, description="Código postal canadiense (ej. L6V 1A1, M5V 2T6)")
    max_distance_km: Optional[float] = Field(None, ge=1.0, le=150.0, description="Radio máximo en kilómetros")
    is_free: Optional[bool] = Field(None, description="Filtrar solo eventos gratuitos")
    wheelchair_accessible: Optional[bool] = Field(None, description="Filtrar acceso garantizado para silla de ruedas")
    senior_friendly: Optional[bool] = Field(None, description="Filtrar actividades amigables para adultos mayores")
    language: str = Field(default="es", description="Idioma preferido para justificación: 'es', 'en', 'pa'")
    limit: int = Field(default=10, ge=1, le=50)


class EventSearchResultItem(BaseModel):
    event: SchemaOrgEvent
    distance_km: Optional[float] = None
    hybrid_score: float = Field(..., description="Puntuación combinada de relevancia semántica + léxica")
    why_recommended: str = Field(..., description="Justificación en lenguaje claro generada para la consulta")


class EventSearchResponse(BaseModel):
    total_found: int
    query_processed: Optional[str] = None
    detected_user_coordinates: Optional[GeoCoordinates] = None
    results: List[EventSearchResultItem]

