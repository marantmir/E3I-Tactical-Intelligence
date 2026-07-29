# Prompts e Direcionamentos

## Direcionamento Principal

Construir e evoluir o E3I Tactical Intelligence como uma aplicacao de analise tatica de futebol com busca publica, pre-analise, grafo tatico, leitura visual de videos, pesquisa operacional, relatorio e historico.

## Iteracoes Relevantes

- Configurar o projeto para o repositorio `marantmir/e3i-tactical-intelligence`.
- Incluir botao `Analisar` antes de salvar a analise.
- Buscar informacoes online sobre o time desejado.
- Resolver problemas de retorno e fallback da busca publica.
- Remover linguagem de dados demonstrativos da interface.
- Implementar analise por grafos.
- Implementar visao computacional visual para videos.
- Aprofundar a analise para apoiar decisao de formacao, estrategia e tatica.

## Criterios de Implementacao

- Entregar experiencia navegavel.
- Manter endpoints claros e testaveis.
- Separar fonte publica, base local e inferencia visual.
- Permitir revisao humana antes do salvamento.
- Priorizar visualizacoes compreensiveis para comissao tecnica.

## Contrato do system prompt

Todo caso de análise deve: (1) usar apenas o contexto entregue; (2) distinguir observação de inferência; (3) informar confiança e evidência faltante; (4) nunca inventar atleta, placar ou evento; e (5) retornar JSON válido. Preferências de idioma/profundidade são anexadas por `_system_with_preferences`, sem substituir as restrições do caso de uso.

## Few-shot multimodal representativo

**Entrada resumida:** quadro em `t=12,4s`; jogadores de uniforme claro concentrados no corredor central; bola não visível; CV estima `formation_guess=4-3-3`, mas há apenas seis rastros confiáveis.

**Saída desejada:**

```json
{
  "visual_observations": [{
    "time_s": 12.4,
    "observation": "Seis jogadores de uniforme claro aparecem compactos no corredor central; a bola não é visível.",
    "evidence": "pixels do quadro anotado",
    "confidence": "media"
  }],
  "cross_check": "O quadro sugere compactação, mas não confirma 4-3-3 porque faltam cinco posições confiáveis.",
  "next_validation": "Revisar um quadro aberto anterior e outro posterior com ao menos dez rastros."
}
```

**Saída rejeitada:** “O camisa 10 João marcou após passe do ponta.” Não há número legível, identidade, bola ou evento que sustente a frase.

## Evolução dos prompts

1. **Versão inicial:** resumia métricas de CV; falhou semanticamente porque era descrita como leitura visual embora nenhuma imagem chegasse ao modelo.
2. **Versão multimodal:** passou a exigir observação por quadro e confronto explícito com as métricas.
3. **Versão com few-shot:** explicita como recusar uma formação quando a cobertura de rastros é insuficiente e como declarar a evidência ausente.

Os prompts originais de solicitação foram conversacionais e continham contexto do repositório; este documento preserva versões representativas, não transcrições literais integrais. A avaliação deve observar o diff, os testes e os artefatos produzidos, e não tratar este resumo como log bruto.
