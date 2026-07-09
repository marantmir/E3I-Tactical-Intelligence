import ConfidenceBadge from "./ConfidenceBadge.jsx";

export default function ReportPreview({ report }) {
  if (!report) {
    return (
      <section className="empty-state">
        <h2>Relatório ainda não gerado</h2>
        <p>Use o botão acima para montar o relatório consolidado com os dados mockados.</p>
      </section>
    );
  }

  return (
    <section className="report-preview">
      <div className="section-heading">
        <div>
          <p className="eyebrow">Relatório final</p>
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
          <h3>Perfil do adversário</h3>
          <p>{report.opponent_profile}</p>
        </article>
        <article>
          <h3>Formação provável</h3>
          <p>{report.probable_formation}</p>
        </article>
        <article>
          <h3>Estratégia recomendada</h3>
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
                <span>{player.position} · nota {player.tactical_score}</span>
              </li>
            ))}
          </ul>
        </article>
        <article>
          <h3>Sugestões de treino</h3>
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
