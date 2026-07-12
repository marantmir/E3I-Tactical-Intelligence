import { Link, useParams } from "react-router-dom";

import { api } from "../api/client.js";
import ErrorState from "../components/ErrorState.jsx";
import LoadingState from "../components/LoadingState.jsx";
import TacticalGraph from "../components/TacticalGraph.jsx";
import { useApiResource } from "./useApiResource.js";

export default function Formations() {
  const { teamId } = useParams();
  const { data, loading, error } = useApiResource(() => api.teamWorkspace(teamId), [teamId]);

  if (loading) return <LoadingState />;
  if (error) return <ErrorState message={error} />;

  return (
    <section>
      <div className="section-heading">
        <div>
          <p className="eyebrow">{data.team.name}</p>
          <h2>Formacoes e grafo do time ativo</h2>
        </div>
      </div>

      {data.formations.length > 0 ? (
        <div className="formation-grid">
          {data.formations.map((item) => (
            <article className="formation-card" key={item.formation}>
              <div className="formation-score">
                <strong>{item.formation}</strong>
                <span>{item.probability}%</span>
              </div>
              <div className="probability-bar" aria-label={`${item.probability}%`}>
                <span style={{ width: `${item.probability}%` }} />
              </div>
              <dl>
                <dt>Contexto</dt>
                <dd>{item.context}</dd>
                <dt>Vantagens</dt>
                <dd>{item.advantages}</dd>
                <dt>Riscos</dt>
                <dd>{item.risks}</dd>
              </dl>
            </article>
          ))}
        </div>
      ) : (
        <div className="empty-state">
          <h2>Nenhuma formacao coletada ainda</h2>
          <p>
            A forma mais assertiva de obter a formacao real e enviar um video do jogo na aba Fontes: a visao
            computacional estima a formacao a partir do rastreamento dos jogadores e voce pode salva-la com um
            clique. Tambem e possivel cadastrar manualmente pela Administracao.
          </p>
          <div className="form-actions" style={{ justifyContent: "center" }}>
            <Link className="button button-primary" to={`/team/${teamId}/sources`}>
              Enviar video para detectar formacao
            </Link>
            <Link className="button button-secondary" to="/admin">
              Cadastrar manualmente
            </Link>
          </div>
        </div>
      )}

      <TacticalGraph graph={data.graph} />
    </section>
  );
}
