export type Language = "en" | "es" | "pa";

export interface Translations {
  // Navigation
  navHome: string;
  navMyEvents: string;
  navSaved: string;
  navProfile: string;
  navAccessibility: string;
  navAbout: string;
  navResponsibleAi: string;

  // Hero & Search
  heroTitle1: string;
  heroTitle2: string;
  heroSubtitle: string;
  homeHint: string;
  askLabel: string;
  askPlaceholder: string;
  ask: string;
  examplesTitle: string;
  tryLabel: string;
  chip1: string;
  chip2: string;
  chip3: string;
  chip4: string;
  example1: string;
  example2: string;
  example3: string;

  // Recommendation & AI reasoning
  recommendedTitle: string;
  seeAll: string;
  seeLess: string;
  whyRecommended: string;
  agentAiLabel: string;
  agentLocalLabel: string;
  noRecommendations: string;
  resultsCount: (count: number) => string;

  // Filters
  filtersTitle: string;
  filtersIntro: string;
  filterCity: string;
  filterCityAll: string;
  filterCost: string;
  filterCostAll: string;
  filterCostFree: string;
  filterCostPaid: string;
  filterPrice: string;
  filterPriceMin: string;
  filterPriceMax: string;
  filterPriceInvalid: string;
  filterPostal: string;
  filterPostalPlaceholder: string;
  filterDistance: string;
  filterDistanceAny: string;
  filterWithin: (km: number) => string;
  filterPostalUnknown: string;
  filterPostalNeeded: string;
  distanceAway: (km: string | number) => string;
  clearFilters: string;
  applyFilters: string;

  // Event Card & View Tabs
  tabSimple: string;
  tabClearly: string;
  viewTabs: string;
  when: string;
  where: string;
  cost: string;
  audience: string;
  registration: string;
  regRequired: string;
  regNotRequired: string;
  deadline: string;
  organizer: string;
  accessibilityInfo: string;
  source: string;
  notProvided: string;
  accessNotProvided: string;
  free: string;
  viewDetails: string;
  listen: string;
  stopListen: string;

  // The 6 Plain Language Questions
  q1: string;
  q2: string;
  q3: string;
  q4: string;
  q5: string;
  q6: string;

  // Attend Guide
  attendTitle: string;
  attendIntro: string;
  attendRegisterT: string;
  attendRegNeeded: string;
  attendRegNotNeeded: string;
  attendRegUnknown: string;
  attendGetThereT: string;
  attendGetThereText: (venue: string) => string;
  directions: string;
  directionsDemoNote: string;
  arriveEarly: string;
  attendCalendarT: string;
  addCalendar: string;
  attendSaveT: string;
  attendBeforeT: string;
  attendBeforeText: string;

  // My Events & Saved
  going: string;
  goingDone: string;
  save: string;
  savedDone: string;
  myEventsTitle: string;
  myEventsIntro: string;
  myEventsEmpty: string;
  savedTitle: string;
  savedIntro: string;
  savedEmpty: string;
  allEventsTitle: string;

  // Municipalities
  municipalities: Record<string, string>;
  categories: Record<string, string>;

  // Tutor & Family
  notifyFamily: string;
  notifiedFamily: string;
}

