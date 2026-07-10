import { useMemo, useState } from "react";
import { useParams } from "react-router-dom";

import { api } from "../api/client.js";
import ErrorState from "../components/ErrorState.jsx";
import LoadingState from "../components/LoadingState.jsx";
import PlayerTable from "../components/PlayerTable.jsx";
import { useApiResource } from "./useApiResource.js";

export default function SquadAnalysis() {
  const { teamId } = useParams();
  const [filters, setFilters] = useState({
    position: "Todos",
    influence: "Todos",
    risk: "Todos",
    status: "Todos"
  });
  const { data, loading, error } = useApiResource(() => api.teamWorkspace(teamId), [teamId]);

  const filteredPlayers = useMemo(() => {
    if (!data?.players) return [];
    return data.players.filter((player) => {
      return (
        (filters.position === "Todos" || player.position === filters.position) &&
        (filters.influence === "Todos" || player.influence === filters.influence) &&
        (filters.risk === "Todos" || player.risk_level === filters.risk) &&
        (filters.status === "Todos" || player.status === filters.status)
      );
    });
  }, [data, filters]);

  if (loading) return <LoadingState />;
  if (error) return <ErrorState message={error} />;

  const options = {
    position: ["Todos", ...new Set(data.players.map((player) => player.position))],
    influence: ["Todos", "Alta", "Media", "Baixa"],
    risk: ["Todos", "Alto", "Medio", "Baixo"],
    status: ["Todos", "Titular", "Reserva"]
  };

  function updateFilter(event) {
    const { name, value } = event.target;
    setFilters((current) => ({ ...current, [name]: value }));
  }

  return (
    <section className="page-grid">
      <div className="section-heading">
        <div>
          <p className="eyebrow">{data.team.name}</p>
          <h2>Elenco e funcoes observaveis</h2>
        </div>
      </div>

      {data.players.length ? (
        <>
          <div className="highlight-grid">
            {data.players.slice(0, 5).map((player) => (
              <article className="highlight-card" key={player.name}>
                <span>{player.highlight}</span>
                <strong>{player.name}</strong>
                <p>
                  {player.position} - influencia {player.influence} - risco {player.risk_level}
                </p>
              </article>
            ))}
          </div>
          <div className="filter-bar">
            <label>
              Posicao
              <select name="position" value={filters.position} onChange={updateFilter}>
                {options.position.map((item) => (
                  <option key={item}>{item}</option>
                ))}
              </select>
            </label>
            <label>
              Influencia
              <select name="influence" value={filters.influence} onChange={updateFilter}>
                {options.influence.map((item) => (
                  <option key={item}>{item}</option>
                ))}
              </select>
            </label>
            <label>
              Risco
              <select name="risk" value={filters.risk} onChange={updateFilter}>
                {options.risk.map((item) => (
                  <option key={item}>{item}</option>
                ))}
              </select>
            </label>
            <label>
              Status
              <select name="status" value={filters.status} onChange={updateFilter}>
                {options.status.map((item) => (
                  <option key={item}>{item}</option>
                ))}
              </select>
            </label>
          </div>
          <PlayerTable players={filteredPlayers} />
        </>
      ) : (
        <section className="two-column">
          <article>
            <h3>Elenco ainda nao coletado</h3>
            <p>
              Este time vem de fonte tatica salva. Para preencher jogadores e funcoes, use videos com boa visibilidade
              e salve as evidencias geradas pela visao computacional.
            </p>
          </article>
          <article>
            <h3>Proximos passos</h3>
            <ul className="check-list">
              {data.collection.to_collect.map((item) => (
                <li key={item.stage}>
                  <strong>{item.stage}:</strong> {item.action}
                </li>
              ))}
            </ul>
          </article>
        </section>
      )}
    </section>
  );
}
