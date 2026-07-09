import { Save } from "lucide-react";
import { useEffect, useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";

import { api } from "../api/client.js";

const objectives = [
  "Análise de adversário",
  "Scouting de jogadores",
  "Preparação de jogo",
  "Avaliação de elenco",
  "Relatório para comissão técnica"
];

const profiles = [
  "Scout",
  "Treinador",
  "Analista de desempenho",
  "Coordenador técnico",
  "Gestor esportivo"
];

export default function NewAnalysis() {
  const navigate = useNavigate();
  const [teams, setTeams] = useState([]);
  const [message, setMessage] = useState("");
  const [saving, setSaving] = useState(false);
  const [form, setForm] = useState({
    team_name: "Flamengo",
    competition: "Brasileirão Série A",
    season: "2026",
    objective: objectives[0],
    user_profile: profiles[2]
  });

  useEffect(() => {
    api.teams().then(setTeams).catch(() => setTeams([]));
  }, []);

  const selectedTeam = useMemo(() => {
    return teams.find((team) => team.name.toLowerCase() === form.team_name.toLowerCase());
  }, [teams, form.team_name]);

  function updateField(event) {
    const { name, value } = event.target;
    setForm((current) => ({ ...current, [name]: value }));
  }

  async function submit(event) {
    event.preventDefault();
    setSaving(true);
    setMessage("");
    try {
      const record = await api.createAnalysis({
        ...form,
        team_id: selectedTeam?.id
      });
      setMessage(`Análise salva para ${record.team_name}.`);
      navigate(`/team/${record.team_id}`);
    } catch (err) {
      setMessage(err.message || "Não foi possível salvar a análise.");
    } finally {
      setSaving(false);
    }
  }

  return (
    <section className="form-page">
      <div className="section-heading">
        <div>
          <p className="eyebrow">Fluxo de análise</p>
          <h2>Nova análise</h2>
        </div>
      </div>
      <form className="analysis-form" onSubmit={submit}>
        <label>
          Nome do time
          <input list="team-options" name="team_name" value={form.team_name} onChange={updateField} />
          <datalist id="team-options">
            {teams.map((team) => (
              <option key={team.id} value={team.name} />
            ))}
          </datalist>
        </label>
        <label>
          Competição
          <input name="competition" value={form.competition} onChange={updateField} />
        </label>
        <label>
          Temporada
          <input name="season" value={form.season} onChange={updateField} />
        </label>
        <label>
          Objetivo da análise
          <select name="objective" value={form.objective} onChange={updateField}>
            {objectives.map((objective) => (
              <option key={objective}>{objective}</option>
            ))}
          </select>
        </label>
        <label>
          Perfil do usuário
          <select name="user_profile" value={form.user_profile} onChange={updateField}>
            {profiles.map((profile) => (
              <option key={profile}>{profile}</option>
            ))}
          </select>
        </label>
        <div className="form-actions">
          <button className="button button-primary" type="submit" disabled={saving}>
            <Save size={16} />
            {saving ? "Salvando..." : "Salvar análise"}
          </button>
          {message ? <span className="inline-message">{message}</span> : null}
        </div>
      </form>
    </section>
  );
}
