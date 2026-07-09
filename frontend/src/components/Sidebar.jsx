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
  { to: "/new-analysis", label: "Nova análise", icon: ClipboardList },
  { to: "/search", label: "Buscar time", icon: Search },
  { to: "/team/1", label: "Dossiê", icon: ShieldCheck },
  { to: "/team/1/formations", label: "Formações", icon: LineChart },
  { to: "/team/1/squad", label: "Elenco", icon: UsersRound },
  { to: "/team/1/sources", label: "Fontes", icon: Video },
  { to: "/team/1/game-plan", label: "Plano", icon: ClipboardList },
  { to: "/team/1/report", label: "Relatório", icon: FileText },
  { to: "/history", label: "Histórico", icon: Archive },
  { to: "/future-ai", label: "IA futura", icon: BrainCircuit }
];

export default function Sidebar() {
  return (
    <aside className="sidebar">
      <div className="brand">
        <div className="brand-mark">E3I</div>
        <div>
          <strong>Tactical</strong>
          <span>Intelligence</span>
        </div>
      </div>
      <nav aria-label="Navegação principal">
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
