import { createContext, useContext, useEffect, useMemo, useState } from "react";
import { useLocation } from "react-router-dom";

import { api } from "../api/client.js";

const TeamSelectionContext = createContext(null);
const STORAGE_KEY = "e3i-selected-team-ref";

export function TeamSelectionProvider({ children }) {
  const location = useLocation();
  const [options, setOptions] = useState([]);
  const [selectedRef, setSelectedRefState] = useState(() => localStorage.getItem(STORAGE_KEY) || "1");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let active = true;
    api
      .teamOptions()
      .then((payload) => {
        if (!active) return;
        const nextOptions = payload.options || [];
        setOptions(nextOptions);
        if (!localStorage.getItem(STORAGE_KEY) && payload.default_ref) {
          setSelectedRef(payload.default_ref);
        }
      })
      .catch(() => setOptions([]))
      .finally(() => {
        if (active) setLoading(false);
      });
    return () => {
      active = false;
    };
  }, []);

  useEffect(() => {
    const match = location.pathname.match(/^\/team\/([^/]+)/);
    if (match?.[1]) {
      setSelectedRef(decodeURIComponent(match[1]));
    }
  }, [location.pathname]);

  function setSelectedRef(ref) {
    const normalized = String(ref || "1");
    localStorage.setItem(STORAGE_KEY, normalized);
    setSelectedRefState(normalized);
  }

  const selectedTeam = useMemo(() => {
    return options.find((option) => String(option.ref) === String(selectedRef)) || options[0] || null;
  }, [options, selectedRef]);

  const value = useMemo(
    () => ({
      loading,
      options,
      selectedRef,
      selectedTeam,
      setSelectedRef
    }),
    [loading, options, selectedRef, selectedTeam]
  );

  return <TeamSelectionContext.Provider value={value}>{children}</TeamSelectionContext.Provider>;
}

export function useTeamSelection() {
  const context = useContext(TeamSelectionContext);
  if (!context) {
    throw new Error("useTeamSelection deve ser usado dentro de TeamSelectionProvider.");
  }
  return context;
}
