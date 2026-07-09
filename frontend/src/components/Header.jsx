import { AlertTriangle } from "lucide-react";

export default function Header() {
  return (
    <header className="topbar">
      <div>
        <p className="eyebrow">Protótipo acadêmico</p>
        <h1>E3I Tactical Intelligence</h1>
      </div>
      <div className="simulation-banner">
        <AlertTriangle size={18} />
        <span>Sem integração real com IA nesta versão</span>
      </div>
    </header>
  );
}
