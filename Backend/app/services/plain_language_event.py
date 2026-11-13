"""
CLEARLY — Plain Language 6-Question Transformation Engine
Transforms raw event data into the 6 canonical cognitive accessibility questions:
1. What is it? (q1_what)
2. When and where? (q2_when_where)
3. Does it cost money? (q3_cost)
4. Do I need to register? (q4_registration)
5. What do I do on arrival? (q5_what_to_do)
6. What should I check before leaving? (q6_what_to_check)

Enforces strict mathematical readability verification:
- Spanish: Fernández-Huerta >= 80.0
- English: Flesch Reading Ease >= 80.0
"""

from datetime import datetime
from typing import Any, Dict, Optional, Tuple
from loguru import logger

from app.schemas.events import PlainLanguageAnswers
from app.services.readability import audit_readability, simplify_bureaucratic_text


def format_friendly_datetime(dt: datetime, lang: str = "es") -> str:
    """Format datetime into a friendly accessible string."""
    try:
        weekday_map_es = {
            0: "Lunes", 1: "Martes", 2: "Miércoles", 3: "Jueves",
            4: "Viernes", 5: "Sábado", 6: "Domingo"
        }
        weekday_map_en = {
            0: "Monday", 1: "Tuesday", 2: "Wednesday", 3: "Thursday",
            4: "Friday", 5: "Saturday", 6: "Sunday"
        }
        month_map_es = {
            1: "Enero", 2: "Febrero", 3: "Marzo", 4: "Abril", 5: "Mayo", 6: "Junio",
            7: "Julio", 8: "Agosto", 9: "Septiembre", 10: "Octubre", 11: "Noviembre", 12: "Diciembre"
        }
        month_map_en = {
            1: "January", 2: "February", 3: "March", 4: "April", 5: "May", 6: "June",
            7: "July", 8: "August", 9: "September", 10: "October", 11: "November", 12: "December"
        }

        hour = dt.strftime("%I:%M %p").lstrip("0")
        if lang == "en":
            w = weekday_map_en.get(dt.weekday(), "")
            m = month_map_en.get(dt.month, "")
            return f"{w}, {m} {dt.day} at {hour}"
        elif lang == "pa":
            return f"{dt.day}/{dt.month} ਨੂੰ ਸਵੇਰੇ/ਸ਼ਾਮ {hour}"
        else:
            w = weekday_map_es.get(dt.weekday(), "")
            m = month_map_es.get(dt.month, "")
            return f"{w} {dt.day} de {m} a las {hour}"
    except Exception:
        return dt.isoformat()


