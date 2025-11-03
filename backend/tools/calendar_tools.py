"""Herramientas para Google Calendar."""
import os
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from datetime import datetime

SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']

def _authenticate():
    """Autentica con Google Calendar."""
    creds = None
    if os.path.exists('backend/config/token.json'):
        creds = Credentials.from_authorized_user_file('backend/config/token.json', SCOPES)
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('backend/config/credentials.json', SCOPES)
            creds = flow.run_local_server(port=0, open_browser=True)
        with open('backend/config/token.json', 'w') as token:
            token.write(creds.to_json())
    return creds

def _filter_by_hour(events, start_hour, end_hour):
    """Filtra eventos por rango de horas."""
    filtered = []
    for event in events:
        start = event['start'].get('dateTime')
        if not start:  # Eventos de todo el día
            continue
        hour = datetime.fromisoformat(start.replace('Z', '+00:00')).hour
        if start_hour <= hour < end_hour:
            filtered.append(event)
    return filtered

def get_calendar_events() -> str:
    """Obtiene TODOS los eventos futuros entre 6h-24h."""
    service = build('calendar', 'v3', credentials=_authenticate())
    now = datetime.utcnow().isoformat() + 'Z'
    events = service.events().list(
        calendarId='primary',
        timeMin=now,
        maxResults=100,
        singleEvents=True,
        orderBy='startTime'
    ).execute().get('items', [])
    
    events = _filter_by_hour(events, 6, 24)
    
    if not events:
        return "No tienes eventos entre 6h-24h."
    
    result = "Eventos futuros (6h-24h):\n"
    for event in events:
        start = event['start'].get('dateTime', event['start'].get('date'))
        result += f"- {start}: {event['summary']}\n"
    return result

def get_reminders() -> str:
    """Obtiene eventos/recordatorios entre 0h-6h."""
    service = build('calendar', 'v3', credentials=_authenticate())
    now = datetime.utcnow().isoformat() + 'Z'
    events = service.events().list(
        calendarId='primary',
        timeMin=now,
        maxResults=100,
        singleEvents=True,
        orderBy='startTime'
    ).execute().get('items', [])
    
    events = _filter_by_hour(events, 0, 6)
    
    if not events:
        return "No tienes recordatorios entre 0h-6h."
    
    result = "Recordatorios (0h-6h):\n"
    for event in events:
        start = event['start'].get('dateTime', event['start'].get('date'))
        result += f"- {start}: {event['summary']}\n"
    return result

