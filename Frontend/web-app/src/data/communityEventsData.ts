import { Language } from "../locales/translations";

export interface GTAEvent {
  id: string;
  title: Record<Language, string>;
  category: "arts" | "community" | "health" | "education" | "seniors" | "newcomers";
  municipality: "toronto" | "mississauga" | "brampton" | "markham" | "vaughan" | "richmond_hill" | "oakville" | "burlington" | "hamilton";
  location_name: string;
  address: string;
  postal_code: string;
  lat: number;
  lng: number;
  start_datetime: string;
  end_datetime?: string;
  is_free: boolean;
  cost_amount?: string;
  audience: Record<Language, string>;
  registration_required: boolean;
  registration_deadline?: string;
  registration_instructions?: Record<Language, string>;
  registration_url?: string;
  organizer_name: string;
  accessibility_information: Record<Language, string>;
  source_url: string;
  image?: string;
  why_recommended: Record<Language, string>;
  plain_questions: {
    q1: Record<Language, string>; // What is it
    q2: Record<Language, string>; // When & Where
    q3: Record<Language, string>; // Cost
    q4: Record<Language, string>; // Registration
    q5: Record<Language, string>; // What to do
    q6: Record<Language, string>; // What to check
  };
}

export const GTA_COMMUNITY_EVENTS: GTAEvent[] = [
  {
    id: "evt-brampton-yoga-senior",
    title: {
      es: "Taller de Bienestar y Yoga Suave en Silla",
      en: "Gentle Chair Yoga & Senior Balance Workshop",
      pa: "ਕੁਰਸੀ ਯੋਗਾ ਅਤੇ ਬਜ਼ੁਰਗਾਂ ਲਈ ਤੰਦਰੁਸਤੀ ਵਰਕਸ਼ਾਪ",
    },
    category: "seniors",
    municipality: "brampton",
    location_name: "Centro Comunitario Downtown Brampton",
    address: "8 Central Park Dr, Brampton, ON L6T 1B4",
    postal_code: "L6T 1B4",
    lat: 43.7082,
    lng: -79.7225,
    start_datetime: "2026-11-21T10:30:00",
    end_datetime: "2026-11-21T11:45:00",
    is_free: true,
    cost_amount: "Gratis / Free / ਮੁਫ਼ਤ",
    audience: {
      es: "Adultos mayores (60+), cuidadores y personas con movilidad reducida.",
      en: "Seniors (60+), caregivers, and individuals with reduced mobility.",
      pa: "ਬਜ਼ੁਰਗ (60+), ਦੇਖਭਾਲ ਕਰਨ ਵਾਲੇ ਅਤੇ ਘੱਟ ਗਤੀਸ਼ੀਲਤਾ ਵਾਲੇ ਲੋਕ।",
    },
    registration_required: true,
    registration_deadline: "2026-11-20",
    registration_instructions: {
      es: "Inscripción previa obligatoria por teléfono llamando al 311 o en la recepción.",
      en: "Registration required by calling 311 or visiting the front desk.",
      pa: "311 'ਤੇ ਕਾਲ ਕਰਕੇ ਜਾਂ ਫਰੰਟ ਡੈਸਕ 'ਤੇ ਜਾ ਕੇ ਰਜਿਸਟ੍ਰੇਸ਼ਨ ਲਾਜ਼ਮੀ ਹੈ।",
    },
    registration_url: "https://brampton.ca/recreation",
    organizer_name: "Parks & Recreation Brampton & Biblioteca Central",
    accessibility_information: {
      es: "Rampa accesible en entrada principal, elevador, baños adaptados y sillas ergonómicas con descansabrazos.",
      en: "Main entrance ramp, accessible elevator, adapted washrooms, and ergonomic armrest chairs.",
      pa: "ਮੁੱਖ ਪ੍ਰਵੇਸ਼ ਦੁਆਰ 'ਤੇ ਰੈਂਪ, ਲਿਫਟ, ਪਹੁੰਚਯੋਗ ਬਾਥਰੂਮ ਅਤੇ ਆਰਾਮਦਾਇਕ ਕੁਰਸੀਆਂ।",
    },
    source_url: "https://www.eventbrite.ca/e/brampton-chair-yoga",
    image: "https://images.unsplash.com/photo-1545205597-3d9d02c29597?auto=format&fit=crop&w=800&q=80",
    why_recommended: {
      es: "Recomendado por ser 100% gratuito, adaptado para personas mayores y ubicado cerca del transporte público en Brampton.",
      en: "Recommended because it is 100% free, senior-friendly, and located right by Brampton Transit routes.",
      pa: "ਸਿਫ਼ਾਰਸ਼ ਕੀਤੀ ਗਈ ਹੈ ਕਿਉਂਕਿ ਇਹ 100% ਮੁਫ਼ਤ ਹੈ, ਸੀਨੀਅਰਾਂ ਲਈ ਸੁਖਾਲਾ ਹੈ ਅਤੇ ਬ੍ਰੈਂਪਟਨ ਟ੍ਰਾਂਜ਼ਿਟ ਨੇੜੇ ਹੈ।",
    },
    plain_questions: {
      q1: {
        es: "Una clase grupal muy suave de respiración y estiramiento sentado, diseñada para relajar articulaciones sin esfuerzo físico pesado.",
        en: "A very gentle seated breathing and stretching class designed to relax joints without heavy strain.",
        pa: "ਇੱਕ ਬਹੁਤ ਹੀ ਸੁਖਾਲੀ ਕੁਰਸੀ 'ਤੇ ਬੈਠ ਕੇ ਕੀਤੀ ਜਾਣ ਵਾਲੀ ਕਸਰਤ ਜੋ ਜੋੜਾਂ ਦੇ ਦਰਦ ਤੋਂ ਰਾਹਤ ਦਿੰਦੀ ਹੈ।",
      },
      q2: {
        es: "Sábado 21 de Noviembre, 10:30 AM a 11:45 AM en Downtown Brampton Community Centre (8 Central Park Dr).",
        en: "Saturday, November 21, from 10:30 AM to 11:45 AM at Downtown Brampton Community Centre (8 Central Park Dr).",
        pa: "ਸ਼ਨੀਵਾਰ, 21 ਨਵੰਬਰ, ਸਵੇਰੇ 10:30 ਤੋਂ 11:45 ਵਜੇ ਤੱਕ ਡਾਊਨਟਾਊਨ ਬ੍ਰੈਂਪਟਨ ਕਮਿਊਨਿਟੀ ਸੈਂਟਰ ਵਿਖੇ।",
      },
      q3: {
        es: "Cero dólares ($0). Financiado por programas cívicos de inclusión comunitaria de Peel Region.",
        en: "Zero dollars ($0). Fully funded by Peel Region civic inclusion initiatives.",
        pa: "ਬਿਲਕੁਲ ਮੁਫ਼ਤ ($0)। ਪੀਲ ਰੀਜਨ ਦੇ ਪ੍ਰੋਗਰਾਮ ਦੁਆਰਾ ਸਪਾਂਸਰ ਕੀਤਾ ਗਿਆ।",
      },
      q4: {
        es: "Sí, requiere registro previo por cupo de seguridad (máximo 25 sillas adaptadas). Llama al 311.",
        en: "Yes, pre-registration is required for seating capacity (max 25 chairs). Call 311.",
        pa: "ਹਾਂ, ਸੀਟਾਂ ਦੀ ਸੀਮਤ ਗਿਣਤੀ (25 ਕੁਰਸੀਆਂ) ਕਾਰਨ ਪਹਿਲਾਂ ਰਜਿਸਟਰ ਕਰਨਾ ਲਾਜ਼ਮੀ ਹੈ। 311 'ਤੇ ਕਾਲ ਕਰੋ।",
      },
      q5: {
        es: "Llevar ropa holgada y calzado antideslizante o tenis cómodos. No necesitas traer tapete de yoga.",
        en: "Wear comfortable, loose clothing and non-slip shoes. No need to bring a yoga mat.",
        pa: "ਖੁੱਲ੍ਹੇ ਕੱਪੜੇ ਅਤੇ ਆਰਾਮਦਾਇਕ ਜੁੱਤੇ ਪਾ ਕੇ ਆਓ। ਯੋਗਾ ਮੈਟ ਲਿਆਉਣ ਦੀ ਲੋੜ ਨਹੀਂ।",
      },
      q6: {
        es: "Llegar 15 minutos antes para firmar la lista de asistencia y ubicar tu silla cerca del instructor.",
        en: "Arrive 15 minutes early to sign in and choose your seat near the instructor.",
        pa: "ਹਾਜ਼ਰੀ ਲਗਾਉਣ ਅਤੇ ਅੱਗੇ ਕੁਰਸੀ ਲੈਣ ਲਈ 15 ਮਿੰਟ ਪਹਿਲਾਂ ਪਹੁੰਚੋ।",
      },
    },
  },

  {
    id: "evt-toronto-tech-newcomers",
    title: {
      es: "Café Digital: Uso de Celulares y Trámites del Gobierno para Adultos Mayores",
      en: "Digital Café: Smartphone & Government Services for Seniors & Newcomers",
      pa: "ਡਿਜੀਟਲ ਕੈਫੇ: ਸੀਨੀਅਰਾਂ ਲਈ ਸਮਾਰਟਫੋਨ ਅਤੇ ਸਰਕਾਰੀ ਸੇਵਾਵਾਂ",
    },
    category: "education",
    municipality: "toronto",
    location_name: "Toronto Public Library - Toronto Reference Library",
    address: "789 Yonge St, Toronto, ON M4W 2G8",
    postal_code: "M4W 2G8",
    lat: 43.6718,
    lng: -79.3868,
    start_datetime: "2026-11-24T14:00:00",
    end_datetime: "2026-11-24T16:00:00",
    is_free: true,
    cost_amount: "Gratis / Free / ਮੁਫ਼ਤ",
    audience: {
      es: "Adultos mayores y recién llegados que deseen aprender a usar su teléfono o pedir citas gubernamentales.",
      en: "Older adults and newcomers wanting to learn smartphone basics and official online portals.",
      pa: "ਬਜ਼ੁਰਗ ਅਤੇ ਨਵੇਂ ਆਏ ਲੋਕ ਜੋ ਫ਼ੋਨ ਚਲਾਉਣਾ ਅਤੇ ਸਰਕਾਰੀ ਫਾਰਮ ਭਰਨਾ ਸਿੱਖਣਾ ਚਾਹੁੰਦੇ ਹਨ।",
    },
    registration_required: false,
    organizer_name: "Toronto Public Library & Newcomer Settlement Services",
    accessibility_information: {
      es: "Edificio con rampa automática, subtítulos en pantallas, asistencia en español, punjabi e inglés.",
      en: "Automatic door ramps, large display screens, volunteer helpers speaking Spanish, Punjabi and English.",
      pa: "ਆਟੋਮੈਟਿਕ ਦਰਵਾਜ਼ੇ, ਵੱਡੀਆਂ ਸਕ੍ਰੀਨਾਂ, ਪੰਜਾਬੀ, ਅੰਗਰੇਜ਼ੀ ਅਤੇ ਸਪੈਨਿਸ਼ ਬੋਲਣ ਵਾਲੇ ਵਲੰਟੀਅਰ।",
    },
    source_url: "https://www.torontopubliclibrary.ca",
    image: "https://images.unsplash.com/photo-1516321318423-f06f85e504b3?auto=format&fit=crop&w=800&q=80",
    why_recommended: {
      es: "Ideal si buscas aprender tecnología a tu propio ritmo, con voluntarios pacientes y sin costo.",
      en: "Ideal if you want to learn tech at your own pace with patient volunteers in a barrier-free space.",
      pa: "ਆਪਣੀ ਰਫ਼ਤਾਰ ਨਾਲ ਤਕਨਾਲੋਜੀ ਸਿੱਖਣ ਲਈ ਬਹੁਤ ਵਧੀਆ, ਮਦਦਗਾਰ ਵਲੰਟੀਅਰਾਂ ਦੇ ਨਾਲ।",
    },
    plain_questions: {
      q1: {
        es: "Sesión práctica donde voluntarios jóvenes te enseñan a usar WhatsApp, revisar correos y entrar a tu cuenta de Service Canada.",
        en: "A hands-on drop-in session where helpers teach WhatsApp, email, and how to access Service Canada safely.",
        pa: "ਇੱਕ ਸੌਖੀ ਵਰਕਸ਼ਾਪ ਜਿੱਥੇ ਵਲੰਟੀਅਰ ਵਟਸਐਪ, ਈਮੇਲ ਅਤੇ ਸਰਵਿਸ ਕੈਨੇਡਾ ਵਰਤਣਾ ਸਿਖਾਉਂਦੇ ਹਨ।",
      },
      q2: {
        es: "Martes 24 de Noviembre, de 2:00 PM a 4:00 PM en Sala de Conferencias del 1er piso (789 Yonge St, cerca de metro Bloor-Yonge).",
        en: "Tuesday, November 24, from 2:00 PM to 4:00 PM at 1st Floor Learning Centre (Bloor-Yonge Subway Station).",
        pa: "ਮੰਗਲਵਾਰ, 24 ਨਵੰਬਰ, ਦੁਪਹਿਰ 2:00 ਤੋਂ 4:00 ਵਜੇ ਤੱਕ ਬਲੂਰ-ਯੰਗ ਸਬਵੇਅ ਨੇੜੇ ਲਾਇਬ੍ਰੇਰੀ ਵਿੱਚ।",
      },
      q3: {
        es: "Totalmente gratis. Incluye café y té caliente para los participantes.",
        en: "Completely free. Coffee and tea are provided courtesy of library friends.",
        pa: "ਬਿਲਕੁਲ ਮੁਫ਼ਤ। ਚਾਹ ਅਤੇ ਕੌਫ਼ੀ ਮੁਫ਼ਤ ਦਿੱਤੀ ਜਾਵੇਗੀ।",
      },
      q4: {
        es: "No requiere registro previo. Solo llega con tu celular cargado de batería.",
        en: "No pre-registration needed. Just drop in with your smartphone charged.",
        pa: "ਕੋਈ ਰਜਿਸਟ੍ਰੇਸ਼ਨ ਦੀ ਲੋੜ ਨਹੀਂ। ਬਸ ਆਪਣੇ ਫ਼ੋਨ ਨੂੰ ਚਾਰਜ ਕਰਕੇ ਲਿਆਓ।",
      },
      q5: {
        es: "Trae tu teléfono, tu cargador y una libreta si te gusta anotar contraseñas o pasos importantes.",
        en: "Bring your smartphone, charger, and a small notebook to jot down tips.",
        pa: "ਆਪਣਾ ਫ਼ੋਨ, ਚਾਰਜਰ ਅਤੇ ਨੋਟ ਲਿਖਣ ਲਈ ਇੱਕ ਕਾਪੀ-ਪੈੱਨ ਨਾਲ ਲਿਆਓ।",
      },
      q6: {
        es: "Si usas el metro, la estación Bloor-Yonge tiene ascensor directo a la calle Yonge.",
        en: "If taking transit, Bloor-Yonge subway has accessible street elevators to Yonge St.",
        pa: "ਸਬਵੇਅ ਸਟੇਸ਼ਨ 'ਤੇ ਸਿੱਧੀ ਲਿਫਟ ਉਪਲਬਧ ਹੈ।",
      },
    },
  },

  {
    id: "evt-mississauga-food-market",
    title: {
      es: "Mercado Cultural y Festival de Comida Comunitaria al Aire Libre",
      en: "Mississauga Cultural Food Market & Community Celebration",
      pa: "ਮਿਸੀਸਾਗਾ ਸੱਭਿਆਚਾਰਕ ਭੋਜਨ ਮੇਲਾ ਅਤੇ ਭਾਈਚਾਰਕ ਜਸ਼ਨ",
    },
    category: "culture",
    municipality: "mississauga",
    location_name: "Celebration Square Mississauga",
    address: "300 City Centre Dr, Mississauga, ON L5B 3C1",
    postal_code: "L5B 3C1",
    lat: 43.5890,
    lng: -79.6441,
    start_datetime: "2026-11-28T11:00:00",
    end_datetime: "2026-11-28T17:00:00",
    is_free: true,
    cost_amount: "Entrada Gratis (Comida desde $4 CAD)",
    audience: {
      es: "Familias, adultos mayores, niños y vecinos de todas las culturas.",
      en: "Families, seniors, newcomers, and community members of all ages.",
      pa: "ਸਾਰੇ ਪਰਿਵਾਰ, ਬਜ਼ੁਰਗ, ਬੱਚੇ ਅਤੇ ਹਰ ਭਾਈਚਾਰੇ ਦੇ ਲੋਕ।",
    },
    registration_required: false,
    organizer_name: "City of Mississauga & Mississauga Arts Council",
    accessibility_information: {
      es: "Plaza completamente plana sin escalones, bancas con sombra cada 15 metros, baños públicos accesibles.",
      en: "Fully level plaza with zero stairs, benches every 15 meters, heated accessible restrooms.",
      pa: "ਬਿਲਕੁਲ ਪੱਧਰੀ ਥਾਂ, ਬੈਠਣ ਲਈ ਕੁਰਸੀਆਂ ਅਤੇ ਸੁਵਿਧਾਜਨਕ ਬਾਥਰੂਮ।",
    },
    source_url: "https://www.mississauga.ca/celebration-square",
    image: "https://images.unsplash.com/photo-1555396273-367ea4eb4db5?auto=format&fit=crop&w=800&q=80",
    why_recommended: {
      es: "Excelente para salir a caminar con la familia, probar platillos internacionales y disfrutar música en vivo accesible.",
      en: "Great weekend outdoor outing with family, accessible walking paths, and live music.",
      pa: "ਪਰਿਵਾਰ ਨਾਲ ਘੁੰਮਣ, ਸੁਆਦੀ ਖਾਣਾ ਖਾਣ ਅਤੇ ਸੰਗੀਤ ਸੁਣਨ ਲਈ ਵਧੀਆ ਮੌਕਾ।",
    },
    plain_questions: {
      q1: {
        es: "Feria al aire libre con puestos de comida latinoamericana, india, caribeña y música folclórica en vivo.",
        en: "An outdoor community festival with cultural food stalls, traditional music, and artisan booths.",
        pa: "ਵੱਖ-ਵੱਖ ਸੱਭਿਆਚਾਰਾਂ ਦੇ ਖਾਣੇ, ਸੰਗੀਤ ਅਤੇ ਕਲਾ ਦਾ ਇੱਕ ਖੁੱਲ੍ਹਾ ਭਾਈਚਾਰਕ ਮੇਲਾ।",
      },
      q2: {
        es: "Sábado 28 de Noviembre de 11:00 AM a 5:00 PM en Celebration Square frente al centro comercial Square One.",
        en: "Saturday, November 28, 11:00 AM to 5:00 PM at Celebration Square outside Square One Mall.",
        pa: "ਸ਼ਨੀਵਾਰ, 28 ਨਵੰਬਰ, ਸਵੇਰੇ 11:00 ਤੋਂ ਸ਼ਾਮ 5:00 ਵਜੇ ਤੱਕ ਸੈਲੀਬ੍ਰੇਸ਼ਨ ਸੁਕੇਅਰ ਵਿਖੇ।",
      },
      q3: {
        es: "La entrada y los espectáculos musicales son 100% gratuitos. Cada platillo se compra por separado ($4-$12).",
        en: "Free admission and performances. Food items can be purchased individually ($4-$12).",
        pa: "ਮੇਲੇ ਵਿੱਚ ਦਾਖਲਾ ਬਿਲਕੁਲ ਮੁਫ਼ਤ ਹੈ। ਖਾਣ-ਪੀਣ ਦੀਆਂ ਚੀਜ਼ਾਂ ਮੁੱਲ ਮਿਲਣਗੀਆਂ।",
      },
      q4: {
        es: "No se necesita registro. Entrada libre.",
        en: "No ticket required. Open to the general public.",
        pa: "ਕੋਈ ਟਿਕਟ ਜਾਂ ਰਜਿਸਟ੍ਰੇਸ਼ਨ ਦੀ ਲੋੜ ਨਹੀਂ।",
      },
      q5: {
        es: "Ven con abrigo abrigador para disfrutar la plaza al aire libre. Hay carpas con calefacción.",
        en: "Dress warmly for outdoor weather. Heated hospitality tents are available on site.",
        pa: "ਨਿੱਘੇ ਕੱਪੜੇ ਪਾ ਕੇ ਆਓ। ਗਰਮ ਤੰਬੂਆਂ ਦੀ ਸਹੂਲਤ ਵੀ ਹੋਵੇਗੀ।",
      },
      q6: {
        es: "El estacionamiento subterráneo del City Hall es gratuito los fines de semana con ascensor directo a la plaza.",
        en: "Free underground parking at Mississauga Civic Centre on weekends with elevators to square.",
        pa: "ਵੀਕੈਂਡ 'ਤੇ ਸਿਟੀ ਹਾਲ ਦੀ ਪਾਰਕਿੰਗ ਮੁਫ਼ਤ ਹੈ ਅਤੇ ਸਿੱਧੀ ਲਿਫਟ ਹੈ।",
      },
    },
  },

  {
    id: "evt-markham-health-check",
    title: {
      es: "Feria de Salud Preventiva y Control de Presión para Adultos Mayores",
      en: "Markham Senior Preventive Health & Blood Pressure Clinic",
      pa: "ਮਾਰਖਮ ਸੀਨੀਅਰ ਸਿਹਤ ਜਾਂਚ ਅਤੇ ਬਲੱਡ ਪ੍ਰੈਸ਼ਰ ਕਲੀਨਿਕ",
    },
    category: "health",
    municipality: "markham",
    location_name: "Aaniin Community Centre",
    address: "5665 14th Ave, Markham, ON L3S 3K5",
    postal_code: "L3S 3K5",
    lat: 43.8561,
    lng: -79.2570,
    start_datetime: "2026-11-30T09:30:00",
    end_datetime: "2026-11-30T13:00:00",
    is_free: true,
    cost_amount: "Gratis / Free / ਮੁਫ਼ਤ",
    audience: {
      es: "Personas de 55 años o más residentes en York Region.",
      en: "Adults 55+ residing in Markham and York Region.",
      pa: "ਮਾਰਖਮ ਅਤੇ ਯਾਰਕ ਰੀਜਨ ਦੇ 55 ਸਾਲ ਜਾਂ ਵੱਧ ਉਮਰ ਦੇ ਬਜ਼ੁਰਗ।",
    },
    registration_required: true,
    registration_deadline: "2026-11-28",
    registration_instructions: {
      es: "Reserva tu turno de 20 minutos llamando a la clínica comunitaria o en línea.",
      en: "Book your 20-minute time slot online or through York Region Health Services.",
      pa: "ਆਪਣੀ 20 ਮਿੰਟ ਦੀ ਵਾਰੀ ਬੁੱਕ ਕਰਨ ਲਈ ਫ਼ੋਨ ਕਰੋ ਜਾਂ ਆਨਲਾਈਨ ਰਜਿਸਟਰ ਕਰੋ।",
    },
    registration_url: "https://markham.ca/communitycentres",
    organizer_name: "York Region Public Health & Markham Stouffville Hospital Volunteers",
    accessibility_information: {
      es: "Edificio moderno de una sola planta, sin escaleras, traducción disponible en cantonés, español e inglés.",
      en: "Single-level modern facility, wheelchair loan available at entrance, multilingual nurses.",
      pa: "ਇੱਕ ਮੰਜ਼ਿਲਾ ਇਮਾਰਤ, ਮੁਫ਼ਤ ਵ੍ਹੀਲਚੇਅਰ ਦੀ ਸੁਵਿਧਾ ਅਤੇ ਕਈ ਬੋਲੀਆਂ ਬੋਲਣ ਵਾਲੇ ਨਰਸ।",
    },
    source_url: "https://www.york.ca/health",
    image: "https://images.unsplash.com/photo-1576091160399-112ba8d25d1d?auto=format&fit=crop&w=800&q=80",
    why_recommended: {
      es: "Revisión médica preventiva rápida y amable sin costo, ideal para cuidar tu salud antes del invierno.",
      en: "Friendly preventive check-up with no out-of-pocket costs before winter sets in.",
      pa: "ਸਰਦੀਆਂ ਤੋਂ ਪਹਿਲਾਂ ਮੁਫ਼ਤ ਅਤੇ ਸੁਖਾਲੀ ਸਿਹਤ ਜਾਂਚ ਕਰਵਾਉਣ ਦਾ ਵਧੀਆ ਮੌਕਾ।",
    },
    plain_questions: {
      q1: {
        es: "Enfermeros profesionales revisan tu presión arterial, niveles de azúcar y te orientan sobre vacunas de temporada.",
        en: "Nurses provide blood pressure checks, blood glucose tests, and seasonal health tips.",
        pa: "ਨਰਸਾਂ ਤੁਹਾਡਾ ਬੀਪੀ, ਸ਼ੂਗਰ ਚੈੱਕ ਕਰਨਗੀਆਂ ਅਤੇ ਜ਼ਰੂਰੀ ਸਲਾਹ ਦੇਣਗੀਆਂ।",
      },
      q2: {
        es: "Lunes 30 de Noviembre, 9:30 AM a 1:00 PM en Aaniin Community Centre (5665 14th Ave).",
        en: "Monday, November 30, from 9:30 AM to 1:00 PM at Aaniin Community Centre.",
        pa: "ਸੋਮਵਾਰ, 30 ਨਵੰਬਰ, ਸਵੇਰੇ 9:30 ਤੋਂ ਦੁਪਹਿਰ 1:00 ਵਜੇ ਤੱਕ ਆਨੀਨ ਕਮਿਊਨਿਟੀ ਸੈਂਟਰ ਵਿਖੇ।",
      },
      q3: {
        es: "Totalmente gratuito. No te pedirán tarjeta de crédito ni cobros ocultos.",
        en: "100% free. No payment or credit card is ever required.",
        pa: "ਬਿਲਕੁਲ ਮੁਫ਼ਤ। ਕੋਈ ਪੈਸੇ ਨਹੀਂ ਲਏ ਜਾਣਗੇ।",
      },
      q4: {
        es: "Sí, debes reservar un horario para no hacer filas paradas. Turnos cada 20 minutos.",
        en: "Yes, appointment is needed to ensure you don't stand in line.",
        pa: "ਹਾਂ, ਲੰਬੀ ਲਾਈਨ ਤੋਂ ਬਚਣ ਲਈ ਸਮਾਂ ਬੁੱਕ ਕਰਨਾ ਜ਼ਰੂਰੀ ਹੈ।",
      },
      q5: {
        es: "Trae tu tarjeta de salud OHIP (si la tienes) y la lista de medicinas que tomas a diario.",
        en: "Bring your Ontario Health Card (OHIP) if you have one, and a list of current medications.",
        pa: "ਆਪਣਾ ਓਹਿਪ ਕਾਰਡ (ਜੇ ਹੈ ਤਾਂ) ਅਤੇ ਦਵਾਈਆਂ ਦੀ ਸੂਚੀ ਨਾਲ ਲਿਆਓ।",
      },
      q6: {
        es: "Usa ropa con mangas fáciles de subir para tomar la presión con comodidad.",
        en: "Wear a loose short-sleeved top or shirt with easy-to-roll sleeves.",
        pa: "ਖੁੱਲ੍ਹੇ ਕੱਪੜੇ ਪਾਓ ਤਾਂ ਜੋ ਬਾਂਹ 'ਤੇ ਬੀਪੀ ਆਸਾਨੀ ਨਾਲ ਚੈੱਕ ਹੋ ਸਕੇ।",
      },
    },
  },

  {
    id: "evt-hamilton-art-walk",
    title: {
      es: "Paseo de Arte y Taller de Pintura con Acuarela para Principiantes",
      en: "Hamilton Waterfront Art Walk & Beginner Watercolor Workshop",
      pa: "ਹੈਮਿਲਟਨ ਵਾਟਰਫਰੰਟ ਆਰਟ ਵਾਕ ਅਤੇ ਪੇਂਟਿੰਗ ਵਰਕਸ਼ਾਪ",
    },
    category: "arts",
    municipality: "hamilton",
    location_name: "Pier 8 Waterfront Community Hall",
    address: "47 Discovery Dr, Hamilton, ON L8L 8K4",
    postal_code: "L8L 8K4",
    lat: 43.2720,
    lng: -79.8550,
    start_datetime: "2026-12-05T13:00:00",
    end_datetime: "2026-12-05T15:30:00",
    is_free: true,
    cost_amount: "Gratis / Free / ਮੁਫ਼ਤ (Materiales incluidos)",
    audience: {
      es: "Adultos de todas las edades que quieran relajarse pintando.",
      en: "Adults and seniors looking to relax and try watercolor painting.",
      pa: "ਹਰ ਉਮਰ ਦੇ ਲੋਕ ਜੋ ਪੇਂਟਿੰਗ ਸਿੱਖਣਾ ਅਤੇ ਆਨੰਦ ਲੈਣਾ ਚਾਹੁੰਦੇ ਹਨ।",
    },
    registration_required: true,
    registration_deadline: "2026-12-03",
    registration_instructions: {
      es: "Registro en línea para asegurar tu kit de pinceles y papel de acuarela.",
      en: "Pre-register online to guarantee your complimentary watercolor art kit.",
      pa: "ਮੁਫ਼ਤ ਬੁਰਸ਼ ਅਤੇ ਰੰਗ ਕਿੱਟ ਪ੍ਰਾਪਤ ਕਰਨ ਲਈ ਆਨਲਾਈਨ ਰਜਿਸਟਰ ਕਰੋ।",
    },
    registration_url: "https://www.hamilton.ca/culture",
    organizer_name: "Hamilton Arts Council & Waterfront Trust",
    accessibility_information: {
      es: "Mesas ajustables en altura, acceso a nivel del suelo, estacionamiento reservado para discapacitados.",
      en: "Height-adjustable painting tables, ground-floor level entrance, designated accessible parking.",
      pa: "ਉੱਚਾਈ ਅਨੁਕੂਲ ਮੇਜ਼, ਜ਼ਮੀਨੀ ਪੱਧਰ 'ਤੇ ਦਾਖਲਾ ਅਤੇ ਪਾਰਕਿੰਗ ਦੀ ਸੁਵਿਧਾ।",
    },
    source_url: "https://www.hamiltonartscouncil.ca",
    image: "https://images.unsplash.com/photo-1460661419201-fd4cecdf8a8b?auto=format&fit=crop&w=800&q=80",
    why_recommended: {
      es: "Una tarde creativa y tranquila junto al lago de Hamilton con materiales 100% provistos.",
      en: "A relaxing creative afternoon by Hamilton Harbor with all art supplies provided free.",
      pa: "ਝੀਲ ਦੇ ਕੰਢੇ ਕਲਾ ਸਿੱਖਣ ਦਾ ਸ਼ਾਂਤਮਈ ਮੌਕਾ, ਸਾਰਾ ਸਾਮਾਨ ਮੁਫ਼ਤ ਮਿਲੇਗਾ।",
    },
    plain_questions: {
      q1: {
        es: "Taller para pintar paisajes sencillos con acuarela guiado paso a paso por una instructora paciente.",
        en: "A guided step-by-step watercolor painting workshop by an encouraging local artist.",
        pa: "ਇੱਕ ਆਸਾਨ ਪੇਂਟਿੰਗ ਵਰਕਸ਼ਾਪ ਜਿੱਥੇ ਸਿੱਖਿਅਕ ਤੁਹਾਨੂੰ ਕਦਮ ਦਰ ਕਦਮ ਸਿਖਾਏਗਾ।",
      },
      q2: {
        es: "Sábado 5 de Diciembre, de 1:00 PM a 3:30 PM en Pier 8 Community Hall (47 Discovery Dr, Hamilton).",
        en: "Saturday, December 5, 1:00 PM to 3:30 PM at Pier 8 Waterfront Community Hall.",
        pa: "ਸ਼ਨੀਵਾਰ, 5 ਦਸੰਬਰ, ਦੁਪਹਿਰ 1:00 ਤੋਂ 3:30 ਵਜੇ ਤੱਕ ਪੀਅਰ 8 ਕਮਿਊਨਿਟੀ ਹਾਲ ਵਿਖੇ।",
      },
      q3: {
        es: "Gratis. Todos los pinceles, pinturas y papeles los proporciona el ayuntamiento.",
        en: "Free of charge. All brushes, paints and watercolor paper are supplied for you.",
        pa: "ਬਿਲਕੁਲ ਮੁਫ਼ਤ। ਸਾਰੇ ਰੰਗ ਅਤੇ ਕਾਗਜ਼ ਪ੍ਰਬੰਧਕਾਂ ਵੱਲੋਂ ਦਿੱਤੇ ਜਾਣਗੇ।",
      },
      q4: {
        es: "Sí, requiere registro porque el cupo máximo es de 20 participantes.",
        en: "Yes, registration is required due to room capacity (20 participants maximum).",
        pa: "ਹਾਂ, ਸੀਮਤ ਥਾਂ (20 ਸੀਟਾਂ) ਕਾਰਨ ਰਜਿਸਟਰ ਕਰਨਾ ਜ਼ਰੂਰੀ ਹੈ।",
      },
      q5: {
        es: "Ven con ropa que no te preocupe manchar levemente con agua y pintura lavable.",
        en: "Wear clothes suitable for crafting; water-based washable paints are used.",
        pa: "ਸਧਾਰਨ ਕੱਪੜੇ ਪਾ ਕੇ ਆਓ ਕਿਉਂਕਿ ਪਾਣੀ ਵਾਲੇ ਰੰਗ ਵਰਤੇ ਜਾਣਗੇ।",
      },
      q6: {
        es: "Hay parada de autobús HSR Ruta 20 a 100 metros del vestíbulo.",
        en: "Hamilton Street Railway (HSR) Route 20 stops 100m from the entrance.",
        pa: "ਬੱਸ ਸਟਾਪ ਇਮਾਰਤ ਤੋਂ ਸਿਰਫ਼ 100 ਮੀਟਰ ਦੀ ਦੂਰੀ 'ਤੇ ਹੈ।",
      },
    },
  },
];

