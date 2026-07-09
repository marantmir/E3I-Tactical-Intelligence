import { ShieldCheck } from "lucide-react";

export default function Header() {
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
        <span>Busca publica, grafos e leitura visual integrados</span>
      </div>
    </header>
  );
}
