import { CalendarDays, ExternalLink, Link2 } from "lucide-react";
import { useState } from "react";

function isHttpUrl(value) {
  return /^https?:\/\//i.test(String(value || "").trim());
}

function prettyUrlLabel(url) {
  try {
    const parsed = new URL(url);
    const host = parsed.hostname.replace(/^www\./, "");
    const query = parsed.searchParams.get("search_query") || parsed.searchParams.get("q");
    if (query) {
      const term = decodeURIComponent(query);
      return `${host} · ${term.length > 48 ? `${term.slice(0, 48)}…` : term}`;
    }
    const path = `${parsed.pathname}`.replace(/\/$/, "");
    const shownPath = path && path !== "" ? path : "";
    const label = `${host}${shownPath}`;
    return label.length > 60 ? `${label.slice(0, 60)}…` : label;
  } catch {
    return url;
  }
}

export default function SourceCard({ source }) {
  const [open, setOpen] = useState(false);
  const sourceIsUrl = isHttpUrl(source.source);

  return (
    <article className="source-card">
      <div className="source-head">
        <span className="source-type">{source.type}</span>
        <span className="relevance">{source.relevance}</span>
      </div>
      <h3>{source.title}</h3>
      {sourceIsUrl ? (
        <a className="source-origin source-origin-link" href={source.source} target="_blank" rel="noreferrer">
          <Link2 size={14} />
          <span>{prettyUrlLabel(source.source)}</span>
        </a>
      ) : (
        <p className="source-origin">{source.source}</p>
      )}
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
          {sourceIsUrl ? <p className="source-full-url">{source.source}</p> : null}
        </div>
      ) : null}
      <div className="source-actions">
        <button className="button button-ghost" type="button" onClick={() => setOpen((value) => !value)}>
          {open ? "Ocultar detalhes" : "Ver detalhes"}
        </button>
        {sourceIsUrl ? (
          <a className="button button-ghost" href={source.source} target="_blank" rel="noreferrer">
            <ExternalLink size={16} />
            Abrir fonte
          </a>
        ) : null}
      </div>
    </article>
  );
}
