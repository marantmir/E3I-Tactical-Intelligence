from __future__ import annotations

from datetime import datetime, timezone
import json
import re
import urllib.error
import urllib.parse
import urllib.request

from .llm_config import DEFAULT_LLM_CONFIG, PROVIDER_DEFAULT_MODELS, get_llm_runtime_config


OPENAI_RESPONSES_URL = "https://api.openai.com/v1/responses"
ANTHROPIC_MESSAGES_URL = "https://api.anthropic.com/v1/messages"
ANTHROPIC_VERSION = "2023-06-01"
GOOGLE_GEMINI_URL_TEMPLATE = "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
XAI_CHAT_COMPLETIONS_URL = "https://api.x.ai/v1/chat/completions"
DEFAULT_MODEL = PROVIDER_DEFAULT_MODELS["openai_responses"]
DEFAULT_TIMEOUT_SECONDS = 18


def llm_status() -> dict:
    config = get_llm_runtime_config()
    api_key = _api_key()
    enabled = bool(config.get("enabled") and api_key)
    return {
        "enabled": enabled,
        "configured": bool(config.get("enabled")),
        "provider": (config.get("provider") or "openai_responses") if enabled else "local_fallback",
        "model": config.get("model", DEFAULT_MODEL) if enabled else "deterministic_rules",
        "has_api_key": bool(api_key),
        "api_key_source": config.get("api_key_source", "missing"),
        "timeout_seconds": config.get("timeout_seconds", DEFAULT_TIMEOUT_SECONDS),
        "temperature": config.get("temperature", DEFAULT_LLM_CONFIG["temperature"]),
        "analysis_depth": config.get("analysis_depth", DEFAULT_LLM_CONFIG["analysis_depth"]),
        "identity_mode": config.get("identity_mode", DEFAULT_LLM_CONFIG["identity_mode"]),
        "retrieved_at": datetime.now(timezone.utc).isoformat(),
    }


def tactical_search_queries(team_name: str) -> list[dict]:
    fallback = _fallback_search_queries(team_name)
    if not _api_key():
        return fallback

    response = _call_llm_json(
        system=(
            "Você é um analista de desempenho de futebol. Gere APENAS consultas de busca sobre futebol, "
            "focando em material tático e visual: vídeos de jogos, melhores momentos, jogo completo, análise tática. "
            "Inclua buscas específicas por: formação (4-3-3, 4-2-3-1, etc), tática defensiva, saída de bola, "
            "transições rápidas, pressão alta, movimentação coletiva e posicionamento de jogadores. "
            "Evite completamente: história, notícias institucionais, mercado, resultados isolados, "
            "informações sobre cidades ou regiões. Garanta que cada query seja EXPLICITAMENTE sobre futebol."
        ),
        user=json.dumps({"team_name": team_name}, ensure_ascii=False),
        fallback={"queries": fallback},
    )
    queries = response.get("queries") if isinstance(response, dict) else None
    cleaned = []
    for item in queries or []:
        if not isinstance(item, dict):
            continue
        query = _clean_text(item.get("query"))
        category = item.get("category") if item.get("category") in {"match_videos", "analysis_videos", "team_form"} else "team_form"
        if query:
            cleaned.append(
                {
                    "label": _clean_text(item.get("label")) or _category_label(category),
                    "category": category,
                    "query": query,
                }
            )
    return cleaned[:6] or fallback


def enrich_team_search(team_name: str, online_payload: dict) -> dict:
    base = _fallback_team_search_enrichment(team_name, online_payload)
    if not _api_key():
        return base

    compact_payload = {
        "team_name": team_name,
        "status": online_payload.get("status"),
        "coverage": online_payload.get("coverage"),
        "sources": [
            {
                "title": source.get("title"),
                "origin": source.get("origin"),
                "category": source.get("category"),
                "summary": source.get("summary"),
                "url": source.get("url"),
            }
            for source in (online_payload.get("sources") or [])[:12]
        ],
        "errors": online_payload.get("errors", [])[:4],
    }
    response = _call_llm_json(
        system=(
            "Você apoia uma ferramenta de visão computacional para futebol. Transforme fontes coletadas em "
            "hipóteses táticas e prioridades de coleta. Nunca invente dados institucionais. Se as fontes forem "
            "fracas, diga que a próxima evidência deve vir do vídeo."
        ),
        user=json.dumps(compact_payload, ensure_ascii=False),
        fallback=base,
    )
    return _merge_with_defaults(response, base)


