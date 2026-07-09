import { useParams } from "react-router-dom";

import { api } from "../api/client.js";
import ErrorState from "../components/ErrorState.jsx";
import LoadingState from "../components/LoadingState.jsx";
import SourceCard from "../components/SourceCard.jsx";
import VideoVisionPanel from "../components/VideoVisionPanel.jsx";
import { useApiResource } from "./useApiResource.js";

export default function SourcesVideos() {
  const { teamId } = useParams();
  const { data, loading, error } = useApiResource(async () => {
    const [team, sources, vision, publicIntelligence] = await Promise.all([
      api.team(teamId),
      api.sources(teamId),
      api.videoVision(teamId),
      api.publicIntelligence(teamId)
    ]);
    return { team, sources, vision, publicIntelligence };
  }, [teamId]);

  if (loading) return <LoadingState />;
  if (error) return <ErrorState message={error} />;

  return (
    <section className="page-grid">
      <div className="section-heading">
        <div>
          <p className="eyebrow">{data.team.name}</p>
          <h2>Fontes, videos e leitura visual</h2>
        </div>
      </div>
      <div className="notice-strip">
        Fontes locais, busca publica e leitura visual ficam separadas para revisao tecnica.
      </div>
      <VideoVisionPanel vision={data.vision} />
      <section className="online-search-panel public-intelligence-panel">
        <div>
          <h3>Inteligencia publica</h3>
          <p>{data.publicIntelligence.summary}</p>
          <span className="source-origin">{data.publicIntelligence.note}</span>
        </div>
        <span className="badge badge-medium">
          {data.publicIntelligence.status === "available" ? "Online" : "Modo local"}
        </span>
      </section>
      <div className="card-grid three">
        {data.sources.map((source) => (
          <SourceCard key={source.title} source={source} />
        ))}
      </div>
    </section>
  );
}
