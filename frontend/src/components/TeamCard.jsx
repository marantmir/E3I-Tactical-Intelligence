import { ArrowRight, MapPin } from "lucide-react";
import { Link } from "react-router-dom";

import CategoryBadge from "./CategoryBadge.jsx";
import ConfidenceBadge from "./ConfidenceBadge.jsx";

export default function TeamCard({ team }) {
  const isOnlineProfile = team.profile_type === "online" || team.id === 0 || Boolean(team.online_search);
  const target =
    isOnlineProfile && team.online_profile_id
      ? `/team/online-${team.online_profile_id}/sources`
      : isOnlineProfile
        ? `/new-analysis?team=${encodeURIComponent(team.name)}`
        : `/team/${team.id}`;
  const actionLabel =
    isOnlineProfile && team.online_profile_id ? "Abrir coleta salva" : isOnlineProfile ? "Gerar pre-analise" : "Abrir dossie";

  return (
    <article className="team-card">
      <div className="team-card-head">
        <div className="team-card-identity">
          {team.crest_url ? <img className="team-crest" src={team.crest_url} alt={`Escudo de ${team.name}`} /> : null}
          <div>
            <p className="eyebrow">{team.country}</p>
            <h3>{team.name}</h3>
          </div>
        </div>
        <div className="team-card-badges">
          <CategoryBadge category={team.category} />
          <ConfidenceBadge level={team.confidence} />
        </div>
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
