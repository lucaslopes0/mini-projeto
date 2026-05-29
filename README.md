# G8 — Avaliação e Benchmarks para Sistemas Agênticos

> Trabalho Final — Sessão de Painéis sobre Agentes de IA  
> Disciplina: Agentes de IA | Sprint 2 — Checkpoint 2

## 👥 Equipe

| Integrante | GitHub | Responsabilidade |
|---|---|---|
| Lucas Lopes | @lucas-lopes | Coordenação, revisão bibliográfica |
| Carlos Roberto | @carlos-roberto | Setup do ambiente e integração com API |
| Eduardo Henrique | @eduardo-henrique | Execução dos experimentos |
| Henry Vitor | @henry-vitor | Análise de métricas e visualizações |
| Rodrigo Abreu | @rodrigo-abreu | Design do painel A1 |

---

## 🎯 Objetivo

Avaliar a capacidade de um agente LLM (GPT-4o) na categoria **OS** do [AgentBench](https://github.com/THUDM/AgentBench), documentando sistematicamente taxa de conclusão, número de passos por tarefa e tipos de erro recorrentes.

O experimento responde à pergunta: **benchmarks estáticos são suficientes para medir capacidade agêntica real?**

---

## 🗂️ Estrutura do Repositório

```
agentbench-g8/
├── src/
│   ├── agent.py          # Loop agêntico principal (ReAct)
│   ├── tasks.py          # Carregamento e parsing das tarefas OS
│   ├── evaluator.py      # Cálculo de métricas (task completion, passos, erros)
│   └── utils.py          # Helpers (logging, formatação de resultados)
├── results/
│   └── run_sample.json   # Exemplo de saída de uma execução
├── docs/
│   └── analysis.md       # Análise qualitativa dos resultados
├── tasks_os_sample.json  # 10 tarefas OS de exemplo (subconjunto público)
├── requirements.txt      # Dependências Python
├── .env.example          # Variáveis de ambiente necessárias
└── README.md
```

---

## ⚙️ Como Rodar

### 1. Pré-requisitos

- Python 3.11+
- Chave de API da OpenAI com acesso ao GPT-4o

### 2. Instalação

```bash
git clone https://github.com/SEU_ORG/agentbench-g8.git
cd agentbench-g8

python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

pip install -r requirements.txt
```

### 3. Configurar variáveis de ambiente

```bash
cp .env.example .env
# Edite o .env e adicione sua OPENAI_API_KEY
```

### 4. Executar o agente

```bash
# Rodar nas 10 tarefas de amostra
python src/agent.py --tasks tasks_os_sample.json --model gpt-4o --max-steps 10

# Rodar uma tarefa específica pelo índice
python src/agent.py --tasks tasks_os_sample.json --task-id 0 --verbose
```

### 5. Ver métricas

```bash
python src/evaluator.py --results results/run_sample.json
```

---

## 📊 Métricas Coletadas

| Métrica | Descrição |
|---|---|
| `task_completion_rate` | % de tarefas concluídas com sucesso |
| `avg_steps` | Média de passos por tarefa |
| `error_rate` | % de tarefas que terminaram em erro |
| `error_types` | Distribuição dos tipos de erro observados |

---

## 📚 Referências Principais

- AgentBench: [arXiv:2308.03688](https://arxiv.org/abs/2308.03688)
- GAIA: [arXiv:2311.12983](https://arxiv.org/abs/2311.12983)
- SWE-bench: [arXiv:2310.06770](https://arxiv.org/abs/2310.06770)
- Survey on Evaluation of LLM-based Agents: [arXiv:2503.16416](https://arxiv.org/abs/2503.16416)

Lista completa no Checkpoint 1 e no painel final.

---

## 📅 Cronograma

| Sprint | Período | Status |
|---|---|---|
| Sprint 1 | 14–21/Mai | ✅ Checkpoint 1 entregue |
| Sprint 2 | 22–28/Mai | 🔄 Em andamento |
| Sprint 3 | 29/Mai–04/Jun | ⬜ Draft do painel |
| Sprint 4 | 05–11/Jun | ⬜ Painel impresso + sessão |
