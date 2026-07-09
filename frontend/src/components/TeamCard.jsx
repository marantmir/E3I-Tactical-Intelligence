import { ArrowRight, MapPin } from "lucide-react";
import { Link } from "react-router-dom";

import ConfidenceBadge from "./ConfidenceBadge.jsx";

export default function TeamCard({ team }) {
  const isOnlineProfile = team.id === 0 || Boolean(team.online_search);
  const target = isOnlineProfile ? `/new-analysis?team=${encodeURIComponent(team.name)}` : `/team/${team.id}`;
  const actionLabel = isOnlineProfile ? "Gerar pre-analise" : "Abrir dossie";

  return (
    <article className="team-card">
      <div className="team-card-head">
        <div>
          <p className="eyebrow">{team.country}</p>
          <h3>{team.name}</h3>
        </div>
        <ConfidenceBadge level={team.confidence} />
      </div>
      <dl className="meta-grid">
        <div>
          <dt>Liga</dt>
          <dd>{team.league}</dd>
        </div>
        <div>
          <dt>Formacao</dt>
          <dd>{team.base_formation}</dd>
        </div>
        <div>
          <dt>Tecnico</dt>
          <dd>{team.coach}</dd>
        </div>
        <div>
          <dt>Status</dt>
          <dd>{team.status}</dd>
        </div>
      </dl>
      <p className="team-style">
        <MapPin size={16} />
        {team.style}
      </p>
      <Link className="button button-secondary" to={target}>
        {actionLabel}
        <ArrowRight size={16} />
      </Link>
    </article>
  );
}
