import { useMemo, useState } from "react";
import { Database, ListChecks, ShieldCheck, UsersRound } from "lucide-react";

import { api } from "../api/client.js";
import CrudManager from "../components/CrudManager.jsx";
import ErrorState from "../components/ErrorState.jsx";
import LoadingState from "../components/LoadingState.jsx";
import { useTeamSelection } from "../context/TeamSelectionContext.jsx";
import { useApiResource } from "./useApiResource.js";

const CONFIDENCE = ["Alto", "Medio", "Baixo"];
const INFLUENCE = ["Alta", "Media", "Baixa"];
const RELEVANCE = ["Alta", "Media", "Baixa"];
const CATEGORY = ["Masculino", "Feminino"];

export default function Admin() {
  const { isAdmin } = useTeamSelection();
  const { data: meta, loading, error } = useApiResource(() => api.adminMeta(), []);
  const [tab, setTab] = useState("users");

  const teamOptions = useMemo(
    () => (meta?.teams || []).map((team) => ({ value: team.id, label: `${team.name} (#${team.id})` })),
    [meta]
  );
  const teamName = useMemo(() => {
    const lookup = new Map((meta?.teams || []).map((team) => [team.id, team.name]));
    return (id) => lookup.get(Number(id)) || `#${id}`;
  }, [meta]);

  const collectionApi = useMemo(() => {
    const build = (collection) => ({
      list: () => api.adminList(collection),
      create: (payload) => api.adminCreate(collection, payload),
      update: (id, payload) => api.adminUpdate(collection, id, payload),
      remove: (id) => api.adminDelete(collection, id)
    });
    return {
      teams: build("teams"),
      players: build("players"),
      formations: build("formations"),
      sources: build("sources")
    };
  }, []);

  const usersApi = useMemo(
    () => ({
      list: () => api.adminUsers(),
      create: (payload) => api.adminCreateUser(payload),
      update: (id, payload) => api.adminUpdateUser(id, payload),
      remove: (id) => api.adminDeleteUser(id)
    }),
    []
  );

  if (!isAdmin) {
    return (
      <div className="empty-state">
        <h2>Acesso restrito</h2>
        <p>
          Esta area e exclusiva para perfis de administracao. Entre novamente escolhendo o perfil
          "Administrador" ou "Gestor esportivo" na tela inicial.
        </p>
      </div>
    );
  }

  if (loading) return <LoadingState />;
  if (error) return <ErrorState message={error} />;

  const tabs = [
    { key: "users", label: "Acessos", icon: ShieldCheck },
    { key: "teams", label: "Times", icon: Database },
    { key: "players", label: "Jogadores", icon: UsersRound },
    { key: "formations", label: "Formacoes", icon: ListChecks },
    { key: "sources", label: "Fontes", icon: Database }
  ];

  return (
    <div className="page-grid">
      <div className="section-heading">
        <div>
          <p className="eyebrow">Administracao</p>
          <h2>Controle de acesso e manutencao das informacoes</h2>
          <p>Insira, edite e exclua usuarios e os dados taticos da base local.</p>
        </div>
      </div>

      <div className="segmented-control admin-tabs" aria-label="Secoes de administracao">
        {tabs.map((item) => {
          const Icon = item.icon;
          return (
            <button
              key={item.key}
              className={tab === item.key ? "active" : ""}
              type="button"
              onClick={() => setTab(item.key)}
            >
              <Icon size={15} />
              {item.label}
            </button>
          );
        })}
      </div>

      {tab === "users" ? (
        <CrudManager
          title="Usuarios e acesso"
          description="Quem pode usar a ferramenta, com papel, status e areas liberadas."
          api={usersApi}
          emptyLabel="Nenhum usuario cadastrado"
          columns={[
            { key: "name", label: "Nome" },
            { key: "email", label: "Email" },
            { key: "role", label: "Papel" },
            {
              key: "status",
              label: "Status",
              render: (r) => (
                <span className={`badge ${r.status === "Ativo" ? "badge-high" : "badge-low"}`}>{r.status}</span>
              )
            },
            { key: "areas", label: "Areas", render: (r) => (r.areas || []).join(", ") || "-" }
          ]}
          fields={[
            { name: "name", label: "Nome", required: true },
            { name: "email", label: "Email", required: true },
            { name: "role", label: "Papel", type: "select", options: meta.roles, required: true },
            { name: "status", label: "Status", type: "select", options: meta.statuses, required: true },
            { name: "areas", label: "Areas liberadas", type: "tags", options: meta.areas }
          ]}
        />
      ) : null}

      {tab === "teams" ? (
        <CrudManager
          title="Times"
          description="Cadastro de times da base local (aparecem em todas as telas)."
          api={collectionApi.teams}
          emptyLabel="Nenhum time cadastrado"
          columns={[
            { key: "name", label: "Nome" },
            { key: "league", label: "Liga" },
            { key: "category", label: "Categoria" },
            { key: "base_formation", label: "Formacao base" },
            { key: "confidence", label: "Confianca" }
          ]}
          fields={[
            { name: "name", label: "Nome", required: true },
            { name: "country", label: "Pais" },
            { name: "league", label: "Liga" },
            { name: "category", label: "Categoria", type: "select", options: CATEGORY },
            { name: "base_formation", label: "Formacao base" },
            { name: "coach", label: "Tecnico" },
            { name: "confidence", label: "Confianca", type: "select", options: CONFIDENCE },
            { name: "status", label: "Status" },
            { name: "style", label: "Estilo de jogo", type: "textarea" }
          ]}
        />
      ) : null}

      {tab === "players" ? (
        <CrudManager
          title="Jogadores (elenco)"
          description="Elenco por time, com metricas usadas na analise e no grafo."
          api={collectionApi.players}
          emptyLabel="Nenhum jogador cadastrado"
          columns={[
            { key: "name", label: "Nome" },
            { key: "team", label: "Time", render: (r) => teamName(r.team_id) },
            { key: "position", label: "Pos" },
            { key: "goals", label: "G" },
            { key: "assists", label: "A" },
            { key: "tactical_score", label: "Nota" }
          ]}
          fields={[
            { name: "team_id", label: "Time", type: "select", options: teamOptions, required: true },
            { name: "name", label: "Nome", required: true },
            { name: "position", label: "Posicao" },
            { name: "age", label: "Idade", type: "number" },
            { name: "minutes", label: "Minutos", type: "number" },
            { name: "goals", label: "Gols", type: "number" },
            { name: "assists", label: "Assistencias", type: "number" },
            { name: "tactical_score", label: "Nota tatica", type: "number" },
            { name: "influence", label: "Influencia", type: "select", options: INFLUENCE },
            { name: "risk_level", label: "Risco", type: "select", options: CONFIDENCE },
            { name: "status", label: "Status" },
            { name: "highlight", label: "Destaque" }
          ]}
        />
      ) : null}

      {tab === "formations" ? (
        <CrudManager
          title="Formacoes"
          description="Formacoes provaveis por time, com contexto, vantagens e riscos."
          api={collectionApi.formations}
          emptyLabel="Nenhuma formacao cadastrada"
          columns={[
            { key: "team", label: "Time", render: (r) => teamName(r.team_id) },
            { key: "formation", label: "Formacao" },
            { key: "probability", label: "Prob (%)" },
            { key: "context", label: "Contexto" }
          ]}
          fields={[
            { name: "team_id", label: "Time", type: "select", options: teamOptions, required: true },
            { name: "formation", label: "Formacao", required: true },
            { name: "probability", label: "Probabilidade (%)", type: "number" },
            { name: "context", label: "Contexto", type: "textarea" },
            { name: "advantages", label: "Vantagens", type: "textarea" },
            { name: "risks", label: "Riscos", type: "textarea" }
          ]}
        />
      ) : null}

      {tab === "sources" ? (
        <CrudManager
          title="Fontes"
          description="Fontes taticas por time (videos, analises, referencias)."
          api={collectionApi.sources}
          emptyLabel="Nenhuma fonte cadastrada"
          columns={[
            { key: "team", label: "Time", render: (r) => teamName(r.team_id) },
            { key: "title", label: "Titulo" },
            { key: "type", label: "Tipo" },
            { key: "relevance", label: "Relevancia" },
            { key: "date", label: "Data" }
          ]}
          fields={[
            { name: "team_id", label: "Time", type: "select", options: teamOptions, required: true },
            { name: "title", label: "Titulo", required: true },
            { name: "type", label: "Tipo" },
            { name: "source", label: "Fonte/URL" },
            { name: "date", label: "Data", help: "AAAA-MM-DD" },
            { name: "relevance", label: "Relevancia", type: "select", options: RELEVANCE },
            { name: "summary", label: "Resumo", type: "textarea" }
          ]}
        />
      ) : null}
    </div>
  );
}
