import { Route, Routes } from "react-router-dom";

import Header from "./components/Header.jsx";
import Sidebar from "./components/Sidebar.jsx";
import Dashboard from "./pages/Dashboard.jsx";
import FinalReport from "./pages/FinalReport.jsx";
import Formations from "./pages/Formations.jsx";
import FutureAI from "./pages/FutureAI.jsx";
import GamePlan from "./pages/GamePlan.jsx";
import History from "./pages/History.jsx";
import NewAnalysis from "./pages/NewAnalysis.jsx";
import SourcesVideos from "./pages/SourcesVideos.jsx";
import SquadAnalysis from "./pages/SquadAnalysis.jsx";
import TacticalDossier from "./pages/TacticalDossier.jsx";
import TeamSearch from "./pages/TeamSearch.jsx";

export default function App() {
  return (
    <div className="app-shell">
      <Sidebar />
      <div className="workspace">
        <Header />
        <main className="content">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/new-analysis" element={<NewAnalysis />} />
            <Route path="/search" element={<TeamSearch />} />
            <Route path="/team/:teamId" element={<TacticalDossier />} />
            <Route path="/team/:teamId/formations" element={<Formations />} />
            <Route path="/team/:teamId/squad" element={<SquadAnalysis />} />
            <Route path="/team/:teamId/sources" element={<SourcesVideos />} />
            <Route path="/team/:teamId/game-plan" element={<GamePlan />} />
            <Route path="/team/:teamId/report" element={<FinalReport />} />
            <Route path="/history" element={<History />} />
            <Route path="/future-ai" element={<FutureAI />} />
          </Routes>
        </main>
      </div>
    </div>
  );
}
