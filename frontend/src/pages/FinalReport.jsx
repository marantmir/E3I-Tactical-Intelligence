import { Download, FileText, Save } from "lucide-react";
import { useState } from "react";
import { useParams } from "react-router-dom";

import { api } from "../api/client.js";
import ErrorState from "../components/ErrorState.jsx";
import LoadingState from "../components/LoadingState.jsx";
import ReportPreview from "../components/ReportPreview.jsx";
import { useApiResource } from "./useApiResource.js";

export default function FinalReport() {
  const { teamId } = useParams();
  const [report, setReport] = useState(null);
  const [message, setMessage] = useState("");
  const [loadingReport, setLoadingReport] = useState(false);
  const { data: team, loading, error } = useApiResource(() => api.team(teamId), [teamId]);

  if (loading) return <LoadingState />;
  if (error) return <ErrorState message={error} />;

  async function generateReport() {
    setLoadingReport(true);
    setMessage("");
    try {
      const generated = await api.generateReport({
        team_id: Number(teamId),
        objective: "Relatorio para comissao tecnica",
        user_profile: "Analista de desempenho"
      });
      setReport(generated);
    } catch (err) {
      setMessage(err.message || "Nao foi possivel gerar o relatorio.");
    } finally {
      setLoadingReport(false);
    }
  }

  async function saveAnalysis() {
    try {
      await api.createAnalysis({
        team_id: Number(teamId),
        team_name: team.name,
        competition: team.league,
        season: "2026",
        objective: "Relatorio para comissao tecnica",
        user_profile: "Analista de desempenho"
      });
      setMessage("Analise salva no historico.");
    } catch (err) {
      setMessage(err.message || "Nao foi possivel salvar.");
    }
  }

  function exportPdf() {
    setMessage("Exportacao PDF preparada como etapa de entrega do relatorio.");
  }

  return (
    <section className="page-grid">
      <div className="section-heading">
        <div>
          <p className="eyebrow">{team.name}</p>
          <h2>Relatorio final</h2>
        </div>
        <div className="action-row">
          <button className="button button-primary" type="button" onClick={generateReport}>
            <FileText size={16} />
            {loadingReport ? "Gerando..." : "Gerar relatorio"}
          </button>
          <button className="button button-secondary" type="button" onClick={saveAnalysis}>
            <Save size={16} />
            Salvar analise
          </button>
          <button className="button button-ghost" type="button" onClick={exportPdf}>
            <Download size={16} />
            Exportar PDF
          </button>
        </div>
      </div>
      {message ? <div className="notice-strip">{message}</div> : null}
      <ReportPreview report={report} />
    </section>
  );
}
