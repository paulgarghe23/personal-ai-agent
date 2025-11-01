from langchain.agents import create_agent
from langgraph.checkpoint.sqlite import SqliteSaver
from dotenv import load_dotenv
import sys

# 1. Carga API keys desde .env
load_dotenv()

# 2. Define una herramienta simple
def get_weather(city: str) -> str:
    """Obtiene el clima de una ciudad."""
    return f"El clima en {city} es soleado y 25°C"

# 3. Configurar memoria persistente (SQLite)
import sqlite3
conn = sqlite3.connect("memory.db", check_same_thread=False)
memory = SqliteSaver(conn)

# 4. Crea el agente CON MEMORIA
agent = create_agent(
    model="gpt-4o-mini",
    tools=[get_weather],
    system_prompt="Eres un asistente útil. Recuerda lo que te dicen.",
    checkpointer=memory,  # ← CLAVE: Añade memoria
)

# 5. Ejecuta el agente CON thread_id (sesión única)
if __name__ == "__main__":
    thread_id = "user_paul_session"  # ID único por usuario
    
    # Primera conversación
    print("\n=== CONVERSACIÓN 1 ===")
    sys.stdout.flush()  # Fuerza mostrar en debug
    result = agent.invoke(
        {"messages": [{"role": "user", "content": "Hola, me llamo Paul"}]},
        config={"configurable": {"thread_id": thread_id}}  # ← Usa sesión
    )
    print(result["messages"][-1].content)
    sys.stdout.flush()  # Fuerza mostrar en debug
    
    # Segunda conversación (debería recordar)
    print("\n=== CONVERSACIÓN 2 ===")
    sys.stdout.flush()  # Fuerza mostrar en debug
    result = agent.invoke(
        {"messages": [{"role": "user", "content": "¿Cómo me llamo?"}]},
        config={"configurable": {"thread_id": thread_id}}  # ← Misma sesión
    )
    print(result["messages"][-1].content)
    sys.stdout.flush()  # Fuerza mostrar en debug
    