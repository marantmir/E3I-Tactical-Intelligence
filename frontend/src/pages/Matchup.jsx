import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import { ShieldAlert, Swords, Users } from "lucide-react";

import { api } from "../api/client.js";
import ConfidenceBadge from "../components/ConfidenceBadge.jsx";
import ErrorState from "../components/ErrorState.jsx";
import LoadingState from "../components/LoadingState.jsx";
import { useTeamSelection } from "../context/TeamSelectionContext.jsx";

export default function Matchup() {
  const { teamId } = useParams();
  const { ownTeam, loading: loadingOwnTeam } = useTeamSelection();
  const [opponentWorkspace, setOpponentWorkspace] = useState(null);
  const [ownWorkspace, setOwnWorkspace] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const isOwnTeam = ownTeam && String(ownTeam.ref) === String(teamId);

  useEffect(() => {
    let active = true;
    setLoading(true);
    setError("");

    const requests = [api.teamWorkspace(teamId)];
    if (ownTeam && !isOwnTeam) {
      requests.push(api.teamWorkspace(ownTeam.ref));
    }

    Promise.all(requests)
      .then(([opponentData, ownData]) => {
        if (!active) return;
        setOpponentWorkspace(opponentData);
        setOwnWorkspace(ownData || null);
      })
      .catch((err) => {
        if (active) setError(err.message || "Erro ao carregar dados do confronto.");
      })
      .finally(() => {
        if (active) setLoading(false);
      });

    return () => {
      active = false;
    };
  }, [teamId, ownTeam, isOwnTeam]);

  if (loading || loadingOwnTeam) return <LoadingState />;
  if (error) return <ErrorState message={error} />;

  const opponent = opponentWorkspace?.team;

  return (
    <section className="page-grid">
      <div className="section-heading">
        <div>
          <p className="eyebrow">Confronto direto</p>
          <h2>
            <Swords size={20} style={{ verticalAlign: "middle", marginRight: "8px" }} />
            {opponent?.name}
          </h2>
        </div>
      </div>

      {!ownTeam ? (
        <div className="empty-state">
          <h2>Defina o seu time</h2>
          <p>Nao foi possivel identificar o seu time. Saia e entre novamente na ferramenta para redefini-lo.</p>
        </div>
      ) : isOwnTeam ? (
        <div className="notice-strip">
          <ShieldAlert size={16} style={{ verticalAlign: "middle", marginRight: "6px" }} />
          {opponent?.name} e o seu time ativo. Um time nao disputa confronto contra si mesmo - selecione outro time
          para comparar.
        </div>
      ) : (
        <MatchupComparison ownWorkspace={ownWorkspace} opponentWorkspace={opponentWorkspace} />
      )}
    </section>
  );
}

function MatchupComparison({ ownWorkspace, opponentWorkspace }) {
  const own = ownWorkspace?.team;
  const opponent = opponentWorkspace?.team;
  const ownDossier = ownWorkspace?.dossier || {};
  const opponentDossier = opponentWorkspace?.dossier || {};
  const ownPlayers = ownWorkspace?.players || [];
  const opponentPlayers = opponentWorkspace?.players || [];

  return (
    <>
      <div className="card-grid two">
        <TeamSummaryCard label="Seu time" team={own} dossier={ownDossier} accent="badge-high" />
        <TeamSummaryCard label="Time analisado" team={opponent} dossier={opponentDossier} accent="badge-medium" />
      </div>

      <section className="two-column">
        <article>
          <h3>Pontos fortes do seu time</h3>
          <ul className="check-list">
            {(ownDossier.strengths || []).map((item) => (
              <li key={item}>{item}</li>
            ))}
          </ul>
        </article>
        <article>
          <h3>Fragilidades do adversario</h3>
          <ul className="risk-list">
            {(opponentDossier.weaknesses || []).map((item) => (
              <li key={item}>{item}</li>
            ))}
          </ul>
        </article>
      </section>

      <section className="two-column">
        <article>
          <h3>
            <Users size={16} style={{ verticalAlign: "middle", marginRight: "6px" }} />
            Elenco - seu time
          </h3>
          <PlayerList players={ownPlayers} />
        </article>
        <article>
          <h3>
            <Users size={16} style={{ verticalAlign: "middle", marginRight: "6px" }} />
            Elenco - adversario
          </h3>
          <PlayerList players={opponentPlayers} />
        </article>
      </section>

      <article className="info-panel">
        <h3>Formacoes em confronto</h3>
        <p>
          <strong>{own?.base_formation || "A definir"}</strong> ({own?.name}) contra{" "}
          <strong>{opponent?.base_formation || "A definir"}</strong> ({opponent?.name}).
        </p>
      </article>
    </>
  );
}

function TeamSummaryCard({ label, team, dossier, accent }) {
  return (
    <article className="info-panel">
      <div className="team-card-head">
        <div className="team-card-identity">
          {team?.crest_url ? <img className="team-crest" src={team.crest_url} alt={`Escudo de ${team.name}`} /> : null}
          <div>
            <p className="eyebrow">{label}</p>
            <h3>{team?.name || "A definir"}</h3>
          </div>
        </div>
        <span className={`badge ${accent}`}>{team?.base_formation || "A definir"}</span>
      </div>
      <p>{dossier.summary || "Sem resumo tatico disponivel ainda."}</p>
      <dl className="meta-grid">
        <div>
          <dt>Liga</dt>
          <dd>{team?.league || "Nao informado"}</dd>
        </div>
        <div>
          <dt>Confianca</dt>
          <dd>
            <ConfidenceBadge level={dossier.confidence_level || team?.confidence} />
          </dd>
        </div>
      </dl>
    </article>
  );
}

function PlayerList({ players }) {
  if (!players.length) {
    return <p className="team-style">Sem jogadores cadastrados para este time ainda.</p>;
  }

  return (
    <ul className="check-list">
      {players.slice(0, 8).map((player) => (
        <li key={player.name}>
          {player.name} - {player.position}
          {player.highlight ? ` (${player.highlight})` : ""}
        </li>
      ))}
    </ul>
  );
}
