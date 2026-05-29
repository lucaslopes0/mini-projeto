"""
tasks.py — Carregamento e parsing das tarefas OS do AgentBench.
"""

import json
from pathlib import Path


def load_tasks(filepath: str) -> list[dict]:
    """
    Carrega tarefas de um arquivo JSON.
    Espera uma lista de objetos com ao menos os campos:
        - id: identificador único
        - instruction: instrução em linguagem natural
        - expected_answer (opcional): gabarito para avaliação automática
    """
    path = Path(filepath)
    if not path.exists():
        raise FileNotFoundError(f"Arquivo de tarefas não encontrado: {filepath}")

    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    if not isinstance(data, list):
        raise ValueError("O arquivo de tarefas deve conter uma lista JSON.")

    validated = []
    for i, task in enumerate(data):
        if "instruction" not in task:
            raise ValueError(f"Tarefa no índice {i} não tem campo 'instruction'.")
        task.setdefault("id", i)
        task.setdefault("expected_answer", "")
        validated.append(task)

    return validated
