import { Search } from "lucide-react";
import { useEffect, useState } from "react";
import { useSearchParams } from "react-router-dom";

import { api } from "../api/client.js";
import ErrorState from "../components/ErrorState.jsx";
import LoadingState from "../components/LoadingState.jsx";
import TeamCard from "../components/TeamCard.jsx";

export default function TeamSearch() {
  const [params] = useSearchParams();
  const [query, setQuery] = useState(params.get("query") || "");
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    setLoading(true);
    api
      .searchTeams(query)
      .then(setResults)
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  }, [query]);

  if (loading) return <LoadingState />;
  if (error) return <ErrorState message={error} />;

  return (
    <section>
      <div className="section-heading">
        <div>
          <p className="eyebrow">Busca mockada</p>
          <h2>Buscar time</h2>
        </div>
      </div>
      <div className="search-panel">
        <Search size={18} />
        <input
          aria-label="Buscar time"
          value={query}
          onChange={(event) => setQuery(event.target.value)}
          placeholder="Digite o nome do time"
        />
      </div>
      <div className="card-grid three">
        {results.map((team) => (
          <TeamCard key={team.id} team={team} />
        ))}
      </div>
      {results.length === 0 ? (
        <div className="empty-state">
          <h2>Nenhum time encontrado</h2>
          <p>A base mockada contém Flamengo, Palmeiras, Corinthians, São Paulo e clubes europeus.</p>
        </div>
      ) : null}
    </section>
  );
}
