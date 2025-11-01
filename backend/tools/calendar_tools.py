"""Herramienta simple para leer Google Calendar."""
import os
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from datetime import datetime

SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']

def get_calendar_events() -> str:
    """Obtiene los próximos 5 eventos del calendario."""
    creds = None
    
    # Buscar token guardado
    if os.path.exists('backend/config/token.json'):
        creds = Credentials.from_authorized_user_file('backend/config/token.json', SCOPES)
    
    # Si no hay, hacer login
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'backend/config/client_secret_627326261971-28tfa9ej19ukolbu3d1ld2o88omlqn4r.apps.googleusercontent.com.json',
                SCOPES)
            creds = flow.run_local_server(port=0)
        
        with open('backend/config/token.json', 'w') as token:
            token.write(creds.to_json())
    
    # Llamar API
    service = build('calendar', 'v3', credentials=creds)
    now = datetime.utcnow().isoformat() + 'Z'
    events = service.events().list(
        calendarId='primary',
        timeMin=now,
        maxResults=5,
        singleEvents=True,
        orderBy='startTime'
    ).execute().get('items', [])
    
    if not events:
        return "No tienes eventos próximos."
    
    result = "Tus próximos eventos:\n"
    for event in events:
        start = event['start'].get('dateTime', event['start'].get('date'))
        result += f"- {start}: {event['summary']}\n"
    
    return result

