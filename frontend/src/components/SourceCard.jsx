import { CalendarDays, ExternalLink } from "lucide-react";
import { useState } from "react";

export default function SourceCard({ source }) {
  const [open, setOpen] = useState(false);

  return (
    <article className="source-card">
      <div className="source-head">
        <span className="source-type">{source.type}</span>
        <span className="relevance">{source.relevance}</span>
      </div>
      <h3>{source.title}</h3>
      <p className="source-origin">{source.source}</p>
      <p className="date-line">
        <CalendarDays size={15} />
        {new Date(source.date).toLocaleDateString("pt-BR", { timeZone: "UTC" })}
      </p>
      <p>{source.summary}</p>
      {open ? (
        <div className="detail-panel">
          <strong>Detalhe simulado</strong>
          <p>
            Este card representa uma fonte que futuramente poderia ser validada por APIs,
            RAG, transcrição de vídeo ou curadoria técnica.
          </p>
        </div>
      ) : null}
      <button className="button button-ghost" type="button" onClick={() => setOpen((value) => !value)}>
        <ExternalLink size={16} />
        {open ? "Ocultar detalhes" : "Ver detalhes"}
      </button>
    </article>
  );
}
