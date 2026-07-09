const rows = [
  ["Busca de dados", "Dados mockados", "Busca em APIs, web e bases esportivas"],
  ["Vídeos", "Lista simulada", "Transcrição, resumo e análise de lances"],
  ["Dossiê tático", "Texto simulado", "Geração com LLM baseada em evidências"],
  ["Scouting", "Métricas mockadas", "Ranking inteligente de jogadores"],
  ["Plano de jogo", "Recomendações mockadas", "Recomendações baseadas no adversário"],
  ["Relatório", "Template fixo", "Relatório personalizado por objetivo"]
];

export default function FutureAI() {
  return (
    <section className="page-grid">
      <div className="section-heading">
        <div>
          <p className="eyebrow">Roadmap técnico</p>
          <h2>Como a IA será integrada</h2>
        </div>
      </div>
      <div className="notice-strip">
        Nesta entrega, todo conteúdo tático é simulado. A integração real com IA fica delimitada como evolução futura.
      </div>
      <div className="table-wrap">
        <table>
          <thead>
            <tr>
              <th>Área</th>
              <th>Nesta versão</th>
              <th>Futuro com IA</th>
            </tr>
          </thead>
          <tbody>
            {rows.map(([area, now, future]) => (
              <tr key={area}>
                <td>
                  <strong>{area}</strong>
                </td>
                <td>{now}</td>
                <td>{future}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <section className="three-column">
        <article>
          <h3>LLMs</h3>
          <p>
            Gerariam dossiês, relatórios e planos de jogo a partir de evidências recuperadas e revisadas.
          </p>
        </article>
        <article>
          <h3>RAG</h3>
          <p>
            Conectaria dados de partidas, notícias, relatórios internos e estatísticas com rastreabilidade.
          </p>
        </article>
        <article>
          <h3>Vídeo</h3>
          <p>
            Transcrição, marcação de eventos e resumo de lances poderiam apoiar scouts e analistas.
          </p>
        </article>
      </section>
      <section className="two-column">
        <article>
          <h3>Validação de dados</h3>
          <ul className="check-list">
            <li>Separar evidência observada de inferência gerada.</li>
            <li>Exigir fontes rastreáveis para recomendações críticas.</li>
            <li>Registrar nível de confiança por seção do relatório.</li>
          </ul>
        </article>
        <article>
          <h3>Cuidados contra alucinação</h3>
          <ul className="risk-list">
            <li>Bloquear respostas sem fonte em cenários de decisão técnica.</li>
            <li>Comparar dados de múltiplas fontes antes de concluir.</li>
            <li>Manter revisão humana para relatório final.</li>
          </ul>
        </article>
      </section>
    </section>
  );
}
