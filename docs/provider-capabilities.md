# Capacidades dos adaptadores de provedores

Esta matriz descreve **o que os adaptadores locais conseguem representar**, não uma validação dos serviços ou de todos os modelos. A seleção de um modelo continua sujeita às capacidades publicadas pelo respectivo provedor.

| Provedor/adaptador | Texto | Imagem | Tools | Structured output | Temperature | Top-p | Seed | Máx. tokens | Tool result | Paralelas | Limitações conhecidas |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|---:|---|
| OpenAI Responses | Sim | Sim | Sim | Sim | Sim | Sim | Não | Sim | `function_call_output` | Sim | O adaptador não representa seed. |
| Anthropic Messages | Sim | Sim | Sim | Não | Sim | Sim | Não | Sim | bloco `tool_result` | Sim | Sem schema nativo de structured output e sem seed. |
| Google Gemini | Sim | Sim | Sim | Sim | Sim | Sim | Não | Sim | parte `functionResponse` | Sim | O adaptador não representa seed. |
| xAI Grok Chat Completions | Sim | Condicional ao modelo | Sim | Sim | Sim | Sim | Sim | Sim | mensagem role `tool` | Sim | A aceitação de imagem depende do modelo selecionado. |

Parâmetros marcados como não suportados são omitidos, e não emulados. Texto e imagens base64 são preservados nos blocos nativos. As definições JSON Schema, solicitações e resultados de tools são normalizados na fronteira do provedor; o orquestrador continua o ciclo até texto final ou limite configurado.

**Validação online dos provedores: não executada.** Os testes usam transportes mockados e nenhuma credencial real.