// Helper: Coordinates per Postal Code Prefix (Ontario GTA)
export const GTA_POSTAL_COORDS: Record<string, { lat: number; lng: number }> = {
  M: { lat: 43.6532, lng: -79.3832 }, // Toronto Central
  M1: { lat: 43.7845, lng: -79.2294 }, // Scarborough
  M2: { lat: 43.7680, lng: -79.4130 }, // North York
  M4: { lat: 43.6800, lng: -79.3400 }, // East York
  M6: { lat: 43.6600, lng: -79.4500 }, // West Toronto
  M9: { lat: 43.7000, lng: -79.5600 }, // Etobicoke
  L6T: { lat: 43.7082, lng: -79.7225 }, // Brampton East
  L6V: { lat: 43.6833, lng: -79.7667 }, // Brampton Downtown
  L6X: { lat: 43.6700, lng: -79.8000 }, // Brampton West
  L6: { lat: 43.6833, lng: -79.7667 }, // Brampton General
  L5B: { lat: 43.5890, lng: -79.6441 }, // Mississauga City Centre
  L5: { lat: 43.5890, lng: -79.6441 }, // Mississauga General
  L3: { lat: 43.8561, lng: -79.3370 }, // Markham
  L4: { lat: 43.8372, lng: -79.5083 }, // Vaughan / Richmond Hill
  L6H: { lat: 43.4675, lng: -79.6877 }, // Oakville
  L7: { lat: 43.3255, lng: -79.7990 }, // Burlington
  L8: { lat: 43.2557, lng: -79.8711 }, // Hamilton Downtown
  L9: { lat: 43.2300, lng: -79.8900 }, // Hamilton Mountain
};

