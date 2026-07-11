import { ClipboardList, Database, Globe2, PlaySquare, Save, Search, Target } from "lucide-react";
import { useEffect, useState } from "react";
import { useSearchParams } from "react-router-dom";

import { api } from "../api/client.js";
import ErrorState from "../components/ErrorState.jsx";
import LoadingState from "../components/LoadingState.jsx";
import SourceCard from "../components/SourceCard.jsx";
import TeamCard from "../components/TeamCard.jsx";
import { useTeamSelection } from "../context/TeamSelectionContext.jsx";

export default function TeamSearch() {
  const [params] = useSearchParams();
  const { lastSearchedName } = useTeamSelection();
  const [query, setQuery] = useState(params.get("query") || lastSearchedName || "");
  const [mode, setMode] = useState("local");
  const [results, setResults] = useState([]);
  const [savedProfiles, setSavedProfiles] = useState([]);
  const [onlineResult, setOnlineResult] = useState(null);
  const [loadingLocal, setLoadingLocal] = useState(true);
  const [loadingOnline, setLoadingOnline] = useState(false);
  const [savingProfile, setSavingProfile] = useState(false);
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");

  useEffect(() => {
    loadSavedProfiles();
  }, []);

  useEffect(() => {
    if (mode !== "local") return;
    setLoadingLocal(true);
    setError("");
    api
      .searchTeams(query)
      .then(setResults)
      .catch((err) => setError(err.message))
      .finally(() => setLoadingLocal(false));
  }, [query, mode]);

  async function loadSavedProfiles() {
    try {
      const profiles = await api.onlineProfiles();
      setSavedProfiles(profiles);
    } catch {
      setSavedProfiles([]);
    }
  }

  async function handleOnlineSearch() {
    const name = query.trim();
    if (!name) {
      setMessage("Digite o nome do time para buscar material tatico.");
      return;
    }
    setLoadingOnline(true);
    setMessage("");
    setError("");
    try {
      const response = await api.onlineTeamSearch(name);
      setOnlineResult(response);
      setMessage(response.saved ? "Fonte tatica ja salva para uso futuro." : "Resultado tatico pronto para revisao.");
    } catch (err) {
      setError(err.message);
    } finally {
      setLoadingOnline(false);
    }
  }

  async function handleSaveOnlineProfile() {
    if (!onlineResult?.profile) return;
    setSavingProfile(true);
    setMessage("");
    try {
      const profile = onlineResult.profile;
      const saved = await api.saveOnlineProfile({
        team_name: profile.name,
        country: profile.country,
        league: profile.league,
        coach: profile.coach,
        base_formation: profile.base_formation,
        style: profile.style,
        confidence: profile.confidence,
        status: "Fonte tatica salva",
        online_search: onlineResult.online_search
      });
      setOnlineResult((current) => ({ ...current, saved: true, profile: saved }));
      setMessage("Fonte tatica salva para uso futuro.");
      await loadSavedProfiles();
    } catch (err) {
      setMessage(err.message || "Nao foi possivel salvar a fonte tatica.");
    } finally {
      setSavingProfile(false);
    }
  }

  if (mode === "local" && loadingLocal) return <LoadingState />;
  if (error) return <ErrorState message={error} />;

  return (
    <section className="page-grid">
      <div className="section-heading">
        <div>
          <p className="eyebrow">Busca local e tatica</p>
          <h2>Buscar time</h2>
        </div>
        <div className="segmented-control" aria-label="Tipo de busca">
          <button className={mode === "local" ? "active" : ""} type="button" onClick={() => setMode("local")}>
            <Database size={15} />
            Base local
          </button>
          <button className={mode === "online" ? "active" : ""} type="button" onClick={() => setMode("online")}>
            <Globe2 size={15} />
            Fontes taticas
          </button>
        </div>
      </div>

      <div className="search-panel search-panel-wide">
        <Search size={18} />
        <input
          aria-label="Buscar time"
          value={query}
          onChange={(event) => {
            setQuery(event.target.value);
            setMessage("");
          }}
          placeholder={mode === "online" ? "Digite apenas o nome do time" : "Digite o nome do time"}
        />
        {mode === "online" ? (
          <button className="icon-button" type="button" onClick={handleOnlineSearch} disabled={loadingOnline}>
            <Globe2 size={18} />
          </button>
        ) : null}
      </div>

      {message ? <span className="inline-message">{message}</span> : null}

      {mode === "local" ? (
        <>
          <div className="card-grid three">
            {results.map((team) => (
              <TeamCard key={`${team.id}-${team.name}`} team={team} />
            ))}
          </div>
          {results.length === 0 ? (
            <div className="empty-state">
              <h2>Nenhum time encontrado</h2>
              <p>Use a busca de fontes taticas para encontrar videos e analises pelo nome do time.</p>
            </div>
          ) : null}
        </>
      ) : (
        <OnlineSearchResult
          loading={loadingOnline}
          result={onlineResult}
          saving={savingProfile}
          onSave={handleSaveOnlineProfile}
        />
      )}

      {savedProfiles.length > 0 ? (
        <section className="saved-profile-panel">
          <div className="section-heading">
            <div>
              <p className="eyebrow">Uso futuro</p>
              <h2>Fontes taticas salvas</h2>
            </div>
          </div>
          <div className="card-grid three">
            {savedProfiles.map((team) => (
              <TeamCard key={team.id} team={team} />
            ))}
          </div>
        </section>
      ) : null}
    </section>
  );
}

