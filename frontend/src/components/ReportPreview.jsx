import ConfidenceBadge from "./ConfidenceBadge.jsx";

export default function ReportPreview({ report }) {
  if (!report) {
    return (
      <section className="empty-state">
        <h2>Relatorio ainda nao gerado</h2>
        <p>Use o botao acima para montar o relatorio consolidado com fontes, grafo e plano de jogo.</p>
      </section>
    );
  }

  return (
    <section className="report-preview">
      <div className="section-heading">
        <div>
          <p className="eyebrow">Relatorio final</p>
          <h2>{report.team.name}</h2>
        </div>
        <ConfidenceBadge level={report.confidence} />
      </div>
      <div className="report-grid">
        <article>
          <h3>Resumo executivo</h3>
          <p>{report.executive_summary}</p>
        </article>
        <article>
          <h3>Perfil do adversario</h3>
          <p>{report.opponent_profile}</p>
        </article>
        <article>
          <h3>Formacao provavel</h3>
          <p>{report.probable_formation}</p>
        </article>
        <article>
          <h3>Estrategia recomendada</h3>
          <p>{report.recommended_strategy}</p>
        </article>
      </div>
      <div className="two-column">
        <article>
          <h3>Jogadores-chave</h3>
          <ul className="clean-list">
            {report.key_players.map((player) => (
              <li key={player.name}>
                <strong>{player.name}</strong>
                <span>{player.position} - nota {player.tactical_score}</span>
              </li>
            ))}
          </ul>
        </article>
        <article>
          <h3>Sugestoes de treino</h3>
          <ul className="check-list">
            {report.training_suggestions.map((item) => (
              <li key={item}>{item}</li>
            ))}
          </ul>
        </article>
      </div>
    </section>
  );
}
