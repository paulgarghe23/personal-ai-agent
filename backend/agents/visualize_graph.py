"""Script para visualizar el grafo del orquestador."""
import sys
from backend.agents.orchestrator import create_orchestrator

# Fix encoding para Windows
sys.stdout.reconfigure(encoding='utf-8')

# Crea el orquestador
orchestrator = create_orchestrator()

print("\n=== VISUALIZACION DEL GRAFO ===\n")

# Método 1: Diagrama Mermaid (para visualización)
print("Codigo Mermaid (copia esto en https://mermaid.live/):\n")
try:
    mermaid_code = orchestrator.get_graph().draw_mermaid()
    print(mermaid_code)
except AttributeError:
    # Si draw_mermaid no existe, usa otro método
    graph = orchestrator.get_graph()
    print("Grafo creado correctamente!")
    print(f"Nodos: {list(graph.nodes.keys())}")
    
    # Genera diagrama simple
    print("\nDiagrama simple:")
    print("START")
    print("  |")
    print("  v")
    print("decide (analiza pregunta)")
    print("  |")
    print("  v")
    print("calendar_agent (responde)")
    print("  |")
    print("  v")
    print("END")

print("\n" + "="*50)
print("\nTip: Copia el codigo Mermaid y pegarlo en https://mermaid.live/ para ver el diagrama visual")