def analyze_video_visually(team_name: str, vision_result: dict) -> dict:
    """Leitura visual DIRETA dos frames reais do video (multimodal), cruzada
    com as metricas estruturadas do pipeline de CV. Diferente de
    `analyze_video_tactics` (que so recebe numeros/resumos), aqui o LLM
    efetivamente ve as imagens capturadas em `visual_key_frames`."""
    key_frames_payload = vision_result.get("visual_key_frames") or {}
    frames = [frame for frame in (key_frames_payload.get("frames") or []) if frame.get("image_base64")]
    base = _fallback_visual_analysis(team_name, vision_result, frames)
    if not _api_key() or not frames:
        return base

    images = [
        {
            "media_type": frame.get("media_type", "image/jpeg"),
            "data": frame["image_base64"],
            "caption": f"t={frame.get('time_s')}s - {frame.get('label')}",
        }
        for frame in frames
    ]
    compact_payload = {
        "team_name": team_name,
        "team_focus": vision_result.get("team_focus"),
        "shape_analysis": vision_result.get("shape_analysis"),
        "tactical_summary": vision_result.get("tactical_summary"),
        "frames_context": [
            {"time_s": frame.get("time_s"), "trigger": frame.get("trigger"), "label": frame.get("label")}
            for frame in frames
        ],
    }
    response = _call_llm_json(
        system=(
            "Voce e um analista tatico de futebol observando DIRETAMENTE os frames reais enviados do video "
            "(nao apenas numeros). Cada imagem tem uma legenda com o instante e o motivo da captura pela visao "
            "computacional (abertura, mudanca de padrao tatico, disputa/desarme ou conducao em alta velocidade). "
            "Para CADA imagem, descreva o que voce efetivamente ve: posicionamento dos jogadores, uniformes/cores, "
            "bola (quando visivel), aglomeracao ou espacamento entre jogadores. Depois cruze essas observacoes "
            "visuais com as metricas de rastreamento fornecidas (team_focus, shape_analysis, tactical_summary) e "
            "aponte concordancias e divergencias. Nunca invente jogadores, placar ou eventos que nao estejam "
            "visiveis nas imagens recebidas.\n\n"
            "Responda em JSON com os campos: visual_observations (lista de objetos {time_s, trigger, observation}), "
            "cross_check (texto comparando o que foi visto nas imagens com as metricas do pipeline), "
            "executive_summary_visual (resumo curto da leitura visual direta) e "
            "confidence (Alta, Media ou Baixa, conforme nitidez e cobertura das imagens recebidas)."
        ),
        user=json.dumps(compact_payload, ensure_ascii=False),
        fallback=base,
        images=images,
    )
    return _merge_with_defaults(response, base)


