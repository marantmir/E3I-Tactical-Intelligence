import { useState } from "react";

const API_URL = import.meta.env.VITE_API_URL ?? "http://127.0.0.1:8000";

function Section({ title, children }) {
  return (
    <section className="panel">
      <h2>{title}</h2>
      {children}
    </section>
  );
}

function AnalysisCard({ analysis }) {
  if (!analysis) {
    return (
      <div className="empty-state">
        <strong>Ready for kickoff.</strong>
        <span>Choose a club to generate a simulated tactical dossier.</span>
      </div>
    );
  }

  return (
    <div className="analysis-grid">
      <Section title="Formation">
        <p className="formation">{analysis.formation}</p>
      </Section>

      <Section title="Strengths">
        <ul>
          {analysis.strengths.map((item) => (
            <li key={item}>{item}</li>
          ))}
        </ul>
      </Section>

      <Section title="Weaknesses">
        <ul>
          {analysis.weaknesses.map((item) => (
            <li key={item}>{item}</li>
          ))}
        </ul>
      </Section>

      <Section title="Key Players">
        <div className="tags">
          {analysis.key_players.map((player) => (
            <span key={player}>{player}</span>
          ))}
        </div>
      </Section>

      <Section title="Recent Matches">
        <ul>
          {analysis.recent_matches.map((match) => (
            <li key={match}>{match}</li>
          ))}
        </ul>
      </Section>

      <Section title="Game Plan">
        <p>{analysis.game_plan}</p>
      </Section>

      <Section title="Simulation Note">
        <p>{analysis.simulation_note}</p>
      </Section>
    </div>
  );
}

export default function App() {
  const [clubName, setClubName] = useState("Palmeiras");
  const [analysis, setAnalysis] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState("");

  async function handleSubmit(event) {
    event.preventDefault();
    setIsLoading(true);
    setError("");

    try {
      const response = await fetch(`${API_URL}/api/analyses`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ club_name: clubName }),
      });

      if (!response.ok) {
        throw new Error("Could not generate tactical analysis.");
      }

      setAnalysis(await response.json());
    } catch (err) {
      setError(err.message);
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <main className="app-shell">
      <section className="hero">
        <div>
          <p className="eyebrow">Football tactical intelligence</p>
          <h1>E3I Tactical Intelligence</h1>
          <p className="lede">
            Prototype dashboard for simulated opponent analysis, match planning,
            and tactical scouting.
          </p>
        </div>

        <form className="search-panel" onSubmit={handleSubmit}>
          <label htmlFor="clubName">Club</label>
          <div className="input-row">
            <input
              id="clubName"
              value={clubName}
              onChange={(event) => setClubName(event.target.value)}
              placeholder="Ex: Palmeiras"
            />
            <button disabled={isLoading || clubName.trim().length < 2}>
              {isLoading ? "Analyzing..." : "Analyze"}
            </button>
          </div>
          {error && <p className="error">{error}</p>}
        </form>
      </section>

      <AnalysisCard analysis={analysis} />
    </main>
  );
}
