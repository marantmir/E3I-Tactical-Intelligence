import { ShieldCheck } from "lucide-react";
import { useLocation, useNavigate } from "react-router-dom";

import { useTeamSelection } from "../context/TeamSelectionContext.jsx";

export default function Header() {
  const navigate = useNavigate();
  const location = useLocation();
  const { loading, options, selectedRef, setSelectedRef } = useTeamSelection();

  function changeTeam(event) {
    const nextRef = event.target.value;
    setSelectedRef(nextRef);
    const match = location.pathname.match(/^\/team\/[^/]+(\/.*)?$/);
    navigate(match ? `/team/${nextRef}${match[1] || ""}` : `/team/${nextRef}/sources`);
  }

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
      <div className="simulation-banner">
        <ShieldCheck size={18} />
        <label className="team-context-select">
          <span>Time ativo</span>
          <select value={selectedRef} onChange={changeTeam} disabled={loading || options.length === 0}>
            {options.map((option) => (
              <option key={option.ref} value={option.ref}>
                {option.name} - {option.kind === "local" ? "base local" : "fonte salva"}
              </option>
            ))}
          </select>
        </label>
      </div>
    </header>
  );
}