function OnlineSearchResult({ loading, result, saving, onSave }) {
  if (loading) return <LoadingState />;
  if (!result) {
    return (
      <div className="empty-state">
        <h2>Busca tatica por nome</h2>
        <p>Digite o nome do time para buscar videos e analises taticas.</p>
      </div>
    );
  }

  const { profile, online_search: onlineSearch } = result;
  const groups = onlineSearch.source_groups || groupSources(onlineSearch.sources);
  const coverage = onlineSearch.coverage || {};

  return (
    <section className="online-result-layout">
      <article className="online-profile-card">
        <div className="team-card-head">
          <div>
            <p className="eyebrow">{profile.league}</p>
            <h3>{profile.name}</h3>
          </div>
          <span className={result.saved ? "badge badge-high" : "badge badge-medium"}>
            {result.saved ? "Salvo" : "Online"}
          </span>
        </div>
        <p>{profile.style}</p>
        <dl className="meta-grid">
          <div>
            <dt>Fontes</dt>
            <dd>{profile.source_count || onlineSearch.sources.length}</dd>
          </div>
          <div>
            <dt>Status</dt>
            <dd>{onlineSearch.status}</dd>
          </div>
          <div>
            <dt>Videos</dt>
            <dd>{(coverage.match_videos || 0) + (coverage.analysis_videos || 0)}</dd>
          </div>
          <div>
            <dt>Padroes</dt>
            <dd>{coverage.team_form || 0}</dd>
          </div>
        </dl>
        <p className="source-origin">{onlineSearch.note}</p>
        <button className="button button-primary" type="button" onClick={onSave} disabled={saving || result.saved}>
          <Save size={16} />
          {saving ? "Salvando..." : result.saved ? "Fonte salva" : "Salvar fonte"}
        </button>
      </article>

      <div className="online-intelligence-stack">
        {onlineSearch.analysis_focus?.length > 0 ? (
          <article className="online-insight-panel">
            <h3>
              <Target size={17} />
              Como analisar o comportamento visual
            </h3>
            <ul className="check-list">
              {onlineSearch.analysis_focus.map((item) => (
                <li key={item}>{item}</li>
              ))}
            </ul>
          </article>
        ) : null}

        {onlineSearch.collection_plan?.length > 0 ? (
          <article className="online-insight-panel">
            <h3>
              <ClipboardList size={17} />
              Plano de coleta
            </h3>
            <ul className="check-list">
              {onlineSearch.collection_plan.map((item) => (
                <li key={item.stage}>
                  <strong>{item.stage}:</strong> {item.action}
                </li>
              ))}
            </ul>
          </article>
        ) : null}

        {onlineSearch.llm_search ? (
          <article className="online-insight-panel ai-insight-panel">
            <h3>
              <Target size={17} />
              IA aplicada a busca tatica
            </h3>
            <p>{onlineSearch.llm_search.summary}</p>
            {onlineSearch.llm_search.priority_sources?.length > 0 ? (
              <ul className="check-list">
                {onlineSearch.llm_search.priority_sources.map((item) => (
                  <li key={item}>{item}</li>
                ))}
              </ul>
            ) : null}
            {onlineSearch.llm_search.tactical_hypotheses?.length > 0 ? (
              <ul className="check-list">
                {onlineSearch.llm_search.tactical_hypotheses.map((item) => (
                  <li key={item}>{item}</li>
                ))}
              </ul>
            ) : null}
          </article>
        ) : null}

        <div className="source-group-list">
          {sourceGroupConfig.map((group) =>
            groups[group.key]?.length ? (
              <section className="source-group-panel" key={group.key}>
                <div className="source-group-heading">
                  <group.icon size={18} />
                  <div>
                    <h3>{group.label}</h3>
                    <p>{group.description}</p>
                  </div>
                </div>
                <div className="card-grid two">
                  {groups[group.key].slice(0, 6).map((source) => (
                    <SourceCard
                      key={source.url || source.title}
                      source={{
                        title: source.title,
                        type: source.origin,
                        relevance: source.relevance,
                        source: source.url || "Fonte tatica",
                        date: source.published_at || new Date().toISOString(),
                        summary: source.summary || "Fonte tatica encontrada para revisao."
                      }}
                    />
                  ))}
                </div>
              </section>
            ) : null
          )}
        </div>
      </div>
    </section>
  );
}

const sourceGroupConfig = [
  {
    key: "match_videos",
    label: "Videos de jogos",
    description: "Melhores momentos e partidas para alimentar a leitura visual.",
    icon: PlaySquare
  },
  {
    key: "analysis_videos",
    label: "Videos de analise",
    description: "Conteudos que explicam modelo de jogo, pontos fortes e fragilidades.",
    icon: Target
  },
  {
    key: "team_form",
    label: "Como esta jogando",
    description: "Materiais para entender padroes de jogo, movimentacao e ocupacao.",
    icon: Globe2
  }
];

function groupSources(sources) {
  return sources.reduce((groups, source) => {
    const key = source.category || "team_form";
    return { ...groups, [key]: [...(groups[key] || []), source] };
  }, {});
}
