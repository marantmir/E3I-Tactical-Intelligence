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
    const contentType = response.headers.get("Content-Type") || "";
    const message = contentType.includes("application/json")
      ? formatApiError(await response.json())
      : await response.text();
    throw new Error(message || "Falha na requisicao");
  }

  return response.json();
}

function formatApiError(payload) {
  if (typeof payload?.detail === "string") {
    return payload.detail;
  }

  if (Array.isArray(payload?.detail)) {
    return payload.detail
      .map((item) => item?.msg || item?.message || JSON.stringify(item))
      .join(" ");
  }

  return payload?.message || "Falha na requisicao";
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
  graphAnalysis: (teamId) => request(`/api/teams/${teamId}/graph-analysis`),
  videoVision: (teamId) => request(`/api/teams/${teamId}/video-vision`),
  publicIntelligence: (teamId) => request(`/api/teams/${teamId}/public-intelligence`),
  gamePlan: (teamId) => request(`/api/teams/${teamId}/game-plan`),
  previewAnalysis: (payload) =>
    request("/api/analysis/preview", {
      method: "POST",
      body: JSON.stringify(payload)
    }),
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
