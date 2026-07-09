const rows = [
  ["Busca de dados", "Ativo", "Consulta publica, base local e revisao de fonte"],
  ["Videos", "Ativo", "Mapa de calor, trilhas, eventos e recomendacoes por lance"],
  ["Dossie tatico", "Ativo", "Resumo por objetivo com evidencias e nivel de confianca"],
  ["Grafos taticos", "Ativo", "Conexoes entre jogadores, zonas, centralidade e densidade"],
  ["Visao computacional", "Ativo", "Leitura visual de ocupacao, pressao, profundidade e corredores"],
  ["Pesquisa operacional", "Ativo", "Comparacao de formacoes, riscos, cenarios e plano de jogo"],
  ["Scouting", "Ativo", "Ranking por influencia, risco e nota tatica"],
  ["Relatorio", "Ativo", "Relatorio consolidado para comissao tecnica"],
  ["Modelos externos", "Evolucao", "Integrar APIs esportivas premium, tracking real e modelos de video"]
];

export default function FutureAI() {
  return (
    <section className="page-grid">
      <div className="section-heading">
        <div>
          <p className="eyebrow">Inteligencia avancada</p>
          <h2>Busca, grafos, video e decisao tatica</h2>
        </div>
      </div>
      <div className="notice-strip">
        As camadas visuais ja estao integradas ao fluxo: pesquisar, analisar, revisar e salvar.
      </div>
      <div className="table-wrap">
        <table>
          <thead>
            <tr>
              <th>Area</th>
              <th>Status</th>
              <th>Aplicacao</th>
            </tr>
          </thead>
          <tbody>
            {rows.map(([area, status, application]) => (
              <tr key={area}>
                <td>
                  <strong>{area}</strong>
                </td>
                <td>{status}</td>
                <td>{application}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <section className="three-column">
        <article>
          <h3>Busca publica</h3>
          <p>
            Recupera informacoes abertas do time pesquisado e conserva uma trilha de revisao quando
            a rede externa nao estiver disponivel.
          </p>
        </article>
        <article>
          <h3>Grafos</h3>
          <p>
            Modelam jogadores, conexoes e zonas para revelar centralidade, densidade, corredor de
            progressao e pontos de risco.
          </p>
        </article>
        <article>
          <h3>Video</h3>
          <p>
            Organiza lances em mapa de calor, trilhas de movimento e eventos para apoiar decisao de
            treino e plano de jogo.
          </p>
        </article>
      </section>
      <section className="two-column">
        <article>
          <h3>Validade da analise</h3>
          <ul className="check-list">
            <li>Separar fonte publica, base local e inferencia visual.</li>
            <li>Exigir revisao humana antes de usar recomendacoes em jogo.</li>
            <li>Registrar confianca por fonte, jogador, formacao e lance.</li>
          </ul>
        </article>
        <article>
          <h3>Proximas integracoes</h3>
          <ul className="check-list">
            <li>APIs esportivas com estatisticas atualizadas por temporada.</li>
            <li>Upload de videos para extracao real de tracking e eventos.</li>
            <li>Otimizacao numerica de escalacao, formacao e estrategia.</li>
          </ul>
        </article>
      </section>
    </section>
  );
}
