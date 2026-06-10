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

    successful   = [r for r in results if r.get("success")]
    completed    = [r for r in results if r.get("status") == "completed"]
    failed       = [r for r in results if not r.get("success")]

    completion_rate  = len(completed)  / total * 100
    success_rate     = len(successful) / total * 100
    avg_steps        = sum(r["num_steps"] for r in results) / total
    avg_steps_ok     = (
        sum(r["num_steps"] for r in successful) / len(successful)
        if successful else 0
    )

    status_counts = Counter(r["status"] for r in results)
    error_types   = Counter(
        r["error_type"] for r in results if r.get("error_type")
    )

    return {
        "total_tasks":              total,
        "completed_status":         len(completed),   # status == completed
        "successful_with_answer":   len(successful),  # success == true
        "failed":                   len(failed),
        "task_completion_rate_%":   round(completion_rate, 1),
        "answer_success_rate_%":    round(success_rate, 1),
        "avg_steps_all":            round(avg_steps, 2),
        "avg_steps_successful":     round(avg_steps_ok, 2),
        "status_distribution":      dict(status_counts),
        "error_type_distribution":  dict(error_types),
    }


def print_report(metadata: dict, metrics: dict):
    print("\n" + "=" * 52)
    print("  RELATÓRIO DE AVALIAÇÃO — AgentBench OS")
    print("=" * 52)
    print(f"  Modelo:     {metadata.get('model', 'N/A')}")
    print(f"  Max steps:  {metadata.get('max_steps', 'N/A')}")
    print(f"  Timestamp:  {metadata.get('timestamp', 'N/A')}")
    print("-" * 52)
    print(f"  Total de tarefas:              {metrics['total_tasks']}")
    print(f"  Finalizaram (sem erro API):    {metrics['completed_status']}")
    print(f"  Responderam corretamente:      {metrics['successful_with_answer']}")
    print(f"  Com falha / erro:              {metrics['failed']}")
    print(f"  Taxa de conclusão (completed): {metrics['task_completion_rate_%']}%")
    print(f"  Taxa de acerto (com gabarito): {metrics['answer_success_rate_%']}%")
    print(f"  Média de passos (geral):       {metrics['avg_steps_all']}")
    print(f"  Média de passos (êxito):       {metrics['avg_steps_successful']}")
    print("-" * 52)
    print("  Distribuição de status:")
    for status, count in metrics["status_distribution"].items():
        pct = count / metrics["total_tasks"] * 100
        print(f"    {status:<22} {count:>2}  ({pct:.0f}%)")
    if metrics["error_type_distribution"]:
        print("  Tipos de erro:")
        for err, count in metrics["error_type_distribution"].items():
            print(f"    {err:<22} {count:>2}")
    print("=" * 52)


def main():
    parser = argparse.ArgumentParser(description="Calcula métricas de uma execução do agente")
    parser.add_argument("--results", required=True, help="Arquivo JSON com os resultados")
    args = parser.parse_args()

    data     = load_results(args.results)
    metadata = data.get("run_metadata", {})
    results  = data.get("results", [])

    metrics = compute_metrics(results)
    print_report(metadata, metrics)

    metrics_path = Path(args.results).parent / "metrics_summary.json"
    with open(metrics_path, "w", encoding="utf-8") as f:
        json.dump({"metadata": metadata, "metrics": metrics}, f, indent=2, ensure_ascii=False)
    print(f"\n  Métricas salvas em: {metrics_path}")


if __name__ == "__main__":
    main()