#!/usr/bin/env python3
"""
==============================================================================
🏛️ GASTROTEACHER AI ASSISTANT - MASTER QA ORCHESTRATOR & CI/CD PIPELINE
==============================================================================
Ejecuta secuencialmente el ecosistema completo de control de calidad:
1. PyTest Unit & Integration Suite (40 tests con fixtures aislados)
2. Cobertura de Código (Code Coverage >85% en módulos críticos)
3. Pruebas BDD / Gherkin con Behave (Escalamiento y Caché)
4. Pruebas de Mutación (Resiliencia de Umbrales en RAGRetriever)
5. Análisis Estático de Código y Sintaxis con Flake8

Código de salida: 0 si todas las etapas son exitosas, 1 en caso de falla.
"""

from __future__ import annotations
import os
import sys
import time
import subprocess
from pathlib import Path

# Add backend directory to Python path
BACKEND_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BACKEND_DIR))

try:
    from app.utils.sweet_alert_console import SweetAlert
    USE_SWEET_ALERT = True
except Exception:
    USE_SWEET_ALERT = False

def run_command(command: list[str], stage_name: str, cwd: Path = BACKEND_DIR) -> tuple[bool, str, float]:
    """Runs a shell command measuring elapsed time and capturing output."""
    start = time.perf_counter()
    env = os.environ.copy()
    env["PYTHONPATH"] = str(cwd)

    try:
        proc = subprocess.run(
            command,
            cwd=str(cwd),
            env=env,
            capture_output=True,
            text=True,
            check=False
        )
        elapsed = time.perf_counter() - start
        passed = (proc.returncode == 0)
        output = proc.stdout if passed else (proc.stdout + "\n" + proc.stderr)
        return passed, output.strip(), round(elapsed, 2)
    except Exception as e:
        elapsed = time.perf_counter() - start
        return False, str(e), round(elapsed, 2)

def main() -> int:
    start_total = time.perf_counter()
    print("\n" + "=" * 80)
    print(" 🚀 INICIANDO ORQUESTADOR DE PRUEBAS DE CALIDAD - GASTROTEACHER QA ECOSYSTEM")
    print("=" * 80 + "\n")

    stages = [
        {
            "id": "STAGE_1_PYTEST",
            "name": "PyTest Unit & Integration Suite",
            "command": [sys.executable, "-m", "pytest", "tests", "-v", "--cov=app", "--cov-fail-under=85"],
            "description": "40 pruebas unitarias/integración con mocks para Ollama"
        },
        {
            "id": "STAGE_2_BDD",
            "name": "BDD / Gherkin Cucumber Suite (Behave)",
            "command": [sys.executable, "-m", "behave", "qa_ecosystem/bdd/features"],
            "description": "Escenarios Gherkin de Escalamiento Humano y Respuesta desde Caché"
        },
        {
            "id": "STAGE_3_MUTATION",
            "name": "Mutation Testing (Threshold Resilience)",
            "command": [sys.executable, "qa_ecosystem/mutation/mutation_runner.py"],
            "description": "Evaluación de mutantes en app.rag.retriever (score >= 0.20)"
        },
        {
            "id": "STAGE_4_LINTER",
            "name": "Static Code Analysis & Linting (Flake8)",
            "command": [sys.executable, "-m", "flake8", "app", "--count", "--select=E9,F63,F7,F82", "--show-source", "--statistics"],
            "description": "Validación de sintaxis, variables no definidas y errores críticos"
        }
    ]

    results_table = []
    all_passed = True

    for stage in stages:
        print(f"▶️  Ejecutando {stage['name']}...")
        passed, output, duration = run_command(stage["command"], stage["name"])

        status_str = "✅ APROBADO" if passed else "❌ FALLIDO"
        results_table.append([stage["name"], status_str, f"{duration}s", stage["description"]])

        if not passed:
            all_passed = False
            print(f"\n❌ Error en {stage['name']}:\n{output}\n")
        else:
            print(f"   ✓ {stage['name']} completado con éxito en {duration}s.\n")

    total_duration = round(time.perf_counter() - start_total, 2)

    # Render summary table with SweetAlert / Rich
    if USE_SWEET_ALERT:
        SweetAlert.render_summary_table(
            title="Resumen General del Ecosistema de Calidad (QA Pipeline)",
            headers=["Fase de Evaluación", "Resultado", "Tiempo", "Alcance de la Prueba"],
            rows=results_table
        )
    else:
        print("\n" + "=" * 80)
        print(" RESUMEN GENERAL DE CONTROL DE CALIDAD")
        print("=" * 80)
        for row in results_table:
            print(f" • {row[0]:<42} | {row[1]:<12} | {row[2]:<6} | {row[3]}")
        print("=" * 80)

    if all_passed:
        if USE_SWEET_ALERT:
            SweetAlert.success(
                title="¡Ecosistema de Calidad 100% Validado!",
                text="Todas las suites de prueba (PyTest, Coverage >85%, BDD Behave, Mutaciones y Flake8) pasaron satisfactoriamente.",
                details={
                    "Total Fases Ejecutadas": str(len(stages)),
                    "Tiempo Total Pipeline": f"{total_duration} segundos",
                    "Estado CI/CD": "READY FOR PRODUCTION (Exit Code 0)"
                }
            )
        else:
            print(f"\n🎉 ¡TODAS LAS PRUEBAS PASARON SATISFACTORIAMENTE EN {total_duration}s! (Exit Code 0)\n")
        return 0
    else:
        if USE_SWEET_ALERT:
            SweetAlert.error(
                title="Falla en la Verificación de Calidad",
                text="Una o más fases del pipeline no cumplieron los criterios de aceptación.",
                details={
                    "Estado CI/CD": "BUILD FAILED (Exit Code 1)",
                    "Tiempo de Ejecución": f"{total_duration} segundos"
                }
            )
        else:
            print(f"\n⚠️ SE DETECTARON FALLAS EN EL PIPELINE DE CALIDAD. (Exit Code 1)\n")
        return 1

if __name__ == "__main__":
    sys.exit(main())
