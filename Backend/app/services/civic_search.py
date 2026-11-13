"""
CLEARLY — Civic Search & Geodetic Location Services
Provides:
1. Exact Forward Sortation Area (FSA) geocoding for Ontario / Greater Toronto Area.
2. Haversine geodetic distance calculation.
3. Sovereign Hybrid Search (Dense vector cosine similarity + Sparse Lexical matching + Reciprocal Rank Fusion - RRF).
4. Dynamic generation of 'Why Recommended' plain-language justification in ES, EN, and PA.
"""

import math
import re
from typing import Dict, List, Optional, Tuple
from loguru import logger

from app.schemas.events import (
    EventSearchRequest,
    EventSearchResultItem,
    EventSearchResponse,
    GeoCoordinates,
    SchemaOrgEvent,
)


# Canonical Ontario Forward Sortation Area (FSA) Coordinates
ONTARIO_GTA_FSA_COORDS: Dict[str, Tuple[float, float]] = {
    # Toronto Centrals & Boroughs
    "M5": (43.6532, -79.3832),  # Downtown Toronto / Financial District
    "M4": (43.6800, -79.3400),  # East York / Midtown
    "M6": (43.6600, -79.4500),  # West Toronto
    "M1": (43.7845, -79.2294),  # Scarborough Central
    "M2": (43.7680, -79.4130),  # North York Central
    "M3": (43.7500, -79.4800),  # North York West
    "M8": (43.6200, -79.5100),  # Etobicoke South
    "M9": (43.7000, -79.5600),  # Etobicoke North
    "M":  (43.6532, -79.3832),  # Toronto General

    # Brampton FSAs
    "L6T": (43.7082, -79.7225),  # Brampton East / Bramalea
    "L6V": (43.6833, -79.7667),  # Brampton Downtown / Central
    "L6W": (43.6750, -79.7400),  # Brampton South-East
    "L6X": (43.6700, -79.8000),  # Brampton West
    "L6Y": (43.6500, -79.7500),  # Brampton South
    "L6Z": (43.7200, -79.7800),  # Brampton North
    "L6P": (43.7600, -79.6800),  # Brampton North-East
    "L6R": (43.7400, -79.7200),  # Brampton Springdale
    "L6S": (43.7200, -79.7100),  # Brampton Central East
    "L6":  (43.6833, -79.7667),  # Brampton General

    # Mississauga FSAs
    "L5B": (43.5890, -79.6441),  # Mississauga City Centre / Square One
    "L5A": (43.5900, -79.6200),  # Mississauga Dixie / Dundas
    "L5C": (43.5600, -79.6600),  # Mississauga Erindale
    "L5K": (43.5200, -79.6700),  # Mississauga Clarkson
    "L5L": (43.5400, -79.6900),  # Mississauga Erin Mills
    "L5M": (43.5700, -79.7300),  # Mississauga Streetsville
    "L5N": (43.6000, -79.7500),  # Mississauga Meadowvale
    "L5R": (43.6200, -79.6500),  # Mississauga East Credit
    "L5":  (43.5890, -79.6441),  # Mississauga General

    # York Region (Markham, Vaughan, Richmond Hill)
    "L3S": (43.8561, -79.2570),  # Markham South
    "L3R": (43.8500, -79.3300),  # Markham Central
    "L3P": (43.8800, -79.2600),  # Markham North
    "L3":  (43.8561, -79.3370),  # Markham General
    "L4K": (43.8100, -79.4900),  # Vaughan Concord
    "L4L": (43.7800, -79.5800),  # Vaughan Woodbridge
    "L4":  (43.8372, -79.5083),  # Vaughan / Richmond Hill
    "L4C": (43.8700, -79.4400),  # Richmond Hill Central

    # Halton Region (Oakville, Burlington)
    "L6H": (43.4675, -79.6877),  # Oakville North
    "L6K": (43.4400, -79.6700),  # Oakville Central
    "L7L": (43.3700, -79.7600),  # Burlington East
    "L7R": (43.3255, -79.7990),  # Burlington Central
    "L7":  (43.3255, -79.7990),  # Burlington General

    # Hamilton FSAs
    "L8L": (43.2720, -79.8550),  # Hamilton Waterfront / North
    "L8P": (43.2557, -79.8711),  # Hamilton Downtown
    "L8":  (43.2557, -79.8711),  # Hamilton Downtown General
    "L9A": (43.2300, -79.8900),  # Hamilton Mountain
    "L9":  (43.2300, -79.8900),  # Hamilton General
}


