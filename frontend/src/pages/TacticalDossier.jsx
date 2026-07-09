import { Link, useParams } from "react-router-dom";
import { ArrowRight, CircleDot } from "lucide-react";

import { api } from "../api/client.js";
import ConfidenceBadge from "../components/ConfidenceBadge.jsx";
import ErrorState from "../components/ErrorState.jsx";
import LoadingState from "../components/LoadingState.jsx";
import { useApiResource } from "./useApiResource.js";

const playerDots = [
  ["GOL", "50%", "90%"],
  ["LD", "82%", "68%"],
  ["ZAG", "60%", "70%"],
  ["ZAG", "40%", "70%"],
  ["LE", "18%", "68%"],
  ["VOL", "42%", "52%"],
  ["VOL", "58%", "52%"],
  ["MEI", "50%", "34%"],
  ["PD", "78%", "24%"],
  ["PE", "22%", "24%"],
  ["ATA", "50%", "14%"]
];

export default function TacticalDossier() {
  const { teamId } = useParams();
  const { data, loading, error } = useApiResource(async () => {
    const [team, dossier] = await Promise.all([api.team(teamId), api.tacticalAnalysis(teamId)]);
    return { team, dossier };
  }, [teamId]);

  if (loading) return <LoadingState />;
  if (error) return <ErrorState message={error} />;

  const { team, dossier } = data;

  return (
    <section className="page-grid">
      <div className="team-hero">
        <div>
          <p className="eyebrow">{team.league}</p>
          <h2>{team.name}</h2>
          <p>{team.style}</p>
        </div>
        <div className="hero-actions">
          <ConfidenceBadge level={dossier.confidence_level} />
          <Link className="button button-primary" to={`/team/${team.id}/report`}>
            Relatório
            <ArrowRight size={16} />
          </Link>
        </div>
      </div>

      <div className="dossier-layout">
        <section className="pitch-panel">
          <div className="tactical-pitch" aria-label={`Formação base ${team.base_formation}`}>
            {playerDots.map(([label, x, y]) => (
              <span key={`${label}-${x}-${y}`} style={{ left: x, top: y }}>
                {label}
              </span>
            ))}
          </div>
          <div className="pitch-caption">
            <CircleDot size={16} />
            Formação base: {team.base_formation}
          </div>
        </section>

        <section className="analysis-stack">
          <article>
            <h3>Perfil do clube</h3>
            <dl className="meta-grid">
              <div>
                <dt>País</dt>
                <dd>{team.country}</dd>
              </div>
              <div>
                <dt>Técnico</dt>
                <dd>{team.coach}</dd>
              </div>
              <div>
                <dt>Status</dt>
                <dd>{team.status}</dd>
              </div>
              <div>
                <dt>Confiança</dt>
                <dd>{dossier.confidence_level}</dd>
              </div>
            </dl>
          </article>
          <article>
            <h3>Resumo tático</h3>
            <p>{dossier.summary}</p>
          </article>
        </section>
      </div>

      <section className="card-grid two">
        <article className="info-panel">
          <h3>Modelo ofensivo</h3>
          <p>{dossier.offensive_model}</p>
        </article>
        <article className="info-panel">
          <h3>Modelo defensivo</h3>
          <p>{dossier.defensive_model}</p>
        </article>
        <article className="info-panel">
          <h3>Transição ofensiva</h3>
          <p>{dossier.offensive_transition}</p>
        </article>
        <article className="info-panel">
          <h3>Transição defensiva</h3>
          <p>{dossier.defensive_transition}</p>
        </article>
        <article className="info-panel">
          <h3>Bola parada</h3>
          <p>{dossier.set_pieces}</p>
        </article>
        <article className="info-panel">
          <h3>Variações</h3>
          <p>{dossier.formation_variations.join(" · ")}</p>
        </article>
      </section>

      <section className="two-column">
        <article>
          <h3>Pontos fortes</h3>
          <ul className="check-list">
            {dossier.strengths.map((item) => (
              <li key={item}>{item}</li>
            ))}
          </ul>
        </article>
        <article>
          <h3>Fragilidades</h3>
          <ul className="risk-list">
            {dossier.weaknesses.map((item) => (
              <li key={item}>{item}</li>
            ))}
          </ul>
        </article>
      </section>
    </section>
  );
}
