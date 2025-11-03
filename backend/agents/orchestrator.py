"""Orquestador que decide qué agente especializado usar."""
from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
from typing import TypedDict, Annotated
import operator
import json

# Estado compartido entre nodos (como una "caja" que pasa información entre funciones)
class OrchestratorState(TypedDict):
    messages: Annotated[list, operator.add]  # Lista de mensajes que se acumula

# Nodo: Decide qué agente usar (simple paso intermedio)
def decide_node(state: OrchestratorState) -> OrchestratorState:
    """Paso intermedio para analizar el mensaje."""
    return state

# Función: Usa IA para decidir a qué agente redirigir
def route_to_agent(state: OrchestratorState) -> str:
    """Analiza la pregunta con IA y decide qué agente usar."""
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    
    last_message = state["messages"][-1].content
    
    # Pide a la IA que analice la pregunta
    prompt = """Analiza esta pregunta y decide qué agente debe manejarla.

Agentes disponibles:
- calendar_agent: calendario, eventos, reuniones, citas, recordatorios

Responde solo en formato: "X_agent"

Pregunta: {question}"""

    response = llm.invoke([HumanMessage(content=prompt.format(question=last_message))])
    agent_choice = response.content.strip().lower()
    
    # Retorna el agente elegido
    if "calendar" in agent_choice:
        return "calendar_agent"
    return "calendar_agent"  # Por defecto

# Nodo: Ejecuta el agente de calendario
def calendar_agent_node(state: OrchestratorState) -> OrchestratorState:
    """Ejecuta el agente especializado en calendario."""
    from backend.agents.calendar_agent import calendar_agent
    
    result = calendar_agent.invoke(state)
    return {"messages": result["messages"]}

# Construye el grafo
def create_orchestrator():
    """Crea el grafo orquestador."""
    graph = StateGraph(OrchestratorState)
    
    # Añade nodos
    graph.add_node("decide", decide_node)
    graph.add_node("calendar_agent", calendar_agent_node)
    
    # Añade ruta de decisión
    graph.add_conditional_edges(
        "decide",
        route_to_agent,
        {
            "calendar_agent": "calendar_agent",
        }
    )
    
    # Define entrada y salida
    graph.set_entry_point("decide")
    graph.add_edge("calendar_agent", END)
    
    return graph.compile()