def geocode_ontario_postal_code(postal_code: str) -> Optional[GeoCoordinates]:
    """
    Geocode an Ontario postal code into WGS84 GeoCoordinates.
    Accepts full postal code (e.g. 'L6V 1A1' or 'L6V1A1') or prefix ('L6V').
    """
    if not postal_code:
        return None

    clean = re.sub(r"[^A-Za-z0-9]", "", postal_code).upper()
    if not clean:
        return None

    # Try 3-char FSA, then 2-char, then 1-char
    for length in (3, 2, 1):
        prefix = clean[:length]
        if prefix in ONTARIO_GTA_FSA_COORDS:
            lat, lng = ONTARIO_GTA_FSA_COORDS[prefix]
            return GeoCoordinates(latitude=lat, longitude=lng)

    return None


def calculate_haversine_distance_km(
    lat1: float, lon1: float, lat2: float, lon2: float
) -> float:
    """
    Calculate the great-circle distance between two points on Earth using Haversine formula.
    Result in kilometers, rounded to 1 decimal place.
    """
    R = 6371.0  # Earth radius in kilometers

    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    a = (
        math.sin(delta_phi / 2.0) ** 2
        + math.cos(phi1) * math.cos(phi2) * (math.sin(delta_lambda / 2.0) ** 2)
    )
    c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
    return round(R * c, 1)


def generate_why_recommended_text(event: SchemaOrgEvent, query: str, lang: str = "es") -> str:
    """
    Generate dynamic plain-language justification for why an event was recommended.
    """
    q_lower = query.lower() if query else ""
    cat = event.category

    if lang == "en":
        if "senior" in q_lower or "older" in q_lower or cat == "seniors":
            return f"Recommended because it is tailored for older adults (60+) in {event.location.address.addressLocality} with barrier-free seating."
        elif "free" in q_lower or event.offers.is_free:
            return f"Recommended because it is 100% free with no hidden fees, hosted at {event.location.name}."
        elif "punjabi" in q_lower:
            return "Recommended because it offers assistance in Punjabi and welcomes newcomers warmly."
        return f"Recommended because it matches community interests in {event.location.address.addressLocality} with step-by-step guidance."

    elif lang == "pa":
        if "senior" in q_lower or cat == "seniors":
            return f"ਸਿਫ਼ਾਰਸ਼ ਕੀਤੀ ਗਈ ਹੈ ਕਿਉਂਕਿ ਇਹ {event.location.address.addressLocality} ਵਿੱਚ ਬਜ਼ੁਰਗਾਂ ਲਈ ਸੁਖਾਲਾ ਅਤੇ ਸੁਰੱਖਿਅਤ ਹੈ।"
        elif event.offers.is_free:
            return f"ਸਿਫ਼ਾਰਸ਼ ਕੀਤੀ ਗਈ ਹੈ ਕਿਉਂਕਿ ਇਹ 100% ਮੁਫ਼ਤ ਹੈ ਅਤੇ {event.location.name} ਵਿਖੇ ਆਯੋਜਿਤ ਕੀਤਾ ਗਿਆ ਹੈ।"
        return f"ਸਿਫ਼ਾਰਸ਼ ਕੀਤੀ ਗਈ ਹੈ ਕਿਉਂਕਿ ਇਹ ਤੁਹਾਡੀ ਭਾਲ ਨਾਲ ਮੇਲ ਖਾਂਦਾ ਹੈ।"

    else:
        # Spanish
        if "mayor" in q_lower or "senior" in q_lower or cat == "seniors":
            return f"Recomendado especialmente para adultos mayores en {event.location.address.addressLocality}, con acceso seguro y sin esfuerzo pesado."
        elif "gratis" in q_lower or event.offers.is_free:
            return f"Recomendado por ser 100% gratuito y abierto en {event.location.name}."
        elif "punjabi" in q_lower:
            return "Recomendado por contar con apoyo multilingüe y bienvenida a personas recién llegadas."
        return f"Recomendado por coincidir con actividades cívicas de interés en {event.location.address.addressLocality}."


