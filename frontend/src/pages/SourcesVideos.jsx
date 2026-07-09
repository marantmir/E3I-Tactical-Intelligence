import { useParams } from "react-router-dom";

import { api } from "../api/client.js";
import ErrorState from "../components/ErrorState.jsx";
import LoadingState from "../components/LoadingState.jsx";
import SourceCard from "../components/SourceCard.jsx";
import { useApiResource } from "./useApiResource.js";

export default function SourcesVideos() {
  const { teamId } = useParams();
  const { data, loading, error } = useApiResource(async () => {
    const [team, sources] = await Promise.all([api.team(teamId), api.sources(teamId)]);
    return { team, sources };
  }, [teamId]);

  if (loading) return <LoadingState />;
  if (error) return <ErrorState message={error} />;

  return (
    <section>
      <div className="section-heading">
        <div>
          <p className="eyebrow">{data.team.name}</p>
          <h2>Fontes e vídeos simulados</h2>
        </div>
      </div>
      <div className="notice-strip">As fontes abaixo são mockadas e não executam busca real na internet.</div>
      <div className="card-grid three">
        {data.sources.map((source) => (
          <SourceCard key={source.title} source={source} />
        ))}
      </div>
    </section>
  );
}
