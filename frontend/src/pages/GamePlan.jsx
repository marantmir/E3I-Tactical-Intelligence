import { useParams } from "react-router-dom";

import { api } from "../api/client.js";
import ErrorState from "../components/ErrorState.jsx";
import LoadingState from "../components/LoadingState.jsx";
import { useApiResource } from "./useApiResource.js";

export default function GamePlan() {
  const { teamId } = useParams();
  const { data, loading, error } = useApiResource(async () => {
    const [team, plan] = await Promise.all([api.team(teamId), api.gamePlan(teamId)]);
    return { team, plan };
  }, [teamId]);

  if (loading) return <LoadingState />;
  if (error) return <ErrorState message={error} />;

  const { team, plan } = data;

  return (
    <section className="page-grid">
      <div className="section-heading">
        <div>
          <p className="eyebrow">{team.name}</p>
          <h2>Plano de jogo</h2>
        </div>
      </div>
      <div className="card-grid two">
        <article className="info-panel">
          <h3>Como pressionar</h3>
          <p>{plan.how_to_press}</p>
        </article>
        <article className="info-panel">
          <h3>Onde atacar</h3>
          <p>{plan.where_to_attack}</p>
        </article>
      </div>
      <section className="two-column">
        <article>
          <h3>Jogadores a neutralizar</h3>
          <ul className="clean-list">
            {plan.players_to_neutralize.map((item) => (
              <li key={item}>
                <strong>{item}</strong>
                <span>Monitoramento por grafo e video</span>
              </li>
            ))}
          </ul>
        </article>
        <article>
          <h3>Fragilidades a explorar</h3>
          <ul className="risk-list">
            {plan.weaknesses_to_exploit.map((item) => (
              <li key={item}>{item}</li>
            ))}
          </ul>
        </article>
      </section>
      <section className="three-column">
        <article>
          <h3>Sugestoes de treino</h3>
          <ul className="check-list">
            {plan.training_suggestions.map((item) => (
              <li key={item}>{item}</li>
            ))}
          </ul>
        </article>
        <article>
          <h3>Riscos do plano</h3>
          <ul className="risk-list">
            {plan.plan_risks.map((item) => (
              <li key={item}>{item}</li>
            ))}
          </ul>
        </article>
        <article>
          <h3>Ajustes durante a partida</h3>
          <ul className="check-list">
            {plan.in_match_adjustments.map((item) => (
              <li key={item}>{item}</li>
            ))}
          </ul>
        </article>
      </section>
    </section>
  );
}
