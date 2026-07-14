import { useParams } from "react-router-dom";
import { Activity, AlertTriangle, BrainCircuit, ClipboardList, ShieldAlert, Target, Users } from "lucide-react";

import { api } from "../api/client.js";
import ErrorState from "../components/ErrorState.jsx";
import LoadingState from "../components/LoadingState.jsx";
import { useApiResource } from "./useApiResource.js";

export default function GamePlan() {
  const { teamId } = useParams();
  const isLocalTeam = /^\d+$/.test(String(teamId));
  const { data, loading, error } = useApiResource(() => api.teamWorkspace(teamId), [teamId]);
  const { data: research } = useApiResource(
    () => (isLocalTeam ? api.operationalResearch(teamId) : Promise.resolve(null)),
    [teamId]
  );

  if (loading) return <LoadingState />;
  if (error) return <ErrorState message={error} />;

  const { team, plan, collection } = data;

  return (
    <section className="page-grid">
      <div className="section-heading">
        <div>
          <p className="eyebrow">{team.name}</p>
          <h2>Plano de jogo e coleta pendente</h2>
        </div>
      </div>
      <div className="card-grid two">
        <article className="info-panel">
          <h3>
            <Activity size={17} />
            Como pressionar
          </h3>
          <p>{plan.how_to_press}</p>
        </article>
        <article className="info-panel">
          <h3>
            <Target size={17} />
            Onde atacar
          </h3>
          <p>{plan.where_to_attack}</p>
        </article>
      </div>
      <section className="two-column">
        <article>
          <h3>
            <Users size={17} />
            Alvos ou referencias
          </h3>
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
          <h3>
            <ShieldAlert size={17} />
            Fragilidades a confirmar
          </h3>
          <ul className="risk-list">
            {plan.weaknesses_to_exploit.map((item) => (
              <li key={item}>{item}</li>
            ))}
          </ul>
        </article>
      </section>
      <section className="three-column">
        <article>
          <h3>
            <ClipboardList size={17} />
            Sugestoes de treino/coleta
          </h3>
          <ul className="check-list">
            {plan.training_suggestions.map((item) => (
              <li key={item}>{item}</li>
            ))}
          </ul>
        </article>
        <article>
          <h3>
            <AlertTriangle size={17} />
            Riscos do plano
          </h3>
          <ul className="risk-list">
            {plan.plan_risks.map((item) => (
              <li key={item}>{item}</li>
            ))}
          </ul>
        </article>
        <article>
          <h3>
            <Target size={17} />
            A coletar
          </h3>
          <ul className="check-list">
            {collection.to_collect.map((item) => (
              <li key={item.stage}>
                <strong>{item.stage}:</strong> {item.action}
              </li>
            ))}
          </ul>
        </article>
      </section>
      {research ? <OperationalResearch research={research} /> : null}
    </section>
  );
}

function OperationalResearch({ research }) {
  const lineup = research.lineup || {};
  const comparison = research.formation_comparison || {};
  const recommendations = comparison.recommendations || {};
  const stateLabels = { vencendo: "Vencendo", empatando: "Empatando", perdendo: "Perdendo" };

  return (
    <>
      <div className="section-heading">
        <div>
          <p className="eyebrow">Pesquisa operacional</p>
          <h2>Escalacao otima e cenarios por formacao</h2>
        </div>
      </div>
      <div className="card-grid two">
        <article className="info-panel">
          <h3>
            <BrainCircuit size={17} />
            Escalacao otima para {research.target_formation}
          </h3>
          {lineup.status === "sem_elenco" ? (
            <p>{lineup.note}</p>
          ) : (
            <>
              <p>
                Forca da escalacao: <strong>{lineup.lineup_strength}</strong> / 10 · Cobertura posicional:{" "}
                <strong>{lineup.positional_coverage}%</strong>
                {lineup.gaps?.length ? ` · Vagas frageis: ${lineup.gaps.join(", ")}` : ""}
              </p>
              <ul className="clean-list">
                {(lineup.assignments || []).map((slot) => (
                  <li key={slot.slot_id}>
                    <strong>
                      {slot.position} — {slot.player ? slot.player.name : "sem jogador disponivel"}
                    </strong>
                    <span>
                      {slot.player ? `Fit ${slot.fit}/10 · ${slot.explanation}` : slot.explanation}
                    </span>
                  </li>
                ))}
              </ul>
              <p className="inline-message">{lineup.note}</p>
            </>
          )}
        </article>
        <article className="info-panel">
          <h3>
            <ClipboardList size={17} />
            Formacao recomendada por estado de jogo
          </h3>
          {Object.keys(recommendations).length ? (
            <ul className="clean-list">
              {Object.entries(recommendations).map(([state, item]) => (
                <li key={state}>
                  <strong>
                    {stateLabels[state] || state}: {item.formation}
                  </strong>
                  <span>{item.reason}</span>
                </li>
              ))}
            </ul>
          ) : (
            <p>Cadastre formacoes do time para comparar cenarios.</p>
          )}
          {(comparison.scenarios || []).length ? (
            <ul className="check-list">
              {comparison.scenarios.map((scenario) => (
                <li key={scenario.formation}>
                  <strong>{scenario.formation}:</strong> utilidade {scenario.utility} · ofensivo{" "}
                  {scenario.offensive_index} · defensivo {scenario.defensive_index}
                </li>
              ))}
            </ul>
          ) : null}
          <p className="inline-message">{comparison.note}</p>
        </article>
      </div>
    </>
  );
}
