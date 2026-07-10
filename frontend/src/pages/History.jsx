import { RotateCcw } from "lucide-react";
import { Link } from "react-router-dom";

import { api } from "../api/client.js";
import ConfidenceBadge from "../components/ConfidenceBadge.jsx";
import ErrorState from "../components/ErrorState.jsx";
import LoadingState from "../components/LoadingState.jsx";
import { useApiResource } from "./useApiResource.js";

export default function History() {
  const { data, loading, error } = useApiResource(() => api.history(), []);

  if (loading) return <LoadingState />;
  if (error) return <ErrorState message={error} />;

  return (
    <section>
      <div className="section-heading">
        <div>
          <p className="eyebrow">Persistência local</p>
          <h2>Histórico de análises</h2>
        </div>
      </div>
      <div className="table-wrap">
        <table>
          <thead>
            <tr>
              <th>Time</th>
              <th>Data</th>
              <th>Objetivo</th>
              <th>Formação</th>
              <th>Confiança</th>
              <th>Status</th>
              <th>Ação</th>
            </tr>
          </thead>
          <tbody>
            {data.map((item) => (
              <tr key={item.id}>
                <td>
                  <strong>{item.team_name}</strong>
                  <span>{item.competition}</span>
                </td>
                <td>{new Date(item.created_at).toLocaleDateString("pt-BR")}</td>
                <td>{item.objective}</td>
                <td>{item.base_formation}</td>
                <td>
                  <ConfidenceBadge level={item.confidence} />
                </td>
                <td>{item.status}</td>
                <td>
                  <Link
                    className="table-action"
                    to={item.team_id ? `/team/${item.team_id}` : `/new-analysis?team=${encodeURIComponent(item.team_name)}`}
                  >
                    <RotateCcw size={15} />
                    Reabrir
                  </Link>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  );
}
