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
  UsersRound,
  Video
} from "lucide-react";

const links = [
  { to: "/", label: "Dashboard", icon: Home },
  { to: "/new-analysis", label: "Nova analise", icon: ClipboardList },
  { to: "/search", label: "Buscar time", icon: Search },
  { to: "/team/1", label: "Dossie", icon: ShieldCheck },
  { to: "/team/1/formations", label: "Formacoes", icon: LineChart },
  { to: "/team/1/squad", label: "Elenco", icon: UsersRound },
  { to: "/team/1/sources", label: "Fontes", icon: Video },
  { to: "/team/1/game-plan", label: "Plano", icon: ClipboardList },
  { to: "/team/1/report", label: "Relatorio", icon: FileText },
  { to: "/history", label: "Historico", icon: Archive },
  { to: "/future-ai", label: "IA avancada", icon: BrainCircuit }
];

export default function Sidebar() {
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