export const TRANSLATIONS: Record<Language, Translations> = {
  en: {
    navHome: "Home",
    navMyEvents: "My Events",
    navSaved: "Saved",
    navProfile: "Profile",
    navAccessibility: "Accessibility",
    navAbout: "About CLEARLY",
    navResponsibleAi: "Responsible AI",

    heroTitle1: "Your community.",
    heroTitle2: "Made clear.",
    heroSubtitle: "Find local opportunities, understand them in your language, and feel confident taking part.",
    homeHint: "Ask CLEARLY in your own words. It will recommend events for you.",
    askLabel: "Your question for CLEARLY",
    askPlaceholder: "Example: I'm new to Toronto. What free activities can I go to this weekend?",
    ask: "Ask CLEARLY",
    examplesTitle: "Try one of these:",
    tryLabel: "Try:",
    chip1: "Free events nearby",
    chip2: "Activities for seniors",
    chip3: "Events in Punjabi",
    chip4: "Learn something new",
    example1: "I'm new to Toronto. What free activities can I go to this weekend?",
    example2: "Activities for older adults in Brampton and GTA",
    example3: "Gentle wellness and tax clinics for pensioners",

    recommendedTitle: "Recommended for you",
    seeAll: "See all",
    seeLess: "Show fewer",
    whyRecommended: "Why this event",
    agentAiLabel: "AI recommendation. Check the event details before you go.",
    agentLocalLabel: "Simple search (not AI): the AI assistant is not available right now.",
    noRecommendations: "No events matched your question. Try asking in a different way, or look at all events below.",
    resultsCount: (count: number) => (count === 1 ? "1 event found" : `${count} events found`),

    filtersTitle: "Filters",
    filtersIntro: "Narrow the events by place and cost.",
    filterCity: "City",
    filterCityAll: "All cities",
    filterCost: "Free or paid",
    filterCostAll: "Free and paid",
    filterCostFree: "Free only",
    filterCostPaid: "Paid only",
    filterPrice: "Ticket price (Canadian dollars)",
    filterPriceMin: "From $",
    filterPriceMax: "To $",
    filterPriceInvalid: "The minimum price must not be higher than the maximum price.",
    filterPostal: "Your postal code",
    filterPostalPlaceholder: "Example: L6V 1A1",
    filterDistance: "Distance from you",
    filterDistanceAny: "Any distance",
    filterWithin: (km: number) => `Within ${km} km`,
    filterPostalUnknown: "We don't recognise this postal code. Use a code from Toronto (starts with M), GTA (starts with L) or Hamilton (starts with L8 or L9).",
    filterPostalNeeded: "Write your postal code to filter by distance.",
    distanceAway: (km: string | number) => `About ${km} km away`,
    clearFilters: "Clear filters",
    applyFilters: "Apply filters",

    tabSimple: "Simple",
    tabClearly: "CLEARLY",
    viewTabs: "Choose how to see the event",
    when: "Date and time",
    where: "Location",
    cost: "Cost",
    audience: "Who it is for",
    registration: "Registration",
    regRequired: "Registration required",
    regNotRequired: "No registration needed",
    deadline: "Registration deadline",
    organizer: "Organizer",
    accessibilityInfo: "Accessibility",
    source: "Official source",
    notProvided: "Information not provided.",
    accessNotProvided: "Accessibility information has not been provided. Contact organizer to ask.",
    free: "Free",
    viewDetails: "View details",
    listen: "Listen to the description",
    stopListen: "Stop reading",

    q1: "1. What is this event?",
    q2: "2. When and where is it?",
    q3: "3. Does it cost money?",
    q4: "4. Do I need to register?",
    q5: "5. What do I need to do?",
    q6: "6. What should I check before going?",

    attendTitle: "How to attend",
    attendIntro: "CLEARLY will guide you step by step.",
    attendRegisterT: "Register",
    attendRegNeeded: "You need to register before you go.",
    attendRegNotNeeded: "No registration needed. You can just arrive.",
    attendRegUnknown: "It does not say if you need to register. Ask the organizer.",
    attendGetThereT: "Get there",
    attendGetThereText: (venue: string) => `The event is at ${venue}.`,
    directions: "Get directions (Google Maps Transit)",
    directionsDemoNote: "Confirm the address with the organizer before you travel.",
    arriveEarly: "Try to arrive 10 to 15 minutes early.",
    attendCalendarT: "Add it to your calendar",
    addCalendar: "Download .ICS calendar file",
    attendSaveT: "Keep it in My Events",
    attendBeforeT: "Before you go",
    attendBeforeText: "Check the time, cost and accessibility. Contact the organizer if something is missing.",

    going: "Add to My Events",
    goingDone: "In My Events",
    save: "Save",
    savedDone: "Saved",
    myEventsTitle: "My Events",
    myEventsIntro: "Events you plan to attend.",
    myEventsEmpty: "You have not added any events yet. Select an event and press 'Add to My Events'.",
    savedTitle: "Saved events",
    savedIntro: "Events you saved to look at later.",
    savedEmpty: "You have not saved any events yet. Select an event and press 'Save'.",
    allEventsTitle: "All upcoming community opportunities",

    municipalities: {
      all: "All Cities",
      toronto: "Toronto",
      mississauga: "Mississauga",
      brampton: "Brampton",
      markham: "Markham",
      vaughan: "Vaughan",
      richmond_hill: "Richmond Hill",
      oakville: "Oakville",
      burlington: "Burlington",
      hamilton: "Hamilton",
    },

    categories: {
      arts: "Arts & Culture",
      community: "Community & Civic",
      health: "Health & Wellness",
      education: "Education & Skills",
      seniors: "Older Adults (60+)",
      newcomers: "Newcomers & Settlement",
    },

    notifyFamily: "Notify family tutor (Carlos)",
    notifiedFamily: "Notified to Carlos via WhatsApp",
  },

  es: {
    navHome: "Inicio",
    navMyEvents: "Mis Eventos",
    navSaved: "Guardados",
    navProfile: "Perfil",
    navAccessibility: "Accesibilidad",
    navAbout: "Acerca de CLEARLY",
    navResponsibleAi: "IA Responsable",

    heroTitle1: "Tu comunidad.",
    heroTitle2: "Más clara.",
    heroSubtitle: "Encuentra oportunidades locales, entiéndelas en tu idioma y participa con total confianza.",
    homeHint: "Pregúntale a CLEARLY en tus propias palabras. Te recomendará eventos ideales para ti.",
    askLabel: "Tu pregunta para CLEARLY",
    askPlaceholder: "Ejemplo: Soy nuevo en Toronto. ¿A qué actividades gratuitas puedo ir este fin de semana?",
    ask: "Preguntar a CLEARLY",
    examplesTitle: "Prueba una de estas:",
    tryLabel: "Prueba:",
    chip1: "Eventos gratuitos cerca",
    chip2: "Actividades para mayores",
    chip3: "Eventos en Punjabi",
    chip4: "Aprender algo nuevo",
    example1: "Soy nuevo en Toronto. ¿A qué actividades gratuitas puedo ir este fin de semana?",
    example2: "Actividades para personas mayores en Brampton y GTA",
    example3: "Clínicas gratuitas de impuestos y bienestar para pensionados",

    recommendedTitle: "Recomendados para ti",
    seeAll: "Ver todos",
    seeLess: "Mostrar menos",
    whyRecommended: "Por qué este evento",
    agentAiLabel: "Recomendación de IA. Verifica los detalles antes de ir.",
    agentLocalLabel: "Búsqueda estándar: el asistente de IA no está disponible en este momento.",
    noRecommendations: "Ningún evento coincide con tu pregunta. Intenta preguntar de otra manera o explora todos los eventos abajo.",
    resultsCount: (count: number) => (count === 1 ? "1 evento encontrado" : `${count} eventos encontrados`),

    filtersTitle: "Filtros",
    filtersIntro: "Reduce los eventos por lugar y costo.",
    filterCity: "Ciudad",
    filterCityAll: "Todas las ciudades",
    filterCost: "Gratis o pago",
    filterCostAll: "Gratis y pagos",
    filterCostFree: "Solo gratis",
    filterCostPaid: "Solo pagos",
    filterPrice: "Precio de la entrada (dólares canadienses)",
    filterPriceMin: "Desde $",
    filterPriceMax: "Hasta $",
    filterPriceInvalid: "El precio mínimo no puede ser mayor que el precio máximo.",
    filterPostal: "Tu código postal",
    filterPostalPlaceholder: "Ejemplo: L6V 1A1",
    filterDistance: "Distancia desde ti",
    filterDistanceAny: "Cualquier distancia",
    filterWithin: (km: number) => `A menos de ${km} km`,
    filterPostalUnknown: "No reconocemos este código postal. Usa un código de Toronto (empieza con M), del GTA (empieza con L) o Hamilton (empieza con L8 o L9).",
    filterPostalNeeded: "Escribe tu código postal para filtrar por distancia.",
    distanceAway: (km: string | number) => `A unos ${km} km de distancia`,
    clearFilters: "Limpiar filtros",
    applyFilters: "Aplicar filtros",

    tabSimple: "Simple",
    tabClearly: "CLEARLY",
    viewTabs: "Elige cómo ver el evento",
    when: "Fecha y hora",
    where: "Lugar",
    cost: "Costo",
    audience: "Para quién es",
    registration: "Registro",
    regRequired: "Requiere registro previo",
    regNotRequired: "No necesita registro (entrada libre)",
    deadline: "Fecha límite de inscripción",
    organizer: "Organizador",
    accessibilityInfo: "Accesibilidad",
    source: "Fuente oficial",
    notProvided: "Información no especificada.",
    accessNotProvided: "Información de accesibilidad no proporcionada. Contacta al organizador.",
    free: "Gratis",
    viewDetails: "Ver detalles",
    listen: "Escuchar descripción",
    stopListen: "Detener lectura",

    q1: "1. ¿Qué es este evento?",
    q2: "2. ¿Cuándo y dónde se realiza?",
    q3: "3. ¿Cuesta dinero?",
    q4: "4. ¿Necesito registrarme antes de ir?",
    q5: "5. ¿Qué tengo que hacer al llegar?",
    q6: "6. ¿Qué debo verificar antes de salir de casa?",

    attendTitle: "Cómo asistir",
    attendIntro: "CLEARLY te orientará paso a paso para que no tengas dudas.",
    attendRegisterT: "1. Registro",
    attendRegNeeded: "Debes registrarte antes de asistir.",
    attendRegNotNeeded: "No necesitas registrarte. Puedes llegar directamente.",
    attendRegUnknown: "No indica si requiere registro. Te sugerimos consultar al organizador.",
    attendGetThereT: "2. Cómo llegar",
    attendGetThereText: (venue: string) => `El evento se lleva a cabo en ${venue}.`,
    directions: "Cómo llegar (Google Maps Transporte Público)",
    directionsDemoNote: "Confirma la dirección exacta con el organizador antes de viajar.",
    arriveEarly: "Procura llegar de 10 a 15 minutos antes de la hora indicada.",
    attendCalendarT: "3. Agendar en tu calendario",
    addCalendar: "Descargar archivo .ICS para calendario",
    attendSaveT: "4. Guardar en Mis Eventos",
    attendBeforeT: "5. Antes de salir",
    attendBeforeText: "Verifica el clima, la ropa adecuada y la accesibilidad de la entrada.",

    going: "Voy a asistir",
    goingDone: "En Mis Eventos",
    save: "Guardar",
    savedDone: "Guardado",
    myEventsTitle: "Mis Eventos",
    myEventsIntro: "Actividades a las que planeas asistir.",
    myEventsEmpty: "Aún no has agregado eventos. Abre un evento y presiona 'Voy a asistir'.",
    savedTitle: "Eventos guardados",
    savedIntro: "Actividades que guardaste para revisar después.",
    savedEmpty: "No tienes eventos guardados. Abre un evento y presiona 'Guardar'.",
    allEventsTitle: "Todas las oportunidades comunitarias próximas",

    municipalities: {
      all: "Todas las ciudades",
      toronto: "Toronto",
      mississauga: "Mississauga",
      brampton: "Brampton",
      markham: "Markham",
      vaughan: "Vaughan",
      richmond_hill: "Richmond Hill",
      oakville: "Oakville",
      burlington: "Burlington",
      hamilton: "Hamilton",
    },

    categories: {
      arts: "Arte y Cultura",
      community: "Comunidad y Cívico",
      health: "Salud y Bienestar",
      education: "Educación y Habilidades",
      seniors: "Adultos Mayores (60+)",
      newcomers: "Recién Llegados (Newcomers)",
    },

    notifyFamily: "Avisar a mi familiar Carlos (WhatsApp)",
    notifiedFamily: "Avisado a Carlos por WhatsApp para acompañarte",
  },

  pa: {
    navHome: "ਘਰ",
    navMyEvents: "ਮੇਰੇ ਸਮਾਗਮ",
    navSaved: "ਸਾਂਭੇ ਹੋਏ",
    navProfile: "ਪ੍ਰੋਫ਼ਾਈਲ",
    navAccessibility: "ਪਹੁੰਚਯੋਗਤਾ",
    navAbout: "CLEARLY ਬਾਰੇ",
    navResponsibleAi: "ਜ਼ਿੰਮੇਵਾਰ AI",

    heroTitle1: "ਤੁਹਾਡਾ ਭਾਈਚਾਰਾ।",
    heroTitle2: "ਵਧੇਰੇ ਸਪੱਸ਼ਟ।",
    heroSubtitle: "ਸਥਾਨਕ ਮੌਕੇ ਲੱਭੋ, ਉਹਨਾਂ ਨੂੰ ਆਪਣੀ ਬੋਲੀ ਵਿੱਚ ਸਮਝੋ, ਅਤੇ ਭਰੋਸੇ ਨਾਲ ਹਿੱਸਾ ਲਓ।",
    homeHint: "CLEARLY ਨੂੰ ਆਪਣੇ ਸ਼ਬਦਾਂ ਵਿੱਚ ਪੁੱਛੋ। ਇਹ ਤੁਹਾਡੇ ਲਈ ਸਮਾਗਮਾਂ ਦੀ ਸਿਫ਼ਾਰਸ਼ ਕਰੇਗਾ।",
    askLabel: "CLEARLY ਲਈ ਤੁਹਾਡਾ ਸਵਾਲ",
    askPlaceholder: "ਉਦਾਹਰਨ: ਮੈਂ ਟੋਰਾਂਟੋ ਵਿੱਚ ਨਵਾਂ ਹਾਂ। ਇਸ ਵੀਕੈਂਡ ਮੈਂ ਕਿਹੜੀਆਂ ਮੁਫ਼ਤ ਗਤੀਵਿਧੀਆਂ ਵਿੱਚ ਜਾ ਸਕਦਾ ਹਾਂ?",
    ask: "CLEARLY ਨੂੰ ਪੁੱਛੋ",
    examplesTitle: "ਇਹਨਾਂ ਵਿੱਚੋਂ ਇੱਕ ਅਜ਼ਮਾਓ:",
    tryLabel: "ਅਜ਼ਮਾਓ:",
    chip1: "ਨੇੜਲੇ ਮੁਫ਼ਤ ਸਮਾਗਮ",
    chip2: "ਬਜ਼ੁਰਗਾਂ ਲਈ ਗਤੀਵਿਧੀਆਂ",
    chip3: "ਪੰਜਾਬੀ ਵਿੱਚ ਸਮਾਗਮ",
    chip4: "ਕੁਝ ਨਵਾਂ ਸਿੱਖੋ",
    example1: "ਮੈਂ ਟੋਰਾਂਟੋ ਵਿੱਚ ਨਵਾਂ ਹਾਂ। ਇਸ ਵੀਕੈਂਡ ਮੈਂ ਕਿਹੜੀਆਂ ਮੁਫ਼ਤ ਗਤੀਵਿਧੀਆਂ ਵਿੱਚ ਜਾ ਸਕਦਾ ਹਾਂ?",
    example2: "ਬ੍ਰੈਂਪਟਨ ਵਿੱਚ ਸੀਨੀਅਰਾਂ ਲਈ ਸਿਹਤ ਅਤੇ ਯੋਗਾ ਸਮਾਗਮ",
    example3: "ਪੈਨਸ਼ਨਰਾਂ ਲਈ ਮੁਫ਼ਤ ਟੈਕਸ ਕਲੀਨਿਕ ਅਤੇ ਮਦਦ",

    recommendedTitle: "ਤੁਹਾਡੇ ਲਈ ਸਿਫ਼ਾਰਸ਼ ਕੀਤੇ ਗਏ",
    seeAll: "ਸਾਰੇ ਵੇਖੋ",
    seeLess: "ਘੱਟ ਵੇਖੋ",
    whyRecommended: "ਇਹ ਸਮਾਗਮ ਕਿਉਂ",
    agentAiLabel: "AI ਸਿਫ਼ਾਰਸ਼। ਜਾਣ ਤੋਂ ਪਹਿਲਾਂ ਸਮਾਗਮ ਦੇ ਵੇਰਵਿਆਂ ਦੀ ਜਾਂਚ ਕਰੋ।",
    agentLocalLabel: "ਸਧਾਰਨ ਖੋਜ: AI ਸਹਾਇਕ ਇਸ ਸਮੇਂ ਉਪਲਬਧ ਨਹੀਂ ਹੈ।",
    noRecommendations: "ਤੁਹਾਡੇ ਸਵਾਲ ਨਾਲ ਕੋਈ ਸਮਾਗਮ ਮੇਲ ਨਹੀਂ ਖਾਂਦਾ। ਕਿਸੇ ਹੋਰ ਤਰੀਕੇ ਨਾਲ ਪੁੱਛਣ ਦੀ ਕੋਸ਼ਿਸ਼ ਕਰੋ, ਜਾਂ ਹੇਠਾਂ ਸਾਰੇ ਸਮਾਗਮ ਵੇਖੋ।",
    resultsCount: (count: number) => (count === 1 ? "1 ਸਮਾਗਮ ਮਿਲਿਆ" : `${count} ਸਮਾਗਮ ਮਿਲੇ`),

    filtersTitle: "ਫਿਲਟਰ",
    filtersIntro: "ਥਾਂ ਅਤੇ ਖ਼ਰਚੇ ਅਨੁਸਾਰ ਸਮਾਗਮ ਘਟਾਓ।",
    filterCity: "ਸ਼ਹਿਰ",
    filterCityAll: "ਸਾਰੇ ਸ਼ਹਿਰ",
    filterCost: "ਮੁਫ਼ਤ ਜਾਂ ਪੈਸੇ ਵਾਲਾ",
    filterCostAll: "ਮੁਫ਼ਤ ਅਤੇ ਪੈਸੇ ਵਾਲੇ",
    filterCostFree: "ਸਿਰਫ਼ ਮੁਫ਼ਤ",
    filterCostPaid: "ਸਿਰਫ਼ ਪੈਸੇ ਵਾਲੇ",
    filterPrice: "ਟਿਕਟ ਦੀ ਕੀਮਤ (ਕੈਨੇਡੀਅਨ ਡਾਲਰ)",
    filterPriceMin: "ਤੋਂ $",
    filterPriceMax: "ਤੱਕ $",
    filterPriceInvalid: "ਘੱਟੋ-ਘੱਟ ਕੀਮਤ ਵੱਧ ਤੋਂ ਵੱਧ ਕੀਮਤ ਤੋਂ ਵੱਧ ਨਹੀਂ ਹੋ ਸਕਦੀ।",
    filterPostal: "ਤੁਹਾਡਾ ਪੋਸਟਲ ਕੋਡ",
    filterPostalPlaceholder: "ਉਦਾਹਰਨ: L6V 1A1",
    filterDistance: "ਤੁਹਾਡੇ ਤੋਂ ਦੂਰੀ",
    filterDistanceAny: "ਕੋਈ ਵੀ ਦੂਰੀ",
    filterWithin: (km: number) => `${km} ਕਿ.ਮੀ. ਦੇ ਅੰਦਰ`,
    filterPostalUnknown: "ਅਸੀਂ ਇਸ ਪੋਸਟਲ ਕੋਡ ਨੂੰ ਪਛਾਣਦੇ ਨਹੀਂ ਹਾਂ। ਟੋਰਾਂਟੋ (M ਨਾਲ ਸ਼ੁਰੂ), GTA (L ਨਾਲ ਸ਼ੁਰੂ) ਜਾਂ ਹੈਮਿਲਟਨ (L8 ਜਾਂ L9) ਦਾ ਕੋਡ ਵਰਤੋ।",
    filterPostalNeeded: "ਦੂਰੀ ਅਨੁਸਾਰ ਫਿਲਟਰ ਕਰਨ ਲਈ ਆਪਣਾ ਪੋਸਟਲ ਕੋਡ ਲਿਖੋ।",
    distanceAway: (km: string | number) => `ਲਗਭਗ ${km} ਕਿ.ਮੀ. ਦੂਰ`,
    clearFilters: "ਫਿਲਟਰ ਸਾਫ਼ ਕਰੋ",
    applyFilters: "ਫਿਲਟਰ ਲਾਗੂ ਕਰੋ",

    tabSimple: "ਸਧਾਰਨ",
    tabClearly: "CLEARLY",
    viewTabs: "ਸਮਾਗਮ ਵੇਖਣ ਦਾ ਤਰੀਕਾ ਚੁਣੋ",
    when: "ਮਿਤੀ ਅਤੇ ਸਮਾਂ",
    where: "ਸਥਾਨ",
    cost: "ਖ਼ਰਚਾ",
    audience: "ਕਿਸ ਲਈ ਹੈ",
    registration: "ਰਜਿਸਟ੍ਰੇਸ਼ਨ",
    regRequired: "ਰਜਿਸਟ੍ਰੇਸ਼ਨ ਲਾਜ਼ਮੀ ਹੈ",
    regNotRequired: "ਕੋਈ ਰਜਿਸਟ੍ਰੇਸ਼ਨ ਲੋੜੀਂਦੀ ਨਹੀਂ",
    deadline: "ਰਜਿਸਟ੍ਰੇਸ਼ਨ ਦੀ ਆਖ਼ਰੀ ਮਿਤੀ",
    organizer: "ਪ੍ਰਬੰਧਕ",
    accessibilityInfo: "ਪਹੁੰਚਯੋਗਤਾ",
    source: "ਅਧਿਕਾਰਤ ਸਰੋਤ",
    notProvided: "ਜਾਣਕਾਰੀ ਨਹੀਂ ਦਿੱਤੀ ਗਈ।",
    accessNotProvided: "ਪਹੁੰਚਯੋਗਤਾ ਜਾਣਕਾਰੀ ਨਹੀਂ ਦਿੱਤੀ ਗਈ। ਪੁੱਛਣ ਲਈ ਪ੍ਰਬੰਧਕ ਨਾਲ ਸੰਪਰਕ ਕਰੋ।",
    free: "ਮੁਫ਼ਤ",
    viewDetails: "ਵੇਰਵੇ ਵੇਖੋ",
    listen: "ਵੇਰਵਾ ਸੁਣੋ",
    stopListen: "ਪੜ੍ਹਨਾ ਬੰਦ ਕਰੋ",

    q1: "1. ਇਹ ਸਮਾਗਮ ਕੀ ਹੈ?",
    q2: "2. ਇਹ ਕਦੋਂ ਅਤੇ ਕਿੱਥੇ ਹੈ?",
    q3: "3. ਕੀ ਇਸ ਵਿੱਚ ਪੈਸੇ ਲੱਗਦੇ ਹਨ?",
    q4: "4. ਕੀ ਮੈਨੂੰ ਰਜਿਸਟਰ ਕਰਨ ਦੀ ਲੋੜ ਹੈ?",
    q5: "5. ਮੈਨੂੰ ਕੀ ਕਰਨ ਦੀ ਲੋੜ ਹੈ?",
    q6: "6. ਜਾਣ ਤੋਂ ਪਹਿਲਾਂ ਮੈਨੂੰ ਕੀ ਜਾਂਚਣਾ ਚਾਹੀਦਾ ਹੈ?",

    attendTitle: "ਕਿਵੇਂ ਸ਼ਾਮਲ ਹੋਣਾ ਹੈ",
    attendIntro: "CLEARLY ਕਦਮ ਦਰ ਕਦਮ ਤੁਹਾਡੀ ਅਗਵਾਈ ਕਰੇਗਾ।",
    attendRegisterT: "1. ਰਜਿਸਟਰ ਕਰੋ",
    attendRegNeeded: "ਤੁਹਾਨੂੰ ਜਾਣ ਤੋਂ ਪਹਿਲਾਂ ਰਜਿਸਟਰ ਕਰਨਾ ਪਵੇਗਾ।",
    attendRegNotNeeded: "ਕੋਈ ਰਜਿਸਟ੍ਰੇਸ਼ਨ ਲੋੜੀਂਦੀ ਨਹੀਂ। ਤੁਸੀਂ ਸਿੱਧੇ ਪਹੁੰਚ ਸਕਦੇ ਹੋ।",
    attendRegUnknown: "ਇਹ ਨਹੀਂ ਦੱਸਦਾ ਕਿ ਤੁਹਾਨੂੰ ਰਜਿਸਟਰ ਕਰਨ ਦੀ ਲੋੜ ਹੈ ਜਾਂ ਨਹੀਂ।",
    attendGetThereT: "2. ਉੱਥੇ ਪਹੁੰਚੋ",
    attendGetThereText: (venue: string) => `ਸਮਾਗਮ ${venue} ਵਿਖੇ ਹੈ।`,
    directions: "ਦਿਸ਼ਾ-ਨਿਰਦੇਸ਼ ਲਵੋ (ਗੂਗਲ ਮੈਪਸ ਪਬਲਿਕ ਟਰਾਂਸਪੋਰਟ)",
    directionsDemoNote: "ਸਫ਼ਰ ਕਰਨ ਤੋਂ ਪਹਿਲਾਂ ਪ੍ਰਬੰਧਕ ਨਾਲ ਪਤੇ ਦੀ ਪੁਸ਼ਟੀ ਕਰੋ।",
    arriveEarly: "10 ਤੋਂ 15 ਮਿੰਟ ਪਹਿਲਾਂ ਪਹੁੰਚਣ ਦੀ ਕੋਸ਼ਿਸ਼ ਕਰੋ।",
    attendCalendarT: "3. ਆਪਣੇ ਕੈਲੰਡਰ ਵਿੱਚ ਸ਼ਾਮਲ ਕਰੋ",
    addCalendar: "ਕੈਲੰਡਰ ਫ਼ਾਈਲ (.ICS) ਡਾਊਨਲੋਡ ਕਰੋ",
    attendSaveT: "4. ਮੇਰੇ ਸਮਾਗਮਾਂ ਵਿੱਚ ਰੱਖੋ",
    attendBeforeT: "5. ਜਾਣ ਤੋਂ ਪਹਿਲਾਂ",
    attendBeforeText: "ਸਮਾਂ, ਖ਼ਰਚਾ ਅਤੇ ਪਹੁੰਚਯੋਗਤਾ ਦੀ ਜਾਂਚ ਕਰੋ।",

    going: "ਮੈਂ ਜਾ ਰਿਹਾ ਹਾਂ",
    goingDone: "ਮੇਰੇ ਸਮਾਗਮਾਂ ਵਿੱਚ ਹੈ",
    save: "ਸਾਂਭੋ",
    savedDone: "ਸਾਂਭਿਆ ਗਿਆ",
    myEventsTitle: "ਮੇਰੇ ਸਮਾਗਮ",
    myEventsIntro: "ਉਹ ਸਮਾਗਮ ਜਿਨ੍ਹਾਂ ਵਿੱਚ ਤੁਸੀਂ ਸ਼ਾਮਲ ਹੋਣ ਦੀ ਯੋਜਨਾ ਬਣਾਈ ਹੈ।",
    myEventsEmpty: "ਤੁਸੀਂ ਅਜੇ ਕੋਈ ਸਮਾਗਮ ਸ਼ਾਮਲ ਨਹੀਂ ਕੀਤਾ ਹੈ।",
    savedTitle: "ਸਾਂਭੇ ਹੋਏ ਸਮਾਗਮ",
    savedIntro: "ਉਹ ਸਮਾਗਮ ਜੋ ਤੁਸੀਂ ਬਾਅਦ ਵਿੱਚ ਵੇਖਣ ਲਈ ਸਾਂਭੇ ਹਨ।",
    savedEmpty: "ਤੁਸੀਂ ਅਜੇ ਕੋਈ ਸਮਾਗਮ ਨਹੀਂ ਸਾਂਭਿਆ ਹੈ।",
    allEventsTitle: "ਸਾਰੇ ਆਉਣ ਵਾਲੇ ਭਾਈਚਾਰਕ ਮੌਕੇ",

    municipalities: {
      all: "ਸਾਰੇ ਸ਼ਹਿਰ",
      toronto: "ਟੋਰਾਂਟੋ",
      mississauga: "ਮਿਸੀਸਾਗਾ",
      brampton: "ਬ੍ਰੈਂਪਟਨ",
      markham: "ਮਾਰਖਮ",
      vaughan: "ਵੌਨ",
      richmond_hill: "ਰਿਚਮੰਡ ਹਿੱਲ",
      oakville: "ਓਕਵਿਲ",
      burlington: "ਬਰਲਿੰਗਟਨ",
      hamilton: "ਹੈਮਿਲਟਨ",
    },

    categories: {
      arts: "ਕਲਾ ਅਤੇ ਸੱਭਿਆਚਾਰ",
      community: "ਭਾਈਚਾਰਕ ਅਤੇ ਨਾਗਰਿਕ",
      health: "ਸਿਹਤ ਅਤੇ ਤੰਦਰੁਸਤੀ",
      education: "ਸਿੱਖਿਆ ਅਤੇ ਹੁਨਰ",
      seniors: "ਬਜ਼ੁਰਗ (60+)",
      newcomers: "ਨਵੇਂ ਆਏ (Newcomers)",
    },

    notifyFamily: "ਪਰਿਵਾਰਕ ਟਿਊਟਰ (ਕਾਰਲੋਸ) ਨੂੰ ਸੂਚਿਤ ਕਰੋ",
    notifiedFamily: "ਵਟਸਐਪ ਰਾਹੀਂ ਕਾਰਲੋਸ ਨੂੰ ਸੂਚਿਤ ਕੀਤਾ ਗਿਆ",
  },
};