def analyze_video_tactics(team_name: str, vision_result: dict) -> dict:
    base = _fallback_video_analysis(team_name, vision_result)
    if not _api_key():
        return base

    compact_payload = {
        "team_name": team_name,
        "summary": vision_result.get("summary"),
        "team_focus": vision_result.get("team_focus"),
        "tracks_detected": vision_result.get("tracks_detected"),
        "movement_tracks": [
            {
                "id": track.get("id"),
                "samples": track.get("total_samples"),
                "distance_px": track.get("distance_px"),
                "role_hint": track.get("role_hint"),
                "team_label": track.get("team_label"),
                "confidence": track.get("team_confidence"),
            }
            for track in (vision_result.get("movement_tracks") or [])[:12]
        ],
        "shape_analysis": vision_result.get("shape_analysis"),
        "graph_metrics": (vision_result.get("graph") or {}).get("metrics"),
        "events": (vision_result.get("events") or [])[:12],
        "tactical_events": (vision_result.get("tactical_events") or [])[:10],
        "pattern_explanations": vision_result.get("pattern_explanations") or [],
    }
    response = _call_llm_json(
        system=(
            "Você é um analista tático de futebol experiente. Analise APENAS evidências visuais do vídeo e identifique:\n"
            "1. FORMAÇÃO: Detecte e descreva a formação do time (ex: 4-3-3, 4-2-3-1, 5-3-2)\n"
            "2. POSICIONAMENTO: Localização espacial dos jogadores em linhas defensivas, meio-campo e ataque\n"
            "3. TÁTICA DEFENSIVA: Pressão alta vs média vs baixa, marcação por homem vs zona, compactação\n"
            "4. TÁTICA OFENSIVA: Tipo de saída de bola, direcionamento de passes, velocidade de transição, profundidade\n"
            "5. MOVIMENTAÇÃO COLETIVA: Padrões de movimento, deslocamentos, ocupação de espaços\n"
            "6. PERFORMANCE INDIVIDUAL: Dinâmica, intensidade, passes bem executados, erros, tomadas de decisão\n"
            "7. JOGADORES CHAVE: Identifique números de camisa e posições dos jogadores mais influentes\n"
            "8. JOGADAS IDENTIFICADAS: A partir de 'events' e 'tactical_events' fornecidos, retorne um array "
            "'identified_plays' com objetos {type, label, time_s, description, confidence}, nomeando jogadas "
            "específicas (ex: contra-ataque, pressão pós-perda, disputa seguida de falta, condução progressiva, "
            "finalização) realmente presentes nos dados. Nunca crie jogadas sem evidência nos eventos recebidos.\n"
            "\n"
            "Seja específico com números de formação, posições exatas, sequências de movimentação.\n"
            "Não invente nomes de jogadores, placar ou dados externos. Use apenas rastreamento visual."
        ),
        user=json.dumps(compact_payload, ensure_ascii=False),
        fallback=base,
    )
    return _merge_with_defaults(response, base)


def identify_players_from_tracks(team_name: str, vision_result: dict) -> dict:
    base = _fallback_identity_analysis(team_name, vision_result)
    if not _api_key():
        return base

    compact_payload = {
        "team_name": team_name,
        "jersey_reference": vision_result.get("jersey_reference"),
        "team_focus": vision_result.get("team_focus"),
        "field_candidate_filter": vision_result.get("field_candidate_filter"),
        "tracks": [
            {
                "id": track.get("id"),
                "label": track.get("label"),
                "team_label": track.get("team_label"),
                "team_confidence": track.get("team_confidence"),
                "role_hint": track.get("role_hint"),
                "samples": track.get("total_samples"),
                "distance_px": track.get("distance_px"),
            }
            for track in (vision_result.get("movement_tracks") or [])[:18]
        ],
    }
    response = _call_llm_json(
        system=(
            "Você é um especialista em identificação de jogadores em vídeos de futebol. Para CADA jogador rastreado:\n"
            "1. NÚMERO DA CAMISA: Extraia o número observável (1-99)\n"
            "2. TIME: Classifique como time próprio, adversário ou árbitro baseado em padrão/cor da camisa\n"
            "3. POSIÇÃO TÁTICA: Infira a posição (goleiro, lateral, zagueiro, volante, meia, ponta, atacante)\n"
            "4. PERFORMANCE: Registre comportamento tático (agressividade, cobertura, posicionamento, velocidade)\n"
            "5. NÚMERO DE FRAMES: Quantos frames o jogador aparece (continuidade)\n"
            "6. DISTÂNCIA PERCORRIDA: Métrica de mobilidade em pixels\n"
            "\n"
            "Use APENAS evidências de tracking visual e referência de camisa. Se número de camisa não for legível:\n"
            "- Registre como 'número não legível'\n"
            "- Sugira cortes frontal/dorsal para confirmação\n"
            "Classifique confiança: alta (número claro + posição confirmada), média, ou baixa (rastreamento incerto)."
        ),
        user=json.dumps(compact_payload, ensure_ascii=False),
        fallback=base,
    )
    return _merge_with_defaults(response, base)


