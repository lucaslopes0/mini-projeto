"""
evaluator.py — Calcula e exibe métricas a partir dos resultados de uma execução.

Uso:
    python src/evaluator.py --results results/run_results.json
"""

import argparse
import json
from collections import Counter
from pathlib import Path


def load_results(filepath: str) -> dict:
    path = Path(filepath)
    if not path.exists():
        raise FileNotFoundError(f"Arquivo de resultados não encontrado: {filepath}")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def compute_metrics(results: list[dict]) -> dict:
    total = len(results)
    if total == 0:
        return {}

    successful = [r for r in results if r.get("success")]
    failed = [r for r in results if not r.get("success")]

    completion_rate = len(successful) / total * 100
    avg_steps = sum(r["num_steps"] for r in results) / total
    avg_steps_success = (
        sum(r["num_steps"] for r in successful) / len(successful)
        if successful else 0
    )

    # Distribuição de status
    status_counts = Counter(r["status"] for r in results)

    # Distribuição de tipos de erro (apenas tarefas com falha)
    error_types = Counter(
        r["error_type"] for r in results
        if r.get("error_type")
    )

    return {
        "total_tasks": total,
        "successful": len(successful),
        "failed": len(failed),
        "task_completion_rate_%": round(completion_rate, 1),
        "avg_steps_all": round(avg_steps, 2),
        "avg_steps_successful": round(avg_steps_success, 2),
        "status_distribution": dict(status_counts),
        "error_type_distribution": dict(error_types),
    }


def print_report(metadata: dict, metrics: dict):
    print("\n" + "=" * 50)
    print("RELATÓRIO DE AVALIAÇÃO — AgentBench OS")
    print("=" * 50)
    print(f"Modelo:          {metadata.get('model', 'N/A')}")
    print(f"Max steps:       {metadata.get('max_steps', 'N/A')}")
    print(f"Timestamp:       {metadata.get('timestamp', 'N/A')}")
    print("-" * 50)
    print(f"Total de tarefas:        {metrics['total_tasks']}")
    print(f"Tarefas concluídas:      {metrics['successful']}")
    print(f"Tarefas com falha:       {metrics['failed']}")
    print(f"Taxa de conclusão:       {metrics['task_completion_rate_%']}%")
    print(f"Média de passos (geral): {metrics['avg_steps_all']}")
    print(f"Média de passos (êxito): {metrics['avg_steps_successful']}")
    print("-" * 50)
    print("Distribuição de status:")
    for status, count in metrics["status_distribution"].items():
        print(f"  {status}: {count}")
    if metrics["error_type_distribution"]:
        print("Distribuição de erros:")
        for err, count in metrics["error_type_distribution"].items():
            print(f"  {err}: {count}")
    print("=" * 50)


def main():
    parser = argparse.ArgumentParser(description="Calcula métricas de uma execução do agente")
    parser.add_argument("--results", required=True, help="Arquivo JSON com os resultados")
    args = parser.parse_args()

    data = load_results(args.results)
    metadata = data.get("run_metadata", {})
    results = data.get("results", [])

    metrics = compute_metrics(results)
    print_report(metadata, metrics)

    # Salva métricas em arquivo separado
    metrics_path = Path(args.results).parent / "metrics_summary.json"
    with open(metrics_path, "w", encoding="utf-8") as f:
        json.dump({"metadata": metadata, "metrics": metrics}, f, indent=2, ensure_ascii=False)
    print(f"\nMétricas salvas em: {metrics_path}")


if __name__ == "__main__":
    main()
