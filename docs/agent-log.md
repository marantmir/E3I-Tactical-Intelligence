# Registro do Agente

## Entrega Atual

O agente evoluiu o E3I Tactical Intelligence para uma plataforma de inteligencia tatica com:

- Busca publica e local sobre o time analisado.
- Pre-analise antes do salvamento.
- Endpoints de grafo tatico, leitura visual de videos e inteligencia publica.
- Painel visual de grafo em `Formacoes`.
- Painel de visao computacional em `Fontes, videos e leitura visual`.
- Relatorio final consolidado.
- Documentacao atualizada para a nova arquitetura.

## Decisoes Tecnicas

- Manter FastAPI e React/Vite.
- Evitar novas dependencias para preservar portabilidade.
- Usar Wikimedia como fonte publica aberta quando a rede permitir.
- Manter modo local quando a rede externa estiver indisponivel.
- Separar busca publica, grafo, video e persistencia em modulos independentes.

## Validacoes

- Testes HTTP com `TestClient`.
- Build de frontend com `npm run build`.
- Verificacao visual no navegador local.
- Varredura de textos antigos no codigo e nos dados exibidos.
