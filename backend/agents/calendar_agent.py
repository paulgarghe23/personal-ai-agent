"""Agente especializado en gestión de calendario."""
from langchain.agents import create_agent
from backend.tools.calendar_tools import get_calendar_events, get_reminders

# Crea el agente especializado en calendario
calendar_agent = create_agent(
    model="gpt-4o-mini",
    tools=[get_calendar_events, get_reminders],
    system_prompt="""Eres un asistente especializado en gestión de calendarios. 
    Tu función es ayudar al usuario con sus eventos y recordatorios.
    Cuando el usuario pregunta por eventos, siempre incluye los calendarios: 
    Paul (todas las tareas) y Eventos(solamente algunos eventos a los que asistirá presencialmente)).
    Proporciona información clara y útil sobre eventos, horarios y descripciones.
    Normalmente, los eventos importantes son entre las 6:00h y las 23:59h. Los que están de madrugada suelen haber sido descartados, 
    no hace falta que los incluyas a menos que el usuario lo pida explicitamente.""",
)

