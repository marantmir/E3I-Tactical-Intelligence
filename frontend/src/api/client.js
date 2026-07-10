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
  teamOptions: () => request("/api/teams/options"),
  teamWorkspace: (teamRef) => request(`/api/teams/workspace/${encodeURIComponent(teamRef)}`),
  searchTeams: (query) => request(`/api/teams/search?query=${encodeURIComponent(query)}`),
  onlineTeamSearch: (name) => request(`/api/teams/online-search?name=${encodeURIComponent(name)}`),
  onlineProfiles: (query = "") => request(`/api/teams/online-profiles?query=${encodeURIComponent(query)}`),
  saveOnlineProfile: (payload) =>
    request("/api/teams/online-profiles", {
      method: "POST",
      body: JSON.stringify(payload)
    }),
  team: (teamId) => request(`/api/teams/${teamId}`),
  tacticalAnalysis: (teamId) => request(`/api/teams/${teamId}/tactical-analysis`),
  formations: (teamId) => request(`/api/teams/${teamId}/formations`),
  players: (teamId) => request(`/api/teams/${teamId}/players`),
  sources: (teamId) => request(`/api/teams/${teamId}/sources`),
  graphAnalysis: (teamId) => request(`/api/teams/${teamId}/graph-analysis`),
  uploadVideoVision: async (teamRef, file, options = {}) => {
    const formData = new FormData();
    formData.append("file", file);
    (options.jerseyFiles || []).forEach((jerseyFile) => {
      formData.append("jersey_refs", jerseyFile);
    });
    const params = new URLSearchParams();
    if (options.maxFrames) params.set("max_frames", options.maxFrames);
    if (options.sampleEvery) params.set("sample_every", options.sampleEvery);
    if (options.teamFilter) params.set("team_filter", options.teamFilter);
    if (!/^\d+$/.test(String(teamRef)) && options.teamName) {
      params.set("team_name", options.teamName);
    }
    const query = params.toString() ? `?${params.toString()}` : "";
    const uploadPath = /^\d+$/.test(String(teamRef))
      ? `/api/teams/${teamRef}/video-vision/upload${query}`
      : `/api/teams/video-vision/upload${query}`;
    const response = await fetch(`${API_BASE}${uploadPath}`, {
      method: "POST",
      body: formData
    });
    if (!response.ok) {
      const contentType = response.headers.get("Content-Type") || "";
      const message = contentType.includes("application/json")
        ? formatApiError(await response.json())
        : await response.text();
      throw new Error(message || "Falha ao processar o video");
    }
    return response.json();
  },
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
  llmConfig: () => request("/api/llm/config"),
  saveLlmConfig: (payload) =>
    request("/api/llm/config", {
      method: "PUT",
      body: JSON.stringify(payload)
    }),
  testLlmConfig: () =>
    request("/api/llm/test", {
      method: "POST",
      body: JSON.stringify({})
    }),
  generateReport: (payload) =>
    request("/api/reports", {
      method: "POST",
      body: JSON.stringify(payload)
    })
};