// Haversine distance calculator in KM
export function calculateDistanceKm(
  lat1: number,
  lon1: number,
  lat2: number,
  lon2: number
): number {
  const R = 6371; // Radius of the Earth in km
  const dLat = ((lat2 - lat1) * Math.PI) / 180;
  const dLon = ((lon2 - lon1) * Math.PI) / 180;
  const a =
    Math.sin(dLat / 2) * Math.sin(dLat / 2) +
    Math.cos((lat1 * Math.PI) / 180) *
      Math.cos((lat2 * Math.PI) / 180) *
      Math.sin(dLon / 2) *
      Math.sin(dLon / 2);
  const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
  return Math.round(R * c * 10) / 10;
}

// Generate RFC 5545 standard .ICS calendar file string
export function generateICSContent(event: GTAEvent, lang: Language): string {
  const clean = (str: string) =>
    str.replace(/\\/g, "\\\\").replace(/[,;]/g, (m) => `\\${m}`).replace(/\n/g, "\\n");

  const formatDt = (dtStr: string) => dtStr.replace(/[-:]/g, "").slice(0, 15);
  const now = new Date().toISOString().replace(/[-:]/g, "").slice(0, 15) + "Z";

  const dtStart = formatDt(event.start_datetime);
  const dtEnd = event.end_datetime ? formatDt(event.end_datetime) : "";

  const title = clean(event.title[lang]);
  const location = clean(`${event.location_name}, ${event.address}`);
  const description = clean(
    `${event.plain_questions.q1[lang]}\n\nOrganizador: ${event.organizer_name}\nAcceso: ${event.accessibility_information[lang]}`
  );

  const lines = [
    "BEGIN:VCALENDAR",
    "VERSION:2.0",
    "PRODID:-//CLEARLY//Accessible Community Events//EN",
    "CALSCALE:GREGORIAN",
    "METHOD:PUBLISH",
    "BEGIN:VEVENT",
    `UID:${event.id}-${Date.now()}@clearly.community`,
    `DTSTAMP:${now}`,
    `DTSTART:${dtStart}`,
    ...(dtEnd ? [`DTEND:${dtEnd}`] : []),
    `SUMMARY:${title}`,
    `LOCATION:${location}`,
    `DESCRIPTION:${description}`,
    "STATUS:CONFIRMED",
    "END:VEVENT",
    "END:VCALENDAR",
  ];

  return lines.join("\r\n");
}

// Trigger instant browser download of .ICS file
export function downloadEventICS(event: GTAEvent, lang: Language): void {
  if (typeof window === "undefined") return;
  const content = generateICSContent(event, lang);
  const blob = new Blob([content], { type: "text/calendar;charset=utf-8" });
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.setAttribute("download", `${event.id}.ics`);
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  setTimeout(() => URL.revokeObjectURL(url), 1000);
}

// Generate Google Maps Directions URL with public transit mode
export function getTransitDirectionsUrl(event: GTAEvent): string {
  const dest = `${event.location_name}, ${event.address}`;
  return `https://www.google.com/maps/dir/?api=1&destination=${encodeURIComponent(dest)}&travelmode=transit`;
}

