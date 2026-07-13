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
            "Voce e um analista de desempenho de futebol. Gere consultas de busca somente para material "
            "tatico e visual: videos de jogos, melhores momentos, jogo completo, analise tatica, modelo de "
            "jogo, pressao, saida de bola, transicoes, movimentacao coletiva. Evite historia, noticias "
            "institucionais, mercado e resultados isolados."
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
            "Voce apoia uma ferramenta de visao computacional para futebol. Transforme fontes coletadas em "
            "hipoteses taticas e prioridades de coleta. Nunca invente dados institucionais. Se as fontes forem "
            "fracas, diga que a proxima evidencia deve vir do video."
        ),
        user=json.dumps(compact_payload, ensure_ascii=False),
        fallback=base,
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
            "Voce e um analista tatico de futebol usando apenas evidencias visuais extraidas do video. "
            "Explique o que esta acontecendo, quais padroes aparecem, quais duvidas permanecem e quais "
            "decisoes o analista pode tomar. Nao invente nomes de jogadores, placar ou contexto externo."
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
            "Voce ajuda a identificar time, jogador e numero em video de futebol. Use apenas evidencias "
            "presentes no tracking e na camisa de referencia. Quando nao houver OCR/crop suficiente, retorne "
            "candidato como 'nao identificado' e explique como confirmar com crop frontal/dorsal multi-frame."
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
            f"Use a pre-analise de {team_name} como hipotese inicial e confirme com videos recentes antes "
            "de fechar conclusoes taticas."
        ),
        "questions": [
            "O time mantem a mesma altura de bloco contra adversarios fortes e fracos?",
            "A saida de bola ocorre por dentro, pelos lados ou por ligacao direta?",
            "Quais jogadores sustentam as conexoes mais repetidas no grafo de passes?",
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
            "Voce gera pre-analise tatica acessivel para uma ferramenta de futebol. Use objetivo do usuario, "
            "fontes taticas e o preview existente. Nao use historia do clube nem noticia institucional."
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


def _call_llm_json(system: str, user: str, fallback: dict) -> dict:
    """Chama o provedor de LLM configurado (nao mais fixo em um so) e devolve
    um dict JSON. Cada provedor tem sua propria API/autenticacao/formato de
    resposta; o dispatch abaixo isola essa diferenca dos 5 pontos do app que
    consomem esta funcao (busca, pre-analise, video, identidade, etc.)."""
    config = get_llm_runtime_config()
    api_key = _api_key()
    if not api_key:
        return fallback

    provider = config.get("provider") or "openai_responses"
    caller = _PROVIDER_CALLERS.get(provider, _call_openai_responses)
    model = config.get("model") or PROVIDER_DEFAULT_MODELS.get(provider, DEFAULT_MODEL)
    try:
        text = caller(system, user, config, api_key, model)
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


def _call_openai_responses(system: str, user: str, config: dict, api_key: str, model: str) -> str:
    body = {
        "model": model,
        "input": [
            {"role": "system", "content": [{"type": "input_text", "text": _system_with_preferences(system, config)}]},
            {"role": "user", "content": [{"type": "input_text", "text": user}]},
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


def _call_anthropic_messages(system: str, user: str, config: dict, api_key: str, model: str) -> str:
    body = {
        "model": model,
        "max_tokens": int(config.get("max_output_tokens", DEFAULT_LLM_CONFIG["max_output_tokens"])),
        "temperature": float(config.get("temperature", DEFAULT_LLM_CONFIG["temperature"])),
        "system": _system_with_preferences(system, config),
        "messages": [{"role": "user", "content": user}],
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


def _call_google_gemini(system: str, user: str, config: dict, api_key: str, model: str) -> str:
    url = f"{GOOGLE_GEMINI_URL_TEMPLATE.format(model=model)}?key={urllib.parse.quote(api_key)}"
    body = {
        "systemInstruction": {"parts": [{"text": _system_with_preferences(system, config)}]},
        "contents": [{"role": "user", "parts": [{"text": user}]}],
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


def _call_xai_grok(system: str, user: str, config: dict, api_key: str, model: str) -> str:
    # API da xAI e compatível com o formato Chat Completions da OpenAI.
    body = {
        "model": model,
        "messages": [
            {"role": "system", "content": _system_with_preferences(system, config)},
            {"role": "user", "content": user},
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
            "label": "Videos de jogos",
            "category": "match_videos",
            "query": f"{cleaned} futebol melhores momentos jogo completo analise de jogo",
        },
        {
            "label": "Analises taticas",
            "category": "analysis_videos",
            "query": f"{cleaned} futebol analise tatica como joga saida de bola pressao transicao",
        },
        {
            "label": "Padroes de jogo",
            "category": "team_form",
            "query": f"{cleaned} futebol estilo de jogo movimentacao coletiva posicionamento",
        },
        {
            "label": "Videos sobre modelo de jogo",
            "category": "analysis_videos",
            "query": f"{cleaned} modelo de jogo futebol video analise movimentacao",
        },
    ]


def _fallback_team_search_enrichment(team_name: str, online_payload: dict) -> dict:
    coverage = online_payload.get("coverage") or {}
    return {
        "status": "local_fallback",
        "provider": "deterministic_rules",
        "summary": (
            f"Coleta de {team_name} organizada para alimentar analise visual: priorize videos de jogo, "
            "analises taticas e trechos com camera aberta."
        ),
        "generated_queries": _fallback_search_queries(team_name),
        "priority_sources": [
            "Jogo completo ou melhores momentos com camera aberta",
            "Analise tatica em video sobre modelo de jogo atual",
            "Recortes de saida de bola, pressao, transicao e bola parada",
        ],
        "tactical_hypotheses": [
            f"Ha {coverage.get('match_videos', 0)} fonte(s) de video para validar comportamento real.",
            "O tracking deve confirmar amplitude, compactacao e conexoes recorrentes antes da decisao.",
            "As conclusoes ficam condicionadas a qualidade do video enviado.",
        ],
        "questions_for_video": [
            "Qual equipe deve ser rastreada e qual camisa identifica o time?",
            "O trecho mostra fase ofensiva, defensiva, transicao ou bola parada?",
            "A camera permite ver largura e profundidade suficientes para homografia?",
        ],
    }


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
    }


def _fallback_identity_analysis(team_name: str, vision_result: dict) -> dict:
    tracks = vision_result.get("movement_tracks") or []
    candidates = [
        {
            "track_id": track.get("id"),
            "team": team_name,
            "player": "nao identificado",
            "number": "nao identificado",
            "role_hint": track.get("role_hint") or "funcao a revisar",
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
        "Parametros da aplicacao:\n"
        f"- idioma: {config.get('language', 'pt-BR')}\n"
        f"- profundidade da analise: {config.get('analysis_depth', 'profunda')}\n"
        f"- escopo de busca: {config.get('search_scope', 'tactical_visual_only')}\n"
        f"- modo de identidade: {config.get('identity_mode', 'strict_visual_evidence')}\n"
        "Responda sempre em JSON valido e mantenha inferencias separadas das evidencias visuais."
    )


def _clean_text(value) -> str:
    return " ".join(str(value or "").strip().split())


def _category_label(category: str) -> str:
    return {
        "match_videos": "Videos de jogos",
        "analysis_videos": "Analises taticas",
        "team_form": "Padroes de jogo",
    }.get(category, "Busca tatica")