def enrich_pre_analysis(team_name: str, objective: str, online_payload: dict, pre_analysis: dict) -> dict:
    base = {
        "status": "local_fallback",
        "provider": "deterministic_rules",
        "summary": (
            f"Use a pré-análise de {team_name} como hipótese inicial e confirme com vídeos recentes antes "
            "de fechar conclusões táticas."
        ),
        "questions": [
            "O time mantém a mesma altura de bloco contra adversários fortes e fracos?",
            "A saída de bola ocorre por dentro, pelos lados ou por ligação direta?",
            "Quais jogadores sustentam as conexões mais repetidas no grafo de passes?",
        ],
        "next_actions": [
            "Enviar video com camera aberta para tracking da equipe selecionada.",
            "Anexar camisa de referencia para separar time, adversario e torcida.",
            "Revisar grafo, heatmap e trilhas antes de salvar o relatorio final.",
        ],
    }
    if not _api_key():
        return base

    response = _call_llm_json(
        system=(
            "Você é um analista tático de futebol que gera pré-análise profunda. Com base no objetivo do usuário "
            "e fontes táticas disponíveis, identifique e analise:\n"
            "1. FORMAÇÃO PRINCIPAL: Qual formação o time geralmente utiliza (ex: 4-3-3)\n"
            "2. VARIAÇÕES TÁTICAS: Como muda em diferentes situações de jogo\n"
            "3. JOGADORES-CHAVE: Quem lidera o jogo, quem marca, quem organiza\n"
            "4. PADRÕES DE MOVIMENTO: Comportamento coletivo, fluxo de passes, transições\n"
            "5. PONTOS FORTES: O que o time faz bem (defesa, transição, posse, etc)\n"
            "6. PONTOS FRACOS: Vulnerabilidades táticas exploráveis\n"
            "7. HIPÓTESES DE PERFORMANCE: Qual é o nível atual (em forma, em crise, volatilidade)\n"
            "\n"
            "Nunca use história do clube, notícias institucionais ou especulação. Baseie-se em fontes de "
            "vídeo tático e análise visual."
        ),
        user=json.dumps(
            {
                "team_name": team_name,
                "objective": objective,
                "online_summary": online_payload.get("summary"),
                "coverage": online_payload.get("coverage"),
                "pre_analysis": pre_analysis,
            },
            ensure_ascii=False,
        ),
        fallback=base,
    )
    return _merge_with_defaults(response, base)


def _call_llm_json(system: str, user: str, fallback: dict, images: list[dict] | None = None) -> dict:
    """Chama o provedor de LLM configurado (não mais fixo em um só) e devolve
    um dict JSON. Cada provedor tem sua própria API/autenticação/formato de
    resposta; o dispatch abaixo isola essa diferença dos pontos do app que
    consomem esta função (busca, pré-análise, vídeo, identidade, leitura
    visual multimodal, etc.). `images` (opcional) leva frames reais em
    base64 para os provedores que suportam entrada multimodal."""
    config = get_llm_runtime_config()
    api_key = _api_key()
    if not api_key:
        return fallback

    provider = config.get("provider") or "openai_responses"
    caller = _PROVIDER_CALLERS.get(provider, _call_openai_responses)
    model = config.get("model") or PROVIDER_DEFAULT_MODELS.get(provider, DEFAULT_MODEL)
    try:
        text = caller(system, user, config, api_key, model, images)
        parsed = json.loads(_extract_json_object(text)) if text else {}
        if not isinstance(parsed, dict):
            return fallback
        parsed.setdefault("status", "llm_enriched")
        parsed.setdefault("provider", provider)
        parsed.setdefault("model", model)
        return parsed
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError, OSError, ValueError) as error:
        enriched = dict(fallback)
        enriched["status"] = "local_fallback"
        enriched["provider"] = "deterministic_rules"
        enriched["llm_error"] = error.__class__.__name__
        return enriched


