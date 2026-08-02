# Roadmap de decisão tática avançada

O estado entregue (upload, CV/tracking heurístico, grafos, otimização de escalação, tools e fallback) está descrito na [arquitetura as-built](architecture.md), não como trabalho futuro.

## Próximas evoluções ainda não implementadas

- Integração licenciada com API esportiva para estatísticas atualizadas, com contrato, orçamento e termos aprovados.
- Exportação PDF acessível do relatório com anexos e cadeia de evidências.
- Detector supervisionado calibrado em dataset autorizado, somente se superar a heurística em benchmark definido.
- Persistência compartilhada, fila durável, rate limit distribuído e egress firewall antes de escala multi-instância.
- Avaliação online dos quatro provedores com corpus congelado, orçamento e credenciais geridas fora do repositório.

## Critérios de aceite

Cada evolução deve separar observação/inferência, preservar revisão humana, registrar proveniência e limitações, incluir teste hermético e não introduzir segredo versionado. Componentes online também precisam de timeout, limite, política de retry/fallback, auditoria de custo e teste de segurança de saída.
