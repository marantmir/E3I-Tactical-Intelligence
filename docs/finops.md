# FinOps, retry e fallback de LLM

## Política de decisão

A aplicação prioriza regras determinísticas, algoritmos tradicionais, busca local e pesquisa operacional. LLM só deve ser habilitada quando esses meios forem insuficientes. Sem credenciais, o comportamento local é preservado.

`FinOpsConfig` centraliza provedor, modelo, temperature, top-p, seed, máximo de tokens, timeout, retries, máximo de iterações/tools/frames, limites de contexto e resultado e ordem de fallback. Os padrões são conservadores; `fallback_order=()` desabilita fallback remoto.

## Retry

Cada adaptador repete somente `timeout`, falha `temporary` e `rate_limit`, com no máximo três retries configuráveis e backoff de 10–40 ms. Autenticação, argumento inválido, bloqueio de segurança e schema inválido não são repetidos.

## Fallback

A ordem é explícita e somente adaptadores com credencial entram na rota. `max_attempts` limita provedores consultados. O contexto normalizado é reutilizado sem inserir segredos ou mensagens de erro. Falhas transitórias permitem o próximo provedor; falhas não transitórias interrompem a cadeia. A causa de autenticação é registrada de forma sanitizada. Eventos registram provedor inicial/final e o último recurso é uma resposta determinística local.

Não há fallback remoto quando a ordem não foi configurada. Não se simula sucesso para capacidades ausentes: a matriz documenta a limitação e o parâmetro incompatível é omitido.
