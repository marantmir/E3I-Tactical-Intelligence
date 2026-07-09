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
          <strong>Contexto de validacao</strong>
          <p>
            Esta fonte entra como evidencia de apoio para cruzar com busca publica, grafo tatico,
            leitura visual dos videos e revisao da comissao tecnica.
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
