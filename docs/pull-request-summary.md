# Problema

A entrega precisava demonstrar, com evidência reproduzível, tool calling nativo,
grounding estruturado, integrações seguras, experimentos offline e qualidade do
repositório, sem confundir mocks com validação online.

# Alterações por commit

- `8132e04`: baseline e quality gate.
- `9a6160a`: orquestração modelo→tool→modelo.
- `5974b64`/`8649e34`: seis tools táticas e evidência.
- `b3ae46e`/`881f9aa`/`55fa93e`/`0b34200`: vídeo público, formatos e filtragem.
- `f675635`: quatro adaptadores e fallback resiliente.
- `9237f3b`/`4c7ca99`: prompt runtime e schema grounded.
- `b429779`: experimentos offline reproduzíveis.
- `13103b7`: hardening, guard de rede e documentação as-built.
- commit final: auditoria, evidências e preparação da apresentação/PR.

# Testes e experimentos

O gate completo aprovou 535 testes Python, 1 teste frontend, compileall, build
Vite, lints, scanners, links e checks de dependências. O runner offline concluiu
20 casos e regenerou JSON, CSV e Markdown. Provedores reais não foram chamados.

# Segurança

Schemas fechados, allowlist, limites, timeouts, erros sanitizados, validação de
DNS/redirect, scanner de segredos e arquivos sensíveis são verificados localmente.
A auditoria npm local é offline e não substitui uma consulta CVE atualizada.

# Limitações

O Python padrão deste contêiner não possui `httpx`; o gate aprovado reutilizou a
instalação local do Poetry. Deploy, provedores reais, firewall de egress,
multi-instância e apresentação gravada não foram verificados.

# Checklist

- [x] Histórico preservado, sem squash/rebase destrutivo.
- [x] Validação hermética completa executada.
- [x] Experimentos offline e documentação atualizados.
- [x] Segurança e limitações registradas sem alegações absolutas.
- [ ] Push/PR remoto (ambiente sem `origin` e sem GitHub CLI).
- [ ] Gravação e validação humana da apresentação.

# Evidências

Consultar [evidências finais](evaluation-evidence.md), [checklist de avaliação](evaluation-checklist.md)
e [roteiro da apresentação](presentation-script.md).