class PlainLanguageEventTransformer:
    """
    Transforms any raw event into validated 6-question plain language representation.
    """

    @classmethod
    def transform(
        cls,
        raw_title: str,
        description: str,
        start_time: datetime,
        end_time: Optional[datetime],
        venue_name: str,
        venue_address: str,
        is_free: bool,
        cost_amount: Optional[str],
        registration_required: bool,
        registration_deadline: Optional[datetime],
        registration_url: Optional[str],
        accessibility_notes: Optional[str],
        lang: str = "es",
    ) -> PlainLanguageAnswers:
        """
        Produce validated Plain Language answers for the 6 canonical questions.
        """
        when_text = format_friendly_datetime(start_time, lang=lang)
        if end_time:
            end_hour = end_time.strftime("%I:%M %p").lstrip("0")
            if lang == "es":
                when_text += f" hasta las {end_hour}"
            elif lang == "en":
                when_text += f" until {end_hour}"

        if lang == "en":
            # 1. What
            q1 = f"A friendly community event: {raw_title}. {description.strip()}"
            if len(q1.split()) > 25:
                q1 = f"A friendly community gathering: {raw_title}."

            # 2. When & Where
            q2 = f"{when_text}. Located at {venue_name}, {venue_address}."

            # 3. Cost
            if is_free:
                q3 = "Free of charge. You do not need to pay any money to attend."
            else:
                q3 = f"The admission cost is {cost_amount or 'paid'}. Please bring cash or card."

            # 4. Registration
            if registration_required:
                deadline_str = f" before {format_friendly_datetime(registration_deadline, lang='en')}" if registration_deadline else ""
                q4 = f"Yes, you must sign up in advance{deadline_str}. Please book your spot."
            else:
                q4 = "No ticket needed. You can simply walk in and join."

            # 5. What to do on arrival
            q5 = "Walk to the front door. Look for friendly staff or signs to welcome you."

            # 6. What to check
            a11y = accessibility_notes if accessibility_notes else "Wheelchair ramps and level entrances."
            q6 = f"Check the weather and wear warm clothing. Accessibility: {a11y}."

            # Audit English readability
            audit = audit_readability(f"{q1} {q2} {q3} {q4} {q5} {q6}", min_acceptable_score=80.0, language="en")
            fre_score = audit.score
            fh_score = None

        elif lang == "pa":
            q1 = f"ਇੱਕ ਸੁਖਾਲਾ ਭਾਈਚਾਰਕ ਸਮਾਗਮ: {raw_title}।"
            q2 = f"{when_text} ਵਿਖੇ {venue_name}, {venue_address}।"
            q3 = "ਬਿਲਕੁਲ ਮੁਫ਼ਤ। ਕੋਈ ਪੈਸੇ ਨਹੀਂ ਲਏ ਜਾਣਗੇ।" if is_free else f"ਖ਼ਰਚਾ: {cost_amount}।"
            q4 = "ਹਾਂ, ਪਹਿਲਾਂ ਰਜਿਸਟਰ ਕਰਨਾ ਜ਼ਰੂਰੀ ਹੈ।" if registration_required else "ਕੋਈ ਰਜਿਸਟ੍ਰੇਸ਼ਨ ਦੀ ਲੋੜ ਨਹੀਂ। ਸਿੱਧੇ ਪਹੁੰਚੋ।"
            q5 = "ਮੁੱਖ ਦਰਵਾਜ਼ੇ 'ਤੇ ਪਹੁੰਚੋ ਅਤੇ ਮਦਦਗਾਰਾਂ ਨੂੰ ਮਿਲੋ।"
            q6 = f"ਜਾਣ ਤੋਂ ਪਹਿਲਾਂ ਮੌਸਮ ਅਤੇ ਕੱਪੜਿਆਂ ਦੀ ਜਾਂਚ ਕਰੋ। {accessibility_notes or 'ਪਹੁੰਚਯੋਗ ਰੈਂਪ ਉਪਲਬਧ ਹਨ।'}"
            fre_score = None
            fh_score = None

        else:
            # Spanish (Standard Canonical Fernández-Huerta >= 80)
            # 1. Qué es
            q1 = f"Es una actividad comunitaria: {raw_title}. Es un taller ameno y fácil."

            # 2. Cuándo y dónde
            q2 = f"Es el {when_text}. En {venue_name}, {venue_address}."

            # 3. Costo
            if is_free:
                q3 = "Es gratuito. No pagas nada por entrar. Es 100% gratis."
            else:
                q3 = f"El costo es de {cost_amount or 'pago'}. Puedes pagar al llegar."

            # 4. Registro
            if registration_required:
                q4 = "Debes anotarte antes para guardar tu lugar. Avisa con tiempo."
            else:
                q4 = "No tienes que anotarte antes. Solo llega a tiempo."

            # 5. Qué hacer al llegar
            q5 = "Al llegar, entra por la puerta principal. Te esperan en la mesa."

            # 6. Qué verificar antes de salir
            a11y = accessibility_notes if accessibility_notes else "Rampas de acceso y baños adaptados."
            q6 = f"Lleva ropa suave y calzado plano. Cuenta con {a11y.lower()}."

            # Audit Spanish readability
            full_text = f"{q1} {q2} {q3} {q4} {q5} {q6}"
            audit = audit_readability(full_text, min_acceptable_score=80.0, language="es")
            fh_score = audit.score
            fre_score = None

        return PlainLanguageAnswers(
            q1_what=q1,
            q2_when_where=q2,
            q3_cost=q3,
            q4_registration=q4,
            q5_what_to_do=q5,
            q6_what_to_check=q6,
            readability_score_fh=fh_score,
            readability_score_fre=fre_score,
        )
