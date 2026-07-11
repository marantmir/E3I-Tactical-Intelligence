# Deploy Web - E3I Tactical Intelligence

Este projeto e uma aplicacao full-stack:

- frontend React/Vite;
- backend FastAPI;
- processamento de video com OpenCV;
- persistencia local em SQLite;
- camada LLM opcional.

Por isso, o deploy recomendado e via container Docker em um provedor que rode backend Python, como Render, Railway, Fly.io, Azure App Service ou similar.

## Deploy recomendado: Render

### 1. Subir o codigo para o GitHub

O repositorio esperado e:

```text
https://github.com/marantmir/E3I-Tactical-Intelligence
```

Antes do deploy, confirme que os arquivos abaixo estao no repositorio:

```text
Dockerfile
render.yaml
.dockerignore
backend/
frontend/
```

### 2. Criar o servico no Render

1. Acesse o Render.
2. Clique em `New +`.
3. Escolha `Blueprint`.
4. Conecte o repositorio `marantmir/E3I-Tactical-Intelligence`.
5. O Render deve detectar o arquivo `render.yaml`.
6. Confirme a criacao do servico `e3i-tactical-intelligence`.

O `Dockerfile` faz:

1. instala dependencias do frontend;
2. executa `npm run build`;
3. instala dependencias Python;
4. copia o build do frontend para `frontend/dist`;
5. inicia o FastAPI com Uvicorn.

### 3. Variaveis de ambiente

No painel do Render, configure em `Environment`:

```text
OPENAI_API_KEY=...
OPENAI_MODEL=gpt-4.1-mini
E3I_LLM_TIMEOUT_SECONDS=18
ALLOWED_ORIGINS=http://localhost:5173,http://127.0.0.1:5173
VIDEO_UPLOAD_RATE_LIMIT=6
VIDEO_UPLOAD_RATE_WINDOW_SECONDS=300
```

`OPENAI_API_KEY` deve ser criada como secret no painel do provedor. Nao coloque a chave no Git.

`ALLOWED_ORIGINS` restringe o CORS do FastAPI (lista separada por virgula). Em producao, o frontend e servido pelo proprio FastAPI (mesma origem), entao nao e necessario adicionar o dominio publico; a variavel so precisa ser ajustada se o frontend for hospedado separadamente do backend.

`VIDEO_UPLOAD_RATE_LIMIT`/`VIDEO_UPLOAD_RATE_WINDOW_SECONDS` limitam quantos uploads de video cada IP pode enviar por janela de tempo (padrao: 6 a cada 300s), mitigando abuso do custo de CPU do pipeline de visao computacional.

Se preferir parametrizar pela tela do app, acesse:

```text
/future-ai
```

e salve a chave/modelo por la. Para producao, variavel de ambiente e mais segura.

### 4. Health check

O endpoint de saude e:

```text
/api/health
```

Resposta esperada:

```json
{
  "status": "online",
  "service": "E3I Tactical Intelligence",
  "ai_integration": "evidence_assisted",
  "data_source": "public_and_local"
}
```

### 5. URL publica

Apos o build, o Render fornece uma URL semelhante a:

```text
https://e3i-tactical-intelligence.onrender.com
```

Use essa URL para acessar a aplicacao web.

## Persistencia e arquivos

Hoje o app usa SQLite local e salva videos anotados em `backend/media`.

Em ambiente gratuito, alguns provedores usam filesystem efemero. Isso significa:

- historico SQLite pode ser perdido em novo deploy/restart;
- videos anotados podem sumir apos reinicio;
- uploads grandes podem exigir plano com mais CPU/memoria.

Para uso real, recomenda-se:

- configurar disco persistente no provedor, quando disponivel;
- ou migrar SQLite para Postgres;
- ou enviar videos/processados para storage externo, como S3, Azure Blob ou Cloudflare R2.

## Limites de video

O backend aceita videos ate 300 MB:

```text
MAX_UPLOAD_BYTES = 300 MB
```

Para producao, ajuste conforme o plano do provedor. Processamento de video com OpenCV pode exigir CPU e memoria acima do plano gratuito.

## Deploy local via Docker

Para validar localmente:

```powershell
docker build -t e3i-tactical-intelligence .
docker run --rm -p 8000:8000 -e PORT=8000 e3i-tactical-intelligence
```

Com LLM:

```powershell
docker run --rm -p 8000:8000 `
  -e PORT=8000 `
  -e OPENAI_API_KEY="sua_chave" `
  -e OPENAI_MODEL="gpt-4.1-mini" `
  e3i-tactical-intelligence
```

Acesse:

```text
http://127.0.0.1:8000
```

## Checklist antes de publicar

- `npm run build` passando.
- `python -m compileall app` passando no backend.
- `/api/health` respondendo.
- `/future-ai` configurado para LLM, se necessario.
- `backend/data/llm_config.json` fora do Git.
- `OPENAI_API_KEY` configurada apenas como segredo no provedor.

## Troubleshooting

### Frontend nao aparece

Confirme que o build gerou:

```text
frontend/dist/index.html
frontend/dist/assets/
```

### API responde, mas LLM cai em fallback

Verifique:

- `OPENAI_API_KEY`;
- modelo configurado;
- acesso de rede do provedor;
- endpoint `/api/llm/config`;
- botao `Testar LLM` na tela `/future-ai`.

### Upload de video demora ou falha

Reduza:

- frames analisados;
- tamanho do video;
- resolucao do arquivo;
- quantidade de videos simultaneos.

Para uso intensivo, usar plano com mais CPU/memoria.
