import { createContext, useContext, useEffect, useMemo, useState } from "react";
import { useLocation } from "react-router-dom";

import { api } from "../api/client.js";

const TeamSelectionContext = createContext(null);
const STORAGE_KEY = "e3i-selected-team-ref";
const LAST_SEARCHED_NAME_KEY = "e3i-last-searched-name";

export function TeamSelectionProvider({ children }) {
  const location = useLocation();
  const [options, setOptions] = useState([]);
  const [selectedRef, setSelectedRefState] = useState(() => localStorage.getItem(STORAGE_KEY) || "1");
  const [loading, setLoading] = useState(true);
  const [ownTeamRef, setOwnTeamRefState] = useState(null);
  const [lastSearchedName, setLastSearchedNameState] = useState(
    () => localStorage.getItem(LAST_SEARCHED_NAME_KEY) || ""
  );

  useEffect(() => {
    let active = true;
    refreshOptions(active);

    api
      .ownTeam()
      .then((data) => {
        if (active) setOwnTeamRefState(data.ref || null);
      })
      .catch(() => {});

    return () => {
      active = false;
    };
  }, []);

  function refreshOptions(active = true) {
    return api
      .teamOptions()
      .then((payload) => {
        if (!active) return;
        const nextOptions = payload.options || [];
        setOptions(nextOptions);
        if (!localStorage.getItem(STORAGE_KEY) && payload.default_ref) {
          setSelectedRef(payload.default_ref);
        }
      })
      .catch(() => {
        if (active) setOptions([]);
      })
      .finally(() => {
        if (active) setLoading(false);
      });
  }

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

  function setLastSearchedName(name) {
    const normalized = String(name || "");
    localStorage.setItem(LAST_SEARCHED_NAME_KEY, normalized);
    setLastSearchedNameState(normalized);
  }

  async function setOwnTeam(ref) {
    const result = await api.setOwnTeam(ref);
    setOwnTeamRefState(result.ref);
    return result;
  }

  const selectedTeam = useMemo(() => {
    return options.find((option) => String(option.ref) === String(selectedRef)) || options[0] || null;
  }, [options, selectedRef]);

  const ownTeam = useMemo(() => {
    if (!ownTeamRef) return null;
    return options.find((option) => String(option.ref) === String(ownTeamRef)) || null;
  }, [options, ownTeamRef]);

  const value = useMemo(
    () => ({
      loading,
      options,
      selectedRef,
      selectedTeam,
      setSelectedRef,
      ownTeamRef,
      ownTeam,
      setOwnTeam,
      lastSearchedName,
      setLastSearchedName,
      refreshOptions
    }),
    [loading, options, selectedRef, selectedTeam, ownTeamRef, ownTeam, lastSearchedName]
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
