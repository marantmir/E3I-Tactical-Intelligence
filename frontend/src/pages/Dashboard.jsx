import { ArrowRight, ClipboardList, FileText, Search, ShieldCheck, Video, UsersRound } from "lucide-react";
import { Link, useNavigate } from "react-router-dom";
import { useState } from "react";

import { api } from "../api/client.js";
import ErrorState from "../components/ErrorState.jsx";
import LoadingState from "../components/LoadingState.jsx";
import MetricCard from "../components/MetricCard.jsx";
import TeamCard from "../components/TeamCard.jsx";
import { useApiResource } from "./useApiResource.js";

export default function Dashboard() {
  const navigate = useNavigate();
  const [query, setQuery] = useState("");
  const { data, loading, error } = useApiResource(async () => {
    const [teams, history] = await Promise.all([api.teams(), api.history()]);
    return { teams, history };
  }, []);

  if (loading) return <LoadingState />;
  if (error) return <ErrorState message={error} />;

  const featuredTeams = data.teams.slice(0, 3);
  const latestHistory = data.history.slice(0, 4);

  function submitSearch(event) {
    event.preventDefault();
    navigate(`/search?query=${encodeURIComponent(query)}`);
  }

  return (
    <div className="page-grid">
      <section className="intro-panel">
        <div>
          <p className="eyebrow">Inteligência tática simulada</p>
          <h2>Central para dossiês, elenco, fontes e plano de jogo</h2>
          <p>
            Plataforma web para scouts, treinadores e analistas organizarem dados mockados de
            adversários em uma visão estruturada e acionável.
          </p>
        </div>
        <form className="quick-search" onSubmit={submitSearch}>
          <Search size={18} />
          <input
            aria-label="Buscar time"
            value={query}
            onChange={(event) => setQuery(event.target.value)}
            placeholder="Buscar Flamengo, Real Madrid..."
          />
          <button className="icon-button" type="submit" aria-label="Buscar">
            <ArrowRight size={18} />
          </button>
        </form>
        <div className="notice-strip">Protótipo com dados simulados - sem integração real com IA nesta versão.</div>
      </section>

      <section className="metric-grid" aria-label="Indicadores simulados">
        <MetricCard icon={ShieldCheck} label="Times cadastrados" value="10" tone="green" />
        <MetricCard icon={FileText} label="Relatórios simulados" value="24" tone="amber" />
        <MetricCard icon={Video} label="Vídeos mapeados" value="56" tone="red" />
        <MetricCard icon={UsersRound} label="Jogadores analisados" value="184" tone="blue" />
        <MetricCard icon={ClipboardList} label="Planos de jogo" value="12" tone="purple" />
      </section>

      <section>
        <div className="section-heading">
          <div>
            <p className="eyebrow">Times em destaque</p>
            <h2>Análises disponíveis</h2>
          </div>
          <Link className="button button-primary" to="/new-analysis">
            Nova análise
            <ArrowRight size={16} />
          </Link>
        </div>
        <div className="card-grid three">
          {featuredTeams.map((team) => (
            <TeamCard key={team.id} team={team} />
          ))}
        </div>
      </section>

      <section>
        <div className="section-heading">
          <div>
            <p className="eyebrow">Histórico</p>
            <h2>Últimas análises realizadas</h2>
          </div>
          <Link className="button button-secondary" to="/history">
            Ver histórico
            <ArrowRight size={16} />
          </Link>
        </div>
        <div className="table-wrap">
          <table>
            <thead>
              <tr>
                <th>Time</th>
                <th>Data</th>
                <th>Objetivo</th>
                <th>Formação</th>
                <th>Confiança</th>
                <th>Status</th>
              </tr>
            </thead>
            <tbody>
              {latestHistory.map((item) => (
                <tr key={item.id}>
                  <td>
                    <strong>{item.team_name}</strong>
                    <span>{item.user_profile}</span>
                  </td>
                  <td>{new Date(item.created_at).toLocaleDateString("pt-BR")}</td>
                  <td>{item.objective}</td>
                  <td>{item.base_formation}</td>
                  <td>{item.confidence}</td>
                  <td>{item.status}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>
    </div>
  );
}