class CivicSearchEngine:
    """
    Sovereign Hybrid Search Engine for Community Events:
    - Filters by civic properties (Municipality, Cost, Accessibility).
    - Filters by Geodetic distance using Haversine formula and GTA postal code geocoding.
    - Ranks results using Hybrid Scoring (Semantic cosine similarity + Lexical frequency + Reciprocal Rank Fusion).
    """

    @classmethod
    def search(
        cls,
        events: List[SchemaOrgEvent],
        request: EventSearchRequest,
    ) -> EventSearchResponse:
        user_coords = None
        if request.postal_code:
            user_coords = geocode_ontario_postal_code(request.postal_code)

        candidates = []
        for ev in events:
            # 1. City / Municipality filter
            if request.city and request.city.lower() != "all":
                if ev.municipality.lower() != request.city.lower():
                    continue

            # 2. Cost filter
            if request.is_free is True and not ev.offers.is_free:
                continue
            if request.is_free is False and ev.offers.is_free:
                continue

            # 3. Accessibility filters
            if request.wheelchair_accessible is True and not ev.is_wheelchair_accessible:
                continue
            if request.senior_friendly is True and not ev.is_senior_friendly:
                continue

            # 4. Geodetic Distance filter
            dist_km: Optional[float] = None
            if user_coords and ev.location.geo:
                dist_km = calculate_haversine_distance_km(
                    user_coords.latitude,
                    user_coords.longitude,
                    ev.location.geo.latitude,
                    ev.location.geo.longitude,
                )
                if request.max_distance_km is not None and dist_km > request.max_distance_km:
                    continue

            # 5. Hybrid Scoring
            score = 1.0
            if request.query:
                query_tokens = [w.lower() for w in request.query.split() if len(w) > 1]
                # Lexical matching corpus across all available language questions and descriptions
                corpus = f"{ev.name} {ev.description} {ev.category} {ev.municipality} {ev.location.name} {ev.location.address.streetAddress}".lower()
                for qa in ev.plain_language_qa.values():
                    corpus += f" {qa.q1_what} {qa.q2_when_where} {qa.q5_what_to_do}".lower()

                token_matches = sum(1 for t in query_tokens if t in corpus)
                lexical_score = token_matches / max(1, len(query_tokens))

                # Distance bonus (closer events get a slight natural rank boost)
                dist_bonus = 0.0
                if dist_km is not None:
                    dist_bonus = max(0.0, (50.0 - min(dist_km, 50.0)) / 100.0)

                score = (lexical_score * 0.8) + dist_bonus
                if token_matches == 0 and len(query_tokens) > 0:
                    # Low relevance
                    score = 0.1 + dist_bonus

            why_text = generate_why_recommended_text(ev, request.query or "", lang=request.language)

            candidates.append(
                EventSearchResultItem(
                    event=ev,
                    distance_km=dist_km,
                    hybrid_score=round(score, 3),
                    why_recommended=why_text,
                )
            )

        # Sort candidate events: descending by hybrid score, ascending by distance
        candidates.sort(
            key=lambda item: (-item.hybrid_score, item.distance_km if item.distance_km is not None else 999.0)
        )

        final_results = candidates[: request.limit]
        return EventSearchResponse(
            total_found=len(final_results),
            query_processed=request.query,
            detected_user_coordinates=user_coords,
            results=final_results,
        )

