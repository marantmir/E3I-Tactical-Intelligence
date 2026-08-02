# Resultado mais recente dos experimentos offline

- Data: `2026-08-02T00:00:00Z`
- Branch: `fix/final-evaluation-compliance`
- Commit base: `44c2cbc`
- Duração: `0 ms`
- Experimentos online: não executados.

## Configuração

```json
{
  "fallback": "local-rule-v1",
  "mock_model": "deterministic-tactical-mock-v1",
  "online_experiments": false,
  "seed": 20260802
}
```

## Casos

| ID | Cenário | Variante | Esperado = obtido |
|---|---|---|---|
| `few-shot-off` | few_shot | without | sim |
| `few-shot-on` | few_shot | with | sim |
| `schema-off` | schema | without | sim |
| `schema-on` | schema | with | sim |
| `tool-off` | tool_usage | without | sim |
| `tool-on` | tool_usage | with | sim |
| `one-tool` | tool_sequence | one | sim |
| `two-tools` | tool_sequence | two_sequential | sim |
| `evidence-insufficient` | evidence | insufficient | sim |
| `evidence-sufficient` | evidence | sufficient | sim |
| `response-normal` | timeout | normal | sim |
| `response-timeout` | timeout | timeout | sim |
| `local-fallback` | engine | local | sim |
| `mock-model` | engine | mock | sim |
| `config-conservative` | configuration | conservative | sim |
| `config-creative` | configuration | creative | sim |
| `tool-valid` | tool_validity | valid | sim |
| `tool-missing` | tool_validity | missing | sim |
| `response-complete` | semantic_completeness | complete | sim |
| `response-incomplete` | semantic_completeness | incomplete | sim |

## Métricas

```json
{
  "average_iterations": 1.3,
  "completion_rate": 0.8,
  "correct_conflict_signaling_rate": 1.0,
  "correct_tool_usage_rate": 0.95,
  "errors_by_scenario": {
    "configuration": 0,
    "engine": 0,
    "evidence": 0,
    "few_shot": 0,
    "schema": 0,
    "semantic_completeness": 0,
    "timeout": 0,
    "tool_sequence": 0,
    "tool_usage": 0,
    "tool_validity": 0
  },
  "fallback_rate": 0.2,
  "grounding_rate": 0.85,
  "offline_latency_ms": 0,
  "schema_adherence_rate": 0.95,
  "valid_response_rate": 0.95
}
```

## Limitações

- Resultados medem um modelo determinístico e regras locais, não a qualidade de provedores reais.
- Latência é duração lógica offline normalizada; não representa latência de rede.
