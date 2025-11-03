from langchain.agents import create_agent
from langgraph.checkpoint.sqlite import SqliteSaver
from dotenv import load_dotenv
import logging
import sys
from backend.tools.calendar_tools import get_calendar_events, get_reminders

# Configurar logging para ver todo el proceso
logging.basicConfig(
    level=logging.INFO,
    format='%(message)s',
    datefmt='%H:%M:%S'
)

# 1. Carga API keys desde .env
load_dotenv()

# 2. Configurar memoria persistente (SQLite)
import sqlite3
conn = sqlite3.connect("memory.db", check_same_thread=False)
memory = SqliteSaver(conn)

# 3. Crea el agente SIN MEMORIA (temporal para probar Calendar)
agent = create_agent(
    model="gpt-4o-mini",
    tools=[get_calendar_events, get_reminders],
    system_prompt="Eres un asistente útil.",
    # checkpointer=memory,  # ← Deshabilitado temporalmente
)

# 4. Ejecuta el agente CON thread_id (sesión única)
if __name__ == "__main__":
    thread_id = "calendar_test_session"  # ID único por usuario
    
    # Prueba Calendar
    print("\n=== PRUEBA CALENDAR ===")
    sys.stdout.flush()
    result = agent.invoke(
        {"messages": [{"role": "user", "content": "¿Qué tareas tengo próximamente en mis calendarios?"}]}
    )
    print(result["messages"][-1].content)
    sys.stdout.flush()
    