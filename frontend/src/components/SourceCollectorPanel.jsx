import { useState } from "react";
import { Globe, KeyRound, Link2, Save, Search } from "lucide-react";

import { api } from "../api/client.js";
import SourceCard from "./SourceCard.jsx";

const MODES = [
  {
    key: "link",
    label: "Link direto",
    icon: Link2,
    placeholder: "https://youtube.com/watch?v=... ou qualquer pagina tatica",
    hint: "A pagina e lida automaticamente (titulo e resumo) e registrada como fonte."
  },
  {
    key: "keyword",
    label: "Palavra-chave",
    icon: KeyRound,
    placeholder: "ex.: pressao alta, saida de bola, bola parada",
    hint: "Busca web publica combinando o time ativo com a palavra-chave."
  },
  {
    key: "api",
    label: "APIs publicas",
    icon: Globe,
    placeholder: "nome do clube (ex.: Palmeiras)",
    hint: "Consulta Wikipedia e TheSportsDB (gratuitas, sem chave) pela ficha do clube."
  }
];

export default function SourceCollectorPanel({ teamName, onSaved }) {
  const [mode, setMode] = useState("link");
  const [value, setValue] = useState("");
  const [result, setResult] = useState(null);
  const [collecting, setCollecting] = useState(false);
  const [saving, setSaving] = useState(false);
  const [savedMessage, setSavedMessage] = useState("");
  const [error, setError] = useState("");

  const activeMode = MODES.find((item) => item.key === mode);

  async function handleCollect(event) {
    event.preventDefault();
    if (!value.trim() || collecting) return;
    setCollecting(true);
    setError("");
    setSavedMessage("");
    setResult(null);
    try {
      const response = await api.collectSources({ mode, value: value.trim(), team_name: teamName });
      setResult(response);
    } catch (collectError) {
      setError(collectError.message || "Falha ao coletar fontes.");
    } finally {
      setCollecting(false);
    }
  }

  async function handleSave() {
    if (!result?.sources?.length || saving) return;
    setSaving(true);
    setError("");
    try {
      await api.collectSources({
        mode,
        value: value.trim() || result.value,
        team_name: teamName,
        save: true,
        sources: result.sources
      });
      setSavedMessage(`${result.sources.length} fonte(s) salvas na coleta de ${teamName}.`);
      onSaved?.();
    } catch (saveError) {
      setError(saveError.message || "Falha ao salvar as fontes coletadas.");
    } finally {
      setSaving(false);
    }
  }

  return (
    <section className="source-collector-panel">
      <div className="section-heading">
        <div>
          <p className="eyebrow">Coleta manual</p>
          <h3>Adicionar fontes por link, palavra-chave ou APIs publicas</h3>
        </div>
      </div>

      <div className="segmented-control" aria-label="Modo de coleta de fontes">
        {MODES.map((item) => {
          const Icon = item.icon;
          return (
            <button
              key={item.key}
              className={mode === item.key ? "active" : ""}
              type="button"
              onClick={() => {
                setMode(item.key);
                setResult(null);
                setError("");
                setSavedMessage("");
              }}
            >
              <Icon size={15} />
              {item.label}
            </button>
          );
        })}
      </div>

      <form className="source-collector-form" onSubmit={handleCollect}>
        <input
          placeholder={activeMode.placeholder}
          value={value}
          onChange={(event) => setValue(event.target.value)}
        />
        <button className="button button-primary" disabled={collecting || !value.trim()} type="submit">
          <Search size={16} />
          {collecting ? "Coletando..." : "Coletar"}
        </button>
      </form>
      <p className="video-caption">{activeMode.hint}</p>

      {error ? <p className="error-text">{error}</p> : null}
      {savedMessage ? <p className="inline-message">{savedMessage}</p> : null}

      {result ? (
        <>
          <div className="notice-strip">{result.note}</div>
          {result.errors?.length > 0 ? (
            <p className="video-caption">
              Falhas tratadas: {result.errors.map((item) => `${item.source} (${item.error})`).join(", ")}.
            </p>
          ) : null}
          {result.sources.length > 0 ? (
            <>
              <div className="card-grid three">
                {result.sources.map((source) => (
                  <SourceCard
                    key={`${source.title}-${source.url}`}
                    source={{
                      title: source.title,
                      type: source.origin,
                      source: source.url || source.origin,
                      date: result.retrieved_at || new Date().toISOString(),
                      relevance: source.relevance,
                      summary: source.summary,
                      category: source.category
                    }}
                  />
                ))}
              </div>
              <div className="action-row">
                <button className="button button-secondary" disabled={saving} type="button" onClick={handleSave}>
                  <Save size={16} />
                  {saving ? "Salvando..." : `Salvar ${result.sources.length} fonte(s) na coleta do time`}
                </button>
              </div>
            </>
          ) : (
            <div className="empty-state">
              <h2>Nada encontrado para este termo</h2>
              <p>Tente outro link, palavra-chave mais especifica ou o nome oficial do clube.</p>
            </div>
          )}
        </>
      ) : null}
    </section>
  );
}
