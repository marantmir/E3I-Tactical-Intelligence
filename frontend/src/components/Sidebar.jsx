import { NavLink } from "react-router-dom";
import {
  Archive,
  BrainCircuit,
  ClipboardList,
  FileText,
  Home,
  LineChart,
  Search,
  ShieldCheck,
  Swords,
  UsersRound,
  Video
} from "lucide-react";

import { useTeamSelection } from "../context/TeamSelectionContext.jsx";

const staticLinks = [
  { to: "/", label: "Dashboard", icon: Home },
  { to: "/new-analysis", label: "Nova analise", icon: ClipboardList },
  { to: "/search", label: "Buscar time", icon: Search },
  { to: "/meu-time", label: "Meu time", icon: ShieldCheck },
  { to: "/history", label: "Historico", icon: Archive },
  { to: "/future-ai", label: "IA avancada", icon: BrainCircuit }
];

export default function Sidebar() {
  const { selectedRef, ownTeamRef } = useTeamSelection();
  const activeRef = selectedRef || "1";
  const isOwnTeamActive = ownTeamRef && String(ownTeamRef) === String(activeRef);
  const teamLinks = [
    { to: `/team/${activeRef}`, label: "Dossie", icon: ShieldCheck },
    { to: `/team/${activeRef}/formations`, label: "Formacoes", icon: LineChart },
    { to: `/team/${activeRef}/squad`, label: "Elenco", icon: UsersRound },
    { to: `/team/${activeRef}/sources`, label: "Fontes", icon: Video },
    { to: `/team/${activeRef}/game-plan`, label: "Plano", icon: ClipboardList },
    { to: `/team/${activeRef}/report`, label: "Relatorio", icon: FileText },
    ...(isOwnTeamActive ? [] : [{ to: `/team/${activeRef}/matchup`, label: "Confronto", icon: Swords }])
  ];
  const links = [...staticLinks.slice(0, 4), ...teamLinks, ...staticLinks.slice(4)];

  return (
    <aside className="sidebar">
      <div className="brand">
        <img className="brand-logo" src="/logo-e3i.png" alt="E3I Solucoes" />
      </div>
      <nav aria-label="Navegacao principal">
        {links.map(({ to, label, icon: Icon }) => (
          <NavLink key={to} to={to} end={to === "/"}>
            <Icon size={18} />
            <span>{label}</span>
          </NavLink>
        ))}
      </nav>
    </aside>
  );
}
