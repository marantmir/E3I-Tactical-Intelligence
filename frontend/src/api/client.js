const API_BASE = import.meta.env.VITE_API_BASE_URL || "";

async function request(path, options = {}) {
  const response = await fetch(`${API_BASE}${path}`, {
    headers: {
      "Content-Type": "application/json",
      ...(options.headers || {})
    },
    ...options
  });

  if (!response.ok) {
    const message = await response.text();
    throw new Error(message || "Falha na requisicao");
  }

  return response.json();
}

export const api = {
  health: () => request("/api/health"),
  teams: () => request("/api/teams"),
  searchTeams: (query) => request(`/api/teams/search?query=${encodeURIComponent(query)}`),
  team: (teamId) => request(`/api/teams/${teamId}`),
  tacticalAnalysis: (teamId) => request(`/api/teams/${teamId}/tactical-analysis`),
  formations: (teamId) => request(`/api/teams/${teamId}/formations`),
  players: (teamId) => request(`/api/teams/${teamId}/players`),
  sources: (teamId) => request(`/api/teams/${teamId}/sources`),
  gamePlan: (teamId) => request(`/api/teams/${teamId}/game-plan`),
  createAnalysis: (payload) =>
    request("/api/analysis", {
      method: "POST",
      body: JSON.stringify(payload)
    }),
  history: () => request("/api/history"),
  generateReport: (payload) =>
    request("/api/reports", {
      method: "POST",
      body: JSON.stringify(payload)
    })
};
