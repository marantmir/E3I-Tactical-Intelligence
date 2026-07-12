import { LogOut, UserCog } from "lucide-react";

import { useTeamSelection } from "../context/TeamSelectionContext.jsx";

export default function Header() {
  const { ownTeam, professionalProfile, logout } = useTeamSelection();

  return (
    <header className="topbar">
      <div className="topbar-brand">
        <div className="topbar-logo-frame">
          <img src="/logo-e3i.png" alt="E3I Solucoes" />
        </div>
        <div>
          <p className="eyebrow">Inteligencia aplicada ao futebol</p>
          <h1>E3I Tactical Intelligence</h1>
        </div>
      </div>
      <div className="session-context">
        <div className="session-context-info">
          <UserCog size={16} />
          <span>
            {professionalProfile}
            {ownTeam ? ` · ${ownTeam.name}` : ""}
          </span>
        </div>
        <button className="button button-ghost" type="button" onClick={logout}>
          <LogOut size={15} />
          Trocar
        </button>
      </div>
    </header>
  );
}
