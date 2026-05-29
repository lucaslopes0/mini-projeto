# Análise dos Resultados — AgentBench OS (Sprint 2)

> Estado: rascunho inicial | Atualizado em: 28/Mai/2026

---

## 1. Visão Geral da Execução

| Parâmetro | Valor |
|---|---|
| Modelo avaliado | GPT-4o |
| Categoria do benchmark | OS (Operating System) |
| Total de tarefas | 10 |
| Max. passos por tarefa | 10 |
| Data da execução | 28/05/2026 |

---

## 2. Métricas Principais

| Métrica | Resultado |
|---|---|
| Taxa de conclusão | **80%** (8/10 tarefas) |
| Média de passos (geral) | 3,4 |
| Média de passos (tarefas bem-sucedidas) | 2,6 |
| Tarefas com falha | 2 |

---

## 3. Distribuição de Status

| Status | Qtd | % |
|---|---|---|
| `completed` | 8 | 80% |
| `max_steps_reached` | 1 | 10% |
| `invalid_action` | 1 | 10% |

---

## 4. Análise Qualitativa das Falhas

### Tarefa 7 — `max_steps_reached`
**Instrução:** encontrar arquivos `.py` em `/usr/lib` contendo `import` na primeira linha.

**Problema observado:** o agente entrou em loop tentando variações do `grep` sem nunca converge para uma resposta. A tarefa exige encadeamento de comandos (`find` + `head` + `grep`) que o modelo tentou resolver em passos separados, perdendo contexto entre iterações.

**Hipótese:** tarefas que requerem pipelines multi-comando com filtragem encadeada são mais difíceis para o padrão ReAct simples adotado.

### Tarefa 8 — `invalid_action`
**Instrução:** identificar o processo com maior consumo de CPU.

**Problema observado:** o modelo retornou um bloco de raciocínio sem seguir o formato `ACTION: bash / ANSWER` esperado, gerando um parse inválido após 3 tentativas.

**Hipótese:** ambiguidade no prompt para tarefas que parecem "respondíveis sem bash" (o modelo tentou dar uma resposta direta sem executar nenhum comando).

---

## 5. Observações sobre o Padrão ReAct

O loop agêntico implementado segue o padrão **ReAct** (Reason + Act), onde o modelo intercala raciocínio (THOUGHT) com ações (ACTION) e incorpora observações do ambiente na próxima iteração.

Pontos positivos observados:
- Tarefas simples de 1–2 comandos foram resolvidas de forma consistente.
- O agente soube usar `cat`, `ls`, `wc -l`, `df -h` e `whoami` corretamente.
- Criação de arquivos e scripts simples funcionou bem (tarefas 2, 5, 9).

Limitações identificadas:
- Tarefas com pipelines complexos degradam rapidamente (tarefa 7).
- Sensibilidade ao formato da resposta: desvios do template causam falha de parse (tarefa 8).
- Sem memória persistente entre tarefas — cada execução é independente.

---

## 6. Próximos Passos (Sprint 3)

- [ ] Executar o conjunto completo de tarefas (não apenas amostra de 10)
- [ ] Comparar resultados com os reportados no paper original do AgentBench
- [ ] Gerar gráficos: distribuição de passos, taxa de erro por tipo de tarefa
- [ ] Redigir discussão sobre limitações dos benchmarks estáticos vs. agênticos
- [ ] Iniciar montagem do painel A1

---

## 7. Referências

- LIU, X. et al. AgentBench: Evaluating LLMs as Agents. ICLR 2024. arXiv:2308.03688.
- YAO, S. et al. ReAct: Synergizing Reasoning and Acting in Language Models. ICLR 2023. arXiv:2210.03629.
