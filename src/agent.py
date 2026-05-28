"""
agent.py — Loop agêntico principal (padrão ReAct)

Avalia GPT-4o em tarefas OS do AgentBench.
Uso:
    python src/agent.py --tasks tasks_os_sample.json --model gpt-4o --max-steps 10
    python src/agent.py --tasks tasks_os_sample.json --task-id 0 --verbose
"""

import argparse
import json
import os
import subprocess
import time
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI

from tasks import load_tasks
from utils import get_logger, save_results

load_dotenv()
logger = get_logger(__name__)

SYSTEM_PROMPT = """Você é um agente que executa tarefas em um ambiente de linha de comando Linux.

A cada passo você deve responder EXATAMENTE em um destes formatos:

THOUGHT: <seu raciocínio sobre o próximo passo>
ACTION: bash
```
<comando bash a executar>
```

ou, quando tiver a resposta final:

THOUGHT: <raciocínio final>
ANSWER: <resposta final>

Regras:
- Execute apenas um comando por vez.
- Não invente saídas; baseie-se apenas no que o ambiente retornar.
- Se um comando falhar, tente uma abordagem diferente.
- Quando tiver certeza da resposta, use ANSWER para finalizar.
"""


def parse_action(response_text: str) -> tuple[str, str | None]:
    """
    Extrai o tipo de ação e o conteúdo da resposta do modelo.
    Retorna: ('bash', comando) | ('answer', resposta) | ('invalid', None)
    """
    text = response_text.strip()

    if "ANSWER:" in text:
        answer = text.split("ANSWER:")[-1].strip()
        return "answer", answer

    if "ACTION: bash" in text and "```" in text:
        try:
            command = text.split("```")[1].strip()
            if command.startswith("bash\n"):
                command = command[5:]
            return "bash", command
        except IndexError:
            return "invalid", None

    return "invalid", None


def execute_bash(command: str, timeout: int = 10) -> str:
    """Executa um comando bash e retorna stdout+stderr combinados."""
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        output = result.stdout
        if result.stderr:
            output += f"\n[stderr]: {result.stderr}"
        return output.strip() or "(sem saída)"
    except subprocess.TimeoutExpired:
        return "[ERRO]: comando excedeu o tempo limite"
    except Exception as e:
        return f"[ERRO]: {e}"


def run_task(client: OpenAI, task: dict, model: str, max_steps: int, verbose: bool) -> dict:
    """
    Executa uma única tarefa e retorna o resultado com métricas.
    """
    task_id = task["id"]
    instruction = task["instruction"]
    expected = task.get("expected_answer", "")

    logger.info(f"[Tarefa {task_id}] {instruction[:80]}...")

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": f"Tarefa: {instruction}"},
    ]

    steps = []
    status = "max_steps_reached"
    final_answer = None
    error_type = None

    for step_num in range(1, max_steps + 1):
        try:
            response = client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=0,
                max_tokens=512,
            )
            reply = response.choices[0].message.content
        except Exception as e:
            logger.error(f"  Erro na API: {e}")
            status = "api_error"
            error_type = "api_error"
            break

        action_type, content = parse_action(reply)

        if verbose:
            print(f"\n--- Passo {step_num} ---")
            print(reply)

        if action_type == "answer":
            final_answer = content
            status = "completed"
            steps.append({"step": step_num, "type": "answer", "content": content})
            break

        elif action_type == "bash":
            observation = execute_bash(content)
            steps.append({
                "step": step_num,
                "type": "bash",
                "command": content,
                "observation": observation,
            })
            if verbose:
                print(f"[obs]: {observation}")

            messages.append({"role": "assistant", "content": reply})
            messages.append({"role": "user", "content": f"Observação:\n{observation}"})

        else:
            logger.warning(f"  Passo {step_num}: resposta inválida do modelo.")
            status = "invalid_action"
            error_type = "invalid_action"
            steps.append({"step": step_num, "type": "invalid", "content": reply})
            break

        time.sleep(0.3)  # evita rate limit

    # Avalia se a resposta está correta (comparação simples de string)
    success = False
    if status == "completed" and expected:
        success = expected.strip().lower() in (final_answer or "").lower()
    elif status == "completed":
        success = True  # sem gabarito, considera concluída

    return {
        "task_id": task_id,
        "instruction": instruction,
        "expected_answer": expected,
        "final_answer": final_answer,
        "status": status,
        "success": success,
        "num_steps": len(steps),
        "error_type": error_type,
        "steps": steps,
    }


def main():
    parser = argparse.ArgumentParser(description="Agente GPT-4o no AgentBench OS")
    parser.add_argument("--tasks", required=True, help="Arquivo JSON com as tarefas")
    parser.add_argument("--model", default="gpt-4o", help="Modelo OpenAI a usar")
    parser.add_argument("--max-steps", type=int, default=10, help="Máx. de passos por tarefa")
    parser.add_argument("--task-id", type=int, default=None, help="Rodar só uma tarefa (índice)")
    parser.add_argument("--output", default="results/run_results.json", help="Arquivo de saída")
    parser.add_argument("--verbose", action="store_true", help="Imprime cada passo")
    args = parser.parse_args()

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise EnvironmentError("OPENAI_API_KEY não encontrada. Configure o arquivo .env")

    client = OpenAI(api_key=api_key)
    tasks = load_tasks(args.tasks)

    if args.task_id is not None:
        tasks = [tasks[args.task_id]]

    logger.info(f"Iniciando avaliação: {len(tasks)} tarefa(s) | modelo: {args.model} | max_steps: {args.max_steps}")

    all_results = []
    for task in tasks:
        result = run_task(client, task, args.model, args.max_steps, args.verbose)
        all_results.append(result)
        status_icon = "✅" if result["success"] else "❌"
        logger.info(f"  {status_icon} Tarefa {result['task_id']}: {result['status']} em {result['num_steps']} passos")

    output = {
        "run_metadata": {
            "model": args.model,
            "max_steps": args.max_steps,
            "timestamp": datetime.now().isoformat(),
            "total_tasks": len(all_results),
        },
        "results": all_results,
    }

    save_results(output, args.output)
    logger.info(f"\nResultados salvos em: {args.output}")

    # Resumo rápido no terminal
    completed = sum(1 for r in all_results if r["success"])
    print(f"\n{'='*40}")
    print(f"Tarefas: {len(all_results)} | Sucesso: {completed} | Taxa: {completed/len(all_results)*100:.1f}%")
    print(f"{'='*40}")


if __name__ == "__main__":
    main()
