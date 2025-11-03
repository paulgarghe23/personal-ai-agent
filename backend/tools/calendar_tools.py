"""Herramientas para Google Calendar."""
import logging
import os
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from datetime import datetime

logger = logging.getLogger(__name__)

SCOPES = ['https://www.googleapis.com/auth/calendar']  # Lectura Y escritura

def _authenticate():
    """Autentica con Google Calendar."""
    creds = None
    if os.path.exists('backend/config/token.json'):
        logger.info("📁 Token encontrado, cargando credenciales...")
        creds = Credentials.from_authorized_user_file('backend/config/token.json', SCOPES)
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            logger.info("🔄 Token expirado, refrescando automáticamente...")
            creds.refresh(Request())
        else:
            logger.info("🔐 No hay credenciales válidas, iniciando login en navegador...")
            flow = InstalledAppFlow.from_client_secrets_file('backend/config/credentials.json', SCOPES)
            creds = flow.run_local_server(port=0, open_browser=True)
        with open('backend/config/token.json', 'w') as token:
            token.write(creds.to_json())
        logger.info("✅ Credenciales guardadas correctamente")
    else:
        logger.info("✅ Credenciales válidas, usando token existente")
    return creds

def _get_calendar_ids(service):
    """Obtiene IDs de calendarios por nombre."""
    calendar_list = service.calendarList().list().execute()
    all_calendars = calendar_list.get('items', [])
    logger.info(f"📋 Google devolvió {len(all_calendars)} calendarios totales:")
    
    calendars = []
    
    for calendar in all_calendars:
        cal_name = calendar['summary']
        cal_id = calendar['id']
        logger.info(f"   - {cal_name}")
        
        # Busca calendarios específicos
        if calendar.get('primary'):
            calendars.append((cal_id, 'Paul'))
        elif cal_name == 'Eventos':
            calendars.append((cal_id, 'Eventos'))
    
    logger.info(f"📅 Calendarios seleccionados para uso: {[name for _, name in calendars]}")
    return calendars

def _log_events_preview(events, label=""):
    """Muestra preview de primeros 3 eventos para debugging."""
    if not events:
        logger.info(f"📭 {label}: Sin eventos")
        return
    
    logger.info(f"📊 {label}: {len(events)} eventos totales")
    preview = []
    for i, event in enumerate(events[:3], 1):
        start = event['start'].get('dateTime', event['start'].get('date'))
        summary = event.get('summary', '(sin título)')
        description = event.get('description', '')
        desc_preview = f" | {description[:50]}..." if description else ""
        preview.append(f"  {i}. {start} - {summary}{desc_preview}")
    if preview:
        logger.info("\n".join(preview))
    if len(events) > 3:
        logger.info(f"  ... y {len(events) - 3} eventos más")

def _filter_by_hour(events, start_hour, end_hour):
    """Filtra eventos por rango de horas."""
    filtered = []
    for event in events:
        start = event['start'].get('dateTime')
        
        # Eventos de todo el día: solo en eventos normales (6h-24h)
        if not start:
            if start_hour == 6:
                filtered.append(event)
            continue  # Salta verificación de hora
        
        # Eventos con hora específica
        hour = datetime.fromisoformat(start.replace('Z', '+00:00')).hour
        if start_hour <= hour < end_hour:
            filtered.append(event)
    return filtered

def get_calendar_events() -> str:
    """Obtiene TODOS los eventos futuros entre 6h-24h de Paul y Eventos."""
    service = build('calendar', 'v3', credentials=_authenticate())
    now = datetime.utcnow().isoformat() + 'Z'
    
    # Obtiene calendarios dinámicamente
    calendars = _get_calendar_ids(service)
    
    all_events = []
    for cal_id, cal_name in calendars:
        logger.info(f"🔍 Obteniendo eventos del calendario '{cal_name}'...")
        events = service.events().list(
            calendarId=cal_id,
            timeMin=now,
            maxResults=200,
            singleEvents=True,
            orderBy='startTime'
        ).execute().get('items', [])
        
        # Añade nombre del calendario a cada evento
        for event in events:
            event['_calendar'] = cal_name
        all_events.extend(events)
    
    # Filtra por hora
    logger.info(f"🔧 Filtrando eventos entre 6h-24h...")
    all_events = _filter_by_hour(all_events, 6, 24)
    _log_events_preview(all_events, "Eventos filtrados 6h-24h")
    
    # Ordena por fecha
    all_events.sort(key=lambda e: e['start'].get('dateTime', e['start'].get('date')))
    
    if not all_events:
        return "No tienes eventos entre 6h-24h."
    
    result = "Eventos futuros (6h-24h):\n"
    for event in all_events:
        start = event['start'].get('dateTime', event['start'].get('date'))
        cal_name = event.get('_calendar', '?')
        summary = event.get('summary', '(sin título)')
        description = event.get('description', '')
        result += f"- [{cal_name}] {start}: {summary}"
        if description:
            result += f"\n  Descripción: {description}"
        result += "\n"
    return result

def get_reminders() -> str:
    """Obtiene eventos/recordatorios entre 0h-6h de Paul y Eventos."""
    service = build('calendar', 'v3', credentials=_authenticate())
    now = datetime.utcnow().isoformat() + 'Z'
    
    # Obtiene calendarios dinámicamente
    calendars = _get_calendar_ids(service)
    
    all_events = []
    for cal_id, cal_name in calendars:
        logger.info(f"🔍 Obteniendo eventos del calendario '{cal_name}'...")
        events = service.events().list(
            calendarId=cal_id,
            timeMin=now,
            maxResults=100,
            singleEvents=True,
            orderBy='startTime'
        ).execute().get('items', [])
        
        # Añade nombre del calendario a cada evento
        for event in events:
            event['_calendar'] = cal_name
        all_events.extend(events)
    
    # Filtra por hora
    logger.info(f"🔧 Filtrando eventos entre 0h-6h...")
    all_events = _filter_by_hour(all_events, 0, 6)
    _log_events_preview(all_events, "Eventos filtrados 0h-6h")
    
    # Ordena por fecha
    all_events.sort(key=lambda e: e['start'].get('dateTime', e['start'].get('date')))
    
    if not all_events:
        return "No tienes recordatorios entre 0h-6h."
    
    result = "Recordatorios (0h-6h):\n"
    for event in all_events:
        start = event['start'].get('dateTime', event['start'].get('date'))
        cal_name = event.get('_calendar', '?')
        summary = event.get('summary', '(sin título)')
        description = event.get('description', '')
        result += f"- [{cal_name}] {start}: {summary}"
        if description:
            result += f"\n  Descripción: {description}"
        result += "\n"
    return result