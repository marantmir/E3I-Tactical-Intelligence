import { useParams } from "react-router-dom";

import { api } from "../api/client.js";
import ErrorState from "../components/ErrorState.jsx";
import LoadingState from "../components/LoadingState.jsx";
import { useApiResource } from "./useApiResource.js";

export default function Formations() {
  const { teamId } = useParams();
  const { data, loading, error } = useApiResource(async () => {
    const [team, formations] = await Promise.all([api.team(teamId), api.formations(teamId)]);
    return { team, formations };
  }, [teamId]);

  if (loading) return <LoadingState />;
  if (error) return <ErrorState message={error} />;

  return (
    <section>
      <div className="section-heading">
        <div>
          <p className="eyebrow">{data.team.name}</p>
          <h2>Formações prováveis</h2>
        </div>
      </div>
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
    </section>
  );
}
