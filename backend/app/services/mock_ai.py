from dataclasses import dataclass


@dataclass(frozen=True)
class MockTacticalProfile:
    formation: str
    strengths: list[str]
    weaknesses: list[str]
    key_players: list[str]
    recent_matches: list[str]
    game_plan: str
    simulation_note: str


MOCK_PROFILES: dict[str, MockTacticalProfile] = {
    "palmeiras": MockTacticalProfile(
        formation="4-2-3-1",
        strengths=[
            "Pressao alta coordenada apos perda",
            "Bolas paradas ofensivas muito agressivas",
            "Laterais com boa amplitude para criar cruzamentos",
        ],
        weaknesses=[
            "Espaco entre lateral e zagueiro quando a linha sobe",
            "Risco de transicao defensiva pelo corredor central",
        ],
        key_players=["Raphael Veiga", "Gustavo Gomez", "Weverton"],
        recent_matches=["Vitoria 2-0", "Empate 1-1", "Vitoria 3-1"],
        game_plan=(
            "Atrair a primeira pressao para acionar o meia entrelinhas, "
            "alternando inversoes rapidas para o lado oposto."
        ),
        simulation_note=(
            "Resposta simulada: o modelo indicaria alta probabilidade de "
            "controle territorial se a equipe vencer os duelos no meio."
        ),
    ),
    "flamengo": MockTacticalProfile(
        formation="4-3-3",
        strengths=[
            "Ataque posicional com muitos jogadores por dentro",
            "Finalizacao forte de media distancia",
            "Extremos atacando o intervalo entre lateral e zagueiro",
        ],
        weaknesses=[
            "Linha defensiva vulneravel a bolas longas diagonais",
            "Recomposicao irregular quando os laterais avancam juntos",
        ],
        key_players=["Arrascaeta", "Pedro", "Gerson"],
        recent_matches=["Vitoria 1-0", "Derrota 2-3", "Vitoria 4-2"],
        game_plan=(
            "Bloquear o passe no volante construtor e forcar circulacao "
            "lateral antes de pressionar o receptor de costas."
        ),
        simulation_note=(
            "Resposta simulada: o time tende a criar mais chances quando "
            "consegue receber entre as linhas sem pressao imediata."
        ),
    ),
    "sao paulo": MockTacticalProfile(
        formation="4-4-2",
        strengths=[
            "Compactacao defensiva em bloco medio",
            "Ataque rapido apos recuperacao no meio",
            "Boa ocupacao da area em cruzamentos",
        ],
        weaknesses=[
            "Dificuldade para sair sob pressao alta intensa",
            "Menor volume criativo quando o meia central e bem marcado",
        ],
        key_players=["Lucas Moura", "Calleri", "Rafael"],
        recent_matches=["Empate 0-0", "Vitoria 2-1", "Derrota 0-1"],
        game_plan=(
            "Aumentar a intensidade sobre a primeira construcao e proteger "
            "a zona frontal da area contra segundas bolas."
        ),
        simulation_note=(
            "Resposta simulada: a vantagem aparece em jogos de ritmo "
            "controlado e duelos fisicos bem distribuidos."
        ),
    ),
    "corinthians": MockTacticalProfile(
        formation="3-4-2-1",
        strengths=[
            "Superioridade numerica na saida com tres defensores",
            "Alas profundos para acelerar pelos corredores",
            "Boa protecao da area em bloco baixo",
        ],
        weaknesses=[
            "Espaco as costas dos alas quando perde a posse",
            "Baixa criacao se os meias recebem sempre de costas",
        ],
        key_players=["Yuri Alberto", "Raniele", "Romero"],
        recent_matches=["Derrota 1-2", "Empate 1-1", "Vitoria 2-0"],
        game_plan=(
            "Circular a bola ate deslocar o ala adversario e atacar o "
            "corredor livre com passe vertical imediato."
        ),
        simulation_note=(
            "Resposta simulada: a equipe melhora quando reduz perdas no "
            "campo central e acelera pelo lado fraco."
        ),
    ),
    "fluminense": MockTacticalProfile(
        formation="4-2-2-2",
        strengths=[
            "Aproximacoes curtas para manter posse sob pressao",
            "Movimentos constantes no setor central",
            "Zagueiros participando da construcao",
        ],
        weaknesses=[
            "Exposicao em transicoes longas",
            "Dependencia de precisao tecnica em zonas perigosas",
        ],
        key_players=["Ganso", "Cano", "Andre"],
        recent_matches=["Vitoria 2-1", "Empate 2-2", "Derrota 0-2"],
        game_plan=(
            "Pressionar gatilhos de passe para tras e atacar rapidamente "
            "a area descoberta quando a linha defensiva estiver aberta."
        ),
        simulation_note=(
            "Resposta simulada: posse alta nao garante dominio se o "
            "adversario conseguir acelerar apos recuperacoes."
        ),
    ),
}


def generate_mock_analysis(club_name: str) -> MockTacticalProfile:
    key = club_name.strip().lower()
    if key in MOCK_PROFILES:
        return MOCK_PROFILES[key]

    normalized = club_name.strip().title()
    return MockTacticalProfile(
        formation="4-3-3",
        strengths=[
            "Bloco medio organizado",
            "Transicoes ofensivas pelo lado direito",
            "Boa agressividade em bolas paradas",
        ],
        weaknesses=[
            "Dificuldade para defender inversoes rapidas",
            "Pouca profundidade quando o centroavante sai da area",
        ],
        key_players=[
            f"Capitao do {normalized}",
            f"Meia criativo do {normalized}",
            f"Goleiro do {normalized}",
        ],
        recent_matches=["Vitoria 1-0", "Empate 1-1", "Derrota 0-1"],
        game_plan=(
            "Simulacao generica: controlar o centro, evitar perdas no "
            "primeiro passe e atacar o espaco atras dos laterais."
        ),
        simulation_note=(
            "Resposta simulada sem IA real: use este dossie apenas como "
            "placeholder para validar o fluxo de produto."
        ),
    )
