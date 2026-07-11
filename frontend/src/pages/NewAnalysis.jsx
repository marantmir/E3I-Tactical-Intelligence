import { Activity, Globe2, Save, UserPlus } from "lucide-react";
import { useEffect, useMemo, useState } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";

import { api } from "../api/client.js";
import { findExistingTeamByName, registerTeamFromOnlineSearch } from "../api/teamRegistration.js";
import { useTeamSelection } from "../context/TeamSelectionContext.jsx";

const objectives = [
  "Análise de adversário",
  "Scouting de jogadores",
  "Preparação de jogo",
  "Avaliação de elenco",
  "Relatório para comissão técnica"
];

const profiles = [
  "Scout",
  "Treinador",
  "Analista de desempenho",
  "Coordenador técnico",
  "Gestor esportivo"
];

export default function NewAnalysis() {
  const navigate = useNavigate();
  const [params] = useSearchParams();
  const { setLastSearchedName, refreshOptions } = useTeamSelection();
  const [teams, setTeams] = useState([]);
  const [message, setMessage] = useState("");
  const [saving, setSaving] = useState(false);
  const [analyzing, setAnalyzing] = useState(false);
  const [preview, setPreview] = useState(null);
  const [existence, setExistence] = useState(null);
  const [checkingExistence, setCheckingExistence] = useState(false);
  const [registering, setRegistering] = useState(false);
  const [form, setForm] = useState({
    team_name: params.get("team") || "Flamengo",
    competition: "Brasileirão Série A",
    season: "2026",
    objective: objectives[0],
    user_profile: profiles[2]
  });

  useEffect(() => {
    api.teams().then(setTeams).catch(() => setTeams([]));
  }, []);

  const selectedTeam = useMemo(() => {
    return teams.find((team) => team.name.toLowerCase() === form.team_name.toLowerCase());
  }, [teams, form.team_name]);

  function buildPayload() {
    return {
      ...form,
      team_id: selectedTeam?.id
    };
  }

  function updateField(event) {
    const { name, value } = event.target;
    setForm((current) => ({ ...current, [name]: value }));
    setPreview(null);
    setMessage("");
    if (name === "team_name") {
      setExistence(null);
    }
  }

  async function checkTeamExistence() {
    const cleaned = form.team_name.trim();
    if (!cleaned) return;
    setCheckingExistence(true);
    try {
      const result = await findExistingTeamByName(cleaned);
      setExistence(result);
      if (result.found) {
        setLastSearchedName(result.name);
      }
    } catch (err) {
      setMessage(err.message || "Nao foi possivel verificar o time.");
    } finally {
      setCheckingExistence(false);
    }
  }

  async function registerTeam() {
    if (!existence || existence.found) return;
    setRegistering(true);
    setMessage("");
    try {
      const { ref, name } = await registerTeamFromOnlineSearch(existence.name, existence.online);
      await refreshOptions();
      setLastSearchedName(name);
      setExistence({ found: true, ref, name });
      setMessage(`${name} cadastrado com sucesso. Voce ja pode analisar.`);
    } catch (err) {
      setMessage(err.message || "Nao foi possivel cadastrar o time.");
    } finally {
      setRegistering(false);
    }
  }

  async function analyze() {
    setAnalyzing(true);
    setMessage("");
    try {
      const result = await api.previewAnalysis(buildPayload());
      setPreview(result);
      setMessage(
        result.save_ready
          ? "Pré-análise gerada. Revise os insights antes de salvar."
          : "Pré-análise gerada, mas o time precisa de validação antes de salvar."
      );
    } catch (err) {
      setMessage(err.message || "Não foi possível gerar a pré-análise.");
    } finally {
      setAnalyzing(false);
    }
  }

  async function submit(event) {
    event.preventDefault();
    if (!preview?.save_ready) {
      setMessage("Gere e revise a pré-análise antes de salvar.");
      return;
    }

    setSaving(true);
    setMessage("");
    try {
      const record = await api.createAnalysis(buildPayload());
      setMessage(`Análise salva para ${record.team_name}.`);
      navigate(record.team_id ? `/team/${record.team_id}` : "/history");
    } catch (err) {
      setMessage(err.message || "Não foi possível salvar a análise.");
    } finally {
      setSaving(false);
    }
  }

  return (
    <section className="form-page">
      <div className="section-heading">
        <div>
          <p className="eyebrow">Fluxo de análise</p>
          <h2>Nova análise</h2>
        </div>
      </div>
      <form className="analysis-form" onSubmit={submit}>
        <label>
          Nome do time
          <input
            list="team-options"
            name="team_name"
            value={form.team_name}
            onChange={updateField}
            onBlur={checkTeamExistence}
          />
          <datalist id="team-options">
            {teams.map((team) => (
              <option key={team.id} value={team.name} />
            ))}
          </datalist>
        </label>
        {checkingExistence ? <span className="inline-message">Verificando time...</span> : null}
        {existence?.found ? (
          <span className="inline-message">{existence.name} selecionado (ja esta na base).</span>
        ) : null}
        {existence && !existence.found ? (
          <div className="notice-strip">
            "{existence.name}" ainda nao esta cadastrado.
            <button
              className="button button-primary"
              type="button"
              onClick={registerTeam}
              disabled={registering}
              style={{ marginLeft: "12px" }}
            >
              <UserPlus size={16} />
              {registering ? "Cadastrando..." : "Cadastrar time"}
            </button>
          </div>
        ) : null}
        <label>
          Competição
          <input name="competition" value={form.competition} onChange={updateField} />
        </label>
        <label>
          Temporada
          <input name="season" value={form.season} onChange={updateField} />
        </label>
        <label>
          Objetivo da análise
          <select name="objective" value={form.objective} onChange={updateField}>
            {objectives.map((objective) => (
              <option key={objective}>{objective}</option>
            ))}
          </select>
        </label>
        <label>
          Perfil do usuário
          <select name="user_profile" value={form.user_profile} onChange={updateField}>
            {profiles.map((profile) => (
              <option key={profile}>{profile}</option>
            ))}
          </select>
        </label>
        <div className="form-actions">
          <button className="button button-primary" type="button" onClick={analyze} disabled={analyzing}>
            <Activity size={16} />
            {analyzing ? "Analisando..." : "Analisar"}
          </button>
          <button className="button button-secondary" type="submit" disabled={saving || !preview?.save_ready}>
            <Save size={16} />
            {saving ? "Salvando..." : "Salvar análise"}
          </button>
          {message ? <span className="inline-message">{message}</span> : null}
        </div>
      </form>

      {preview ? <PreAnalysisPreview preview={preview} /> : null}
    </section>
  );
}

