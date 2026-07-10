import { useParams } from "react-router-dom";

import { api } from "../api/client.js";
import ErrorState from "../components/ErrorState.jsx";
import LoadingState from "../components/LoadingState.jsx";
import SourceCard from "../components/SourceCard.jsx";
import VideoVisionPanel from "../components/VideoVisionPanel.jsx";
import { useApiResource } from "./useApiResource.js";

export default function SourcesVideos() {
  const { teamId } = useParams();
  const { data, loading, error } = useApiResource(() => api.teamWorkspace(teamId), [teamId]);

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

      <div className="collection-summary">
        <article>
          <span>Fontes locais</span>
          <strong>{data.collection.local_source_count}</strong>
        </article>
        <article>
          <span>Fontes salvas</span>
          <strong>{data.collection.saved_source_count}</strong>
        </article>
        <article>
          <span>Videos mapeados</span>
          <strong>{data.collection.video_reference_count}</strong>
        </article>
        <article>
          <span>A coletar</span>
          <strong>{data.collection.to_collect.length}</strong>
        </article>
      </div>

      <div className="notice-strip">
        O time ativo agora centraliza o que ja foi coletado e o que ainda precisa ser coletado para analise visual.
      </div>

      <VideoVisionPanel teamRef={data.ref} teamName={data.team.name} />

      <section className="online-search-panel public-intelligence-panel">
        <div>
          <h3>Fontes taticas salvas</h3>
          <p>{data.public_intelligence.summary}</p>
          <span className="source-origin">{data.public_intelligence.note}</span>
        </div>
        <span className={data.collection.status === "com_coleta_salva" ? "badge badge-high" : "badge badge-medium"}>
          {data.collection.status === "com_coleta_salva" ? "Com coleta" : "A coletar"}
        </span>
      </section>

      {data.collection.to_collect.length > 0 ? (
        <section className="event-grid">
          {data.collection.to_collect.map((item) => (
            <article key={item.stage}>
              <h3>{item.stage}</h3>
              <p>{item.action}</p>
              <strong>Pendente para consolidar o dossie visual</strong>
            </article>
          ))}
        </section>
      ) : null}

      {data.sources.combined.length > 0 ? (
        <div className="card-grid three">
          {data.sources.combined.map((source) => (
            <SourceCard key={`${source.title}-${source.source}`} source={source} />
          ))}
        </div>
      ) : (
        <div className="empty-state">
          <h2>Nenhuma fonte salva ainda</h2>
          <p>Use a busca tatica por nome ou envie videos para iniciar a coleta deste time.</p>
        </div>
      )}
    </section>
  );
}