def _call_openai_responses(
    system: str, user: str, config: dict, api_key: str, model: str, images: list[dict] | None = None
) -> str:
    user_content = [{"type": "input_text", "text": user}]
    for image in images or []:
        if not image.get("data"):
            continue
        media_type = image.get("media_type", "image/jpeg")
        user_content.append({"type": "input_image", "image_url": f"data:{media_type};base64,{image['data']}"})

    body = {
        "model": model,
        "input": [
            {"role": "system", "content": [{"type": "input_text", "text": _system_with_preferences(system, config)}]},
            {"role": "user", "content": user_content},
        ],
        "text": {"format": {"type": "json_object"}},
        "temperature": float(config.get("temperature", DEFAULT_LLM_CONFIG["temperature"])),
        "max_output_tokens": int(config.get("max_output_tokens", DEFAULT_LLM_CONFIG["max_output_tokens"])),
    }
    request = urllib.request.Request(
        OPENAI_RESPONSES_URL,
        data=json.dumps(body, ensure_ascii=False).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    payload = _send_json_request(request, config)
    if payload.get("output_text"):
        return str(payload["output_text"])
    chunks = []
    for item in payload.get("output") or []:
        for content in item.get("content") or []:
            if content.get("text"):
                chunks.append(str(content["text"]))
    return "\n".join(chunks).strip()


def _call_anthropic_messages(
    system: str, user: str, config: dict, api_key: str, model: str, images: list[dict] | None = None
) -> str:
    valid_images = [image for image in images or [] if image.get("data")]
    if valid_images:
        content = [
            {
                "type": "image",
                "source": {
                    "type": "base64",
                    "media_type": image.get("media_type", "image/jpeg"),
                    "data": image["data"],
                },
            }
            for image in valid_images
        ]
        content.append({"type": "text", "text": user})
    else:
        content = user

    body = {
        "model": model,
        "max_tokens": int(config.get("max_output_tokens", DEFAULT_LLM_CONFIG["max_output_tokens"])),
        "temperature": float(config.get("temperature", DEFAULT_LLM_CONFIG["temperature"])),
        "system": _system_with_preferences(system, config),
        "messages": [{"role": "user", "content": content}],
    }
    request = urllib.request.Request(
        ANTHROPIC_MESSAGES_URL,
        data=json.dumps(body, ensure_ascii=False).encode("utf-8"),
        headers={
            "x-api-key": api_key,
            "anthropic-version": ANTHROPIC_VERSION,
            "Content-Type": "application/json",
        },
        method="POST",
    )
    payload = _send_json_request(request, config)
    chunks = [str(item.get("text", "")) for item in payload.get("content") or [] if item.get("type") == "text"]
    return "\n".join(chunks).strip()


def _call_google_gemini(
    system: str, user: str, config: dict, api_key: str, model: str, images: list[dict] | None = None
) -> str:
    url = f"{GOOGLE_GEMINI_URL_TEMPLATE.format(model=model)}?key={urllib.parse.quote(api_key)}"
    parts = [
        {"inlineData": {"mimeType": image.get("media_type", "image/jpeg"), "data": image["data"]}}
        for image in images or []
        if image.get("data")
    ]
    parts.append({"text": user})
    body = {
        "systemInstruction": {"parts": [{"text": _system_with_preferences(system, config)}]},
        "contents": [{"role": "user", "parts": parts}],
        "generationConfig": {
            "temperature": float(config.get("temperature", DEFAULT_LLM_CONFIG["temperature"])),
            "maxOutputTokens": int(config.get("max_output_tokens", DEFAULT_LLM_CONFIG["max_output_tokens"])),
            "responseMimeType": "application/json",
        },
    }
    request = urllib.request.Request(
        url,
        data=json.dumps(body, ensure_ascii=False).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    payload = _send_json_request(request, config)
    candidates = payload.get("candidates") or []
    if not candidates:
        return ""
    parts = (candidates[0].get("content") or {}).get("parts") or []
    return "\n".join(str(part.get("text", "")) for part in parts).strip()


def _call_xai_grok(
    system: str, user: str, config: dict, api_key: str, model: str, images: list[dict] | None = None
) -> str:
    # API da xAI e compatível com o formato Chat Completions da OpenAI.
    valid_images = [image for image in images or [] if image.get("data")]
    if valid_images:
        user_content = [{"type": "text", "text": user}] + [
            {
                "type": "image_url",
                "image_url": {"url": f"data:{image.get('media_type', 'image/jpeg')};base64,{image['data']}"},
            }
            for image in valid_images
        ]
    else:
        user_content = user

    body = {
        "model": model,
        "messages": [
            {"role": "system", "content": _system_with_preferences(system, config)},
            {"role": "user", "content": user_content},
        ],
        "response_format": {"type": "json_object"},
        "temperature": float(config.get("temperature", DEFAULT_LLM_CONFIG["temperature"])),
        "max_tokens": int(config.get("max_output_tokens", DEFAULT_LLM_CONFIG["max_output_tokens"])),
    }
    request = urllib.request.Request(
        XAI_CHAT_COMPLETIONS_URL,
        data=json.dumps(body, ensure_ascii=False).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    payload = _send_json_request(request, config)
    choices = payload.get("choices") or []
    if not choices:
        return ""
    return str((choices[0].get("message") or {}).get("content", "")).strip()


_PROVIDER_CALLERS = {
    "openai_responses": _call_openai_responses,
    "anthropic_messages": _call_anthropic_messages,
    "google_gemini": _call_google_gemini,
    "xai_grok": _call_xai_grok,
}


def _send_json_request(request: urllib.request.Request, config: dict) -> dict:
    timeout = int(config.get("timeout_seconds", DEFAULT_TIMEOUT_SECONDS))
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return json.loads(response.read().decode("utf-8", errors="replace"))


def _extract_json_object(text: str) -> str:
    """OpenAI e Gemini tem modo JSON nativo (resposta ja limpa); Anthropic nao
    tem, entao a resposta pode vir com texto ao redor do JSON apesar da
    instrucao no prompt. Extrai o primeiro bloco {...} como rede de seguranca."""
    stripped = text.strip()
    try:
        json.loads(stripped)
        return stripped
    except json.JSONDecodeError:
        pass
    match = re.search(r"\{.*\}", stripped, re.DOTALL)
    return match.group(0) if match else stripped


def _fallback_search_queries(team_name: str) -> list[dict]:
    cleaned = _clean_text(team_name) or "time"
    return [
        {
            "label": "Vídeos de jogos",
            "category": "match_videos",
            "query": f"{cleaned} futebol melhores momentos jogo completo análise de jogo",
        },
        {
            "label": "Análises táticas",
            "category": "analysis_videos",
            "query": f"{cleaned} futebol análise tática como joga saída de bola pressão transição",
        },
        {
            "label": "Padrões de jogo",
            "category": "team_form",
            "query": f"{cleaned} futebol estilo de jogo movimentação coletiva posicionamento",
        },
        {
            "label": "Vídeos sobre modelo de jogo",
            "category": "analysis_videos",
            "query": f"{cleaned} modelo de jogo futebol vídeo análise movimentação",
        },
    ]


def _fallback_team_search_enrichment(team_name: str, online_payload: dict) -> dict:
    coverage = online_payload.get("coverage") or {}
    return {
        "status": "local_fallback",
        "provider": "deterministic_rules",
        "summary": (
            f"Coleta de {team_name} organizada para alimentar análise visual: priorize vídeos de jogo, "
            "análises táticas e trechos com câmera aberta."
        ),
        "generated_queries": _fallback_search_queries(team_name),
        "priority_sources": [
            "Jogo completo ou melhores momentos com câmera aberta",
            "Análise tática em vídeo sobre modelo de jogo atual",
            "Recortes de saída de bola, pressão, transição e bola parada",
        ],
        "tactical_hypotheses": [
            f"Há {coverage.get('match_videos', 0)} fonte(s) de vídeo para validar comportamento real.",
            "O tracking deve confirmar amplitude, compactação e conexões recorrentes antes da decisão.",
            "As conclusões ficam condicionadas à qualidade do vídeo enviado.",
        ],
        "questions_for_video": [
            "Qual equipe deve ser rastreada e qual camisa identifica o time?",
            "O trecho mostra fase ofensiva, defensiva, transicao ou bola parada?",
            "A camera permite ver largura e profundidade suficientes para homografia?",
        ],
    }


_PLAY_LABELS = {
    "probable_pass": "Passe provavel",
    "probable_shot": "Finalizacao provavel",
    "carry_or_dribble": "Conducao/drible",
    "tackle_or_duel": "Desarme/disputa",
    "potential_foul": "Falta potencial",
    "counter_press": "Pressao pos-perda",
}


def _build_identified_plays(vision_result: dict) -> list[dict]:
    plays = []
    for event in (vision_result.get("events") or [])[:30]:
        event_type = event.get("type")
        if event_type not in _PLAY_LABELS:
            continue
        track_ids = [
            track_id
            for track_id in (event.get("track_id"), event.get("track_id_secondary"))
            if track_id is not None
        ] or list(event.get("active_track_ids") or [])
        plays.append(
            {
                "type": event_type,
                "label": _PLAY_LABELS[event_type],
                "time_s": event.get("time_s"),
                "description": event.get("explanation") or "Jogada inferida por evidencia visual do video.",
                "confidence": event.get("confidence", "Baixa"),
                "track_ids": track_ids,
            }
        )
    return plays[:15]


def _fallback_video_analysis(team_name: str, vision_result: dict) -> dict:
    shape = vision_result.get("shape_analysis") or {}
    metrics = (vision_result.get("graph") or {}).get("metrics") or {}
    tracks = vision_result.get("tracks_detected") or 0
    return {
        "status": "local_fallback",
        "provider": "deterministic_rules",
        "executive_summary": (
            f"A leitura visual de {team_name} rastreou {tracks} jogador(es)/rastro(s) da equipe selecionada. "
            f"A estrutura estimada foi {shape.get('formation_guess', 'indefinida')} com bloco "
            f"{shape.get('block', 'a revisar')}."
        ),
        "tactical_patterns": [
            vision_result.get("tactical_summary") or "Padrao dominante ainda indefinido.",
            f"Densidade do grafo: {metrics.get('network_density', 0)}%.",
            f"Lider de centralidade visual: {metrics.get('centrality_leader') or 'a confirmar'}.",
        ],
        "decision_points": [
            "Revisar as conexoes mais fortes no mapa 2D antes de definir padrao coletivo.",
            "Comparar heatmap e trilhas para separar amplitude, profundidade e compactacao.",
            "Confirmar eventos provaveis no video antes de registrar passe, desarme ou finalizacao.",
        ],
        "risks": [
            "Sem detector supervisionado de jogadores, alguns objetos podem permanecer como rastros genericos.",
            "OCR de nome/numero depende de crops nitidos da camisa em multiplos frames.",
        ],
        "identified_plays": _build_identified_plays(vision_result),
    }


def _fallback_visual_analysis(team_name: str, vision_result: dict, frames: list[dict]) -> dict:
    shape = vision_result.get("shape_analysis") or {}
    if not frames:
        summary = (
            f"Nenhum frame-chave foi capturado para {team_name} neste processamento; a leitura visual direta "
            "por LLM multimodal depende de eventos reais detectados pela visao computacional no video."
        )
    elif not _api_key():
        summary = (
            f"{len(frames)} frame(s)-chave capturado(s) para {team_name}, mas nenhum provedor de LLM com visao "
            "esta habilitado. Ative um provedor (todos os suportados aceitam imagens) para cruzar os frames "
            "reais com as metricas de rastreamento."
        )
    else:
        summary = f"Leitura visual direta indisponivel para {team_name} nesta chamada; usando metricas do pipeline."
    return {
        "status": "local_fallback",
        "provider": "deterministic_rules",
        "executive_summary_visual": summary,
        "visual_observations": [
            {
                "time_s": frame.get("time_s"),
                "trigger": frame.get("trigger"),
                "observation": frame.get("label"),
            }
            for frame in frames
        ],
        "cross_check": (
            f"Estrutura estimada apenas por rastreamento: {shape.get('formation_guess', 'indefinida')} "
            f"({shape.get('block', 'bloco a revisar')})."
        ),
        "confidence": "Baixa",
        "frames_available": len(frames),
    }


def _fallback_identity_analysis(team_name: str, vision_result: dict) -> dict:
    tracks = vision_result.get("movement_tracks") or []
    candidates = [
        {
            "track_id": track.get("id"),
            "team": team_name,
            "player": "não identificado",
            "number": "não identificado",
            "role_hint": track.get("role_hint") or "função a revisar",
            "confidence": track.get("team_confidence") or "Baixa",
            "evidence": track.get("team_label") or "rastro filtrado pela equipe selecionada",
        }
        for track in tracks[:8]
    ]
    return {
        "status": "local_fallback",
        "provider": "deterministic_rules",
        "summary": (
            "A identidade nominal ainda precisa de OCR/VLM sobre crops frontais e dorsais. "
            "O sistema ja separa a equipe por camisa de referencia e campo antes de tentar numero/nome."
        ),
        "candidates": candidates,
        "number_name_method": [
            "Extrair crops da camisa em frames nitidos e dentro do campo.",
            "Aplicar OCR no numero dorsal e, quando visivel, no nome.",
            "Validar o mesmo numero em varios frames antes de associar ao jogador.",
            "Cruzar com lista de relacionados somente quando o usuario fornecer fonte confiavel.",
        ],
        "confidence_note": "Nao atribuir nomes reais sem evidencia visual ou lista oficial fornecida pelo usuario.",
    }


def _merge_with_defaults(response: dict, defaults: dict) -> dict:
    if not isinstance(response, dict):
        return defaults
    merged = dict(defaults)
    for key, value in response.items():
        if value not in (None, "", [], {}):
            merged[key] = value
    return merged


def _api_key() -> str:
    config = get_llm_runtime_config()
    if not config.get("enabled"):
        return ""
    return str(config.get("api_key") or "").strip()


def _system_with_preferences(system: str, config: dict) -> str:
    return (
        f"{system}\n\n"
        "Parâmetros da aplicação:\n"
        f"- idioma: {config.get('language', 'pt-BR')}\n"
        f"- profundidade da análise: {config.get('analysis_depth', 'profunda')}\n"
        f"- escopo de busca: {config.get('search_scope', 'tactical_visual_only')}\n"
        f"- modo de identidade: {config.get('identity_mode', 'strict_visual_evidence')}\n"
        "Responda sempre em JSON válido e mantenha inferências separadas das evidências visuais."
    )


def _clean_text(value) -> str:
    return " ".join(str(value or "").strip().split())


def _category_label(category: str) -> str:
    return {
        "match_videos": "Vídeos de jogos",
        "analysis_videos": "Análises táticas",
        "team_form": "Padrões de jogo",
    }.get(category, "Busca tática")
