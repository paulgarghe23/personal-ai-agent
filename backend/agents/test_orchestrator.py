"""Script de prueba para el orquestador."""
import logging
import sys
from langchain_core.messages import HumanMessage
from backend.agents.orchestrator import create_orchestrator
from dotenv import load_dotenv

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(message)s',
)

# Cargar variables de entorno
load_dotenv()

# Crear orquestador
orchestrator = create_orchestrator()

# Prueba
if __name__ == "__main__":
    print("\n=== PRUEBA ORQUESTADOR ===")
    
    # Mensaje de prueba
    result = orchestrator.invoke({
        "messages": [HumanMessage(content="¿Qué eventos tengo este miércoles? Dime todo lo relevante que tengo ese día")]
    })
    
    # Mostrar respuesta
    print("\n📝 Respuesta:")
    print(result["messages"][-1].content)