function PreAnalysisPreview({ preview }) {
  const online = preview.online_search;
  const analysis = preview.pre_analysis;
  const llmPreAnalysis = preview.llm_pre_analysis;
  const onlineStatus = formatOnlineStatus(online.status);

  return (
    <section className="preview-panel">
      <div className="section-heading">
        <div>
          <p className="eyebrow">Pré-análise</p>
          <h2>{preview.team.name}</h2>
        </div>
        <span className={preview.save_ready ? "badge badge-high" : "badge badge-low"}>
          {preview.save_ready ? "Pronta para salvar" : "Requer validação"}
        </span>
      </div>

      <article className="info-panel">
        <h3>Resumo preliminar</h3>
        <p>{analysis.summary}</p>
      </article>

      {llmPreAnalysis ? (
        <article className="info-panel ai-insight-panel">
          <h3>Apoio LLM para a pre-analise</h3>
          <p>{llmPreAnalysis.summary}</p>
          {llmPreAnalysis.questions?.length > 0 ? (
            <ul className="check-list">
              {llmPreAnalysis.questions.map((item) => (
                <li key={item}>{item}</li>
              ))}
            </ul>
          ) : null}
          {llmPreAnalysis.next_actions?.length > 0 ? (
            <ul className="check-list">
              {llmPreAnalysis.next_actions.map((item) => (
                <li key={item}>{item}</li>
              ))}
            </ul>
          ) : null}
        </article>
      ) : null}

      <div className="online-search-panel">
        <div>
          <h3>
            <Globe2 size={17} />
            Busca online
          </h3>
          <p>{online.summary}</p>
          <span className="source-origin">{online.note}</span>
        </div>
        <span className={onlineStatus.className}>{onlineStatus.label}</span>
      </div>

      {online.sources.length > 0 ? (
        <div className="card-grid three">
          {online.sources.map((source) => (
            <article className="source-card" key={source.url || source.title}>
              <div className="source-head">
                <span className="source-type">{source.origin}</span>
                <span className="relevance">{source.relevance}</span>
              </div>
              <h3>{source.title}</h3>
              <p>{source.summary || "Fonte publica encontrada para revisão do analista."}</p>
              {source.url ? (
                <a className="button button-ghost" href={source.url} target="_blank" rel="noreferrer">
                  Abrir fonte
                </a>
              ) : null}
            </article>
          ))}
        </div>
      ) : null}

      <section className="two-column">
        <article>
          <h3>Focos recomendados</h3>
          <ul className="check-list">
            {analysis.recommended_focus.map((item) => (
              <li key={item}>{item}</li>
            ))}
          </ul>
        </article>
        <article>
          <h3>Pesquisa operacional</h3>
          <ul className="check-list">
            {analysis.operational_research_insights.map((item) => (
              <li key={item}>{item}</li>
            ))}
          </ul>
        </article>
      </section>

      <section className="two-column">
        <article>
          <h3>Grafos táticos</h3>
          <ul className="check-list">
            {analysis.graph_insights.map((item) => (
              <li key={item}>{item}</li>
            ))}
          </ul>
        </article>
        <article>
          <h3>Visão computacional</h3>
          <ul className="check-list">
            {analysis.computer_vision_insights.map((item) => (
              <li key={item}>{item}</li>
            ))}
          </ul>
        </article>
      </section>
    </section>
  );
}

function formatOnlineStatus(status) {
  const statusMap = {
    available: { label: "Online", className: "badge badge-high" },
    partial: { label: "Parcial", className: "badge badge-medium" },
    guided_fallback: { label: "Busca guiada", className: "badge badge-medium" },
    llm_enriched: { label: "LLM", className: "badge badge-high" },
    empty: { label: "Sem resultado", className: "badge badge-medium" },
    local_fallback: { label: "Modo local", className: "badge badge-medium" }
  };

  return statusMap[status] || { label: "Em revisao", className: "badge badge-medium" };
}
