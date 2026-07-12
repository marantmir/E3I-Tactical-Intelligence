import { ArrowRight, Save, ShieldCheck, Users } from "lucide-react";
import { useState } from "react";
import { Link } from "react-router-dom";

import ConfidenceBadge from "../components/ConfidenceBadge.jsx";
import { useTeamSelection } from "../context/TeamSelectionContext.jsx";
import { findExistingTeamByName, registerTeamFromOnlineSearch } from "../api/teamRegistration.js";

export default function OwnTeam() {
  const { options, ownTeam, setOwnTeam, refreshOptions, setLastSearchedName } = useTeamSelection();
  const [name, setName] = useState("");
  const [checking, setChecking] = useState(false);
  const [registering, setRegistering] = useState(false);
  const [message, setMessage] = useState("");
  const [pendingRegistration, setPendingRegistration] = useState(null);

  async function handleCheck(event) {
    event.preventDefault();
    const cleaned = name.trim();
    if (!cleaned) {
      setMessage("Digite o nome do seu time.");
      return;
    }

    setChecking(true);
    setMessage("");
    setPendingRegistration(null);
    try {
      const result = await findExistingTeamByName(cleaned);
      if (result.found) {
        await setOwnTeam(result.ref);
        setLastSearchedName(result.name);
        setMessage(`${result.name} ja existia na base e foi definido como o seu time.`);
        setName("");
      } else {
        setPendingRegistration(result);
        setMessage(`"${cleaned}" ainda nao esta cadastrado. Cadastre para defini-lo como o seu time.`);
      }
    } catch (err) {
      setMessage(err.message || "Nao foi possivel verificar o time.");
    } finally {
      setChecking(false);
    }
  }

  async function handleRegister() {
    if (!pendingRegistration) return;
    setRegistering(true);
    setMessage("");
    try {
      const { ref, name: registeredName } = await registerTeamFromOnlineSearch(
        pendingRegistration.name,
        pendingRegistration.online
      );
      await refreshOptions();
      await setOwnTeam(ref);
      setLastSearchedName(registeredName);
      setMessage(`${registeredName} foi cadastrado e definido como o seu time.`);
      setPendingRegistration(null);
      setName("");
    } catch (err) {
      setMessage(err.message || "Nao foi possivel cadastrar o time.");
    } finally {
      setRegistering(false);
    }
  }

  async function handleSelectExisting(event) {
    const ref = event.target.value;
    if (!ref) return;
    setMessage("");
    try {
      await setOwnTeam(ref);
      const option = options.find((item) => String(item.ref) === String(ref));
      if (option) setLastSearchedName(option.name);
      setMessage("Seu time ativo foi atualizado.");
    } catch (err) {
      setMessage(err.message || "Nao foi possivel definir o seu time.");
    }
  }

  return (
    <section className="page-grid">
      <div className="section-heading">
        <div>
          <p className="eyebrow">Configuracao</p>
          <h2>Meu time</h2>
        </div>
      </div>

      <div className="notice-strip">
        Defina qual time e o seu. Ele deixa de aparecer como opcao de confronto ao analisar outros times, ja que um
        time nao joga contra si mesmo.
      </div>

      <article className="info-panel">
        <h3>
          <ShieldCheck size={17} />
          Time ativo
        </h3>
        {ownTeam ? (
          <div className="team-hero" style={{ padding: 0, boxShadow: "none", border: "none" }}>
            <div>
              <p className="eyebrow">{ownTeam.league}</p>
              <h2>{ownTeam.name}</h2>
            </div>
            <div className="hero-actions">
              <ConfidenceBadge level={ownTeam.confidence} />
              <Link className="button button-secondary" to={`/team/${ownTeam.ref}`}>
                Ver dossie
                <ArrowRight size={16} />
              </Link>
            </div>
          </div>
        ) : (
          <p>Nenhum time definido ainda. Selecione um time existente ou cadastre um abaixo.</p>
        )}
      </article>

      {options.length > 0 ? (
        <div className="select-panel">
          <label>
            Selecionar entre times ja conhecidos
            <select value={ownTeam?.ref || ""} onChange={handleSelectExisting}>
              <option value="">Escolha um time</option>
              {options.map((option) => (
                <option key={option.ref} value={option.ref}>
                  {option.name}
                </option>
              ))}
            </select>
          </label>
        </div>
      ) : null}

      <form className="analysis-form" onSubmit={handleCheck}>
        <label>
          Ou digite o nome de um novo time
          <input
            value={name}
            onChange={(event) => {
              setName(event.target.value);
              setPendingRegistration(null);
              setMessage("");
            }}
            placeholder="Ex: Botafogo"
          />
        </label>
        <div className="form-actions">
          <button className="button button-primary" type="submit" disabled={checking}>
            <Users size={16} />
            {checking ? "Verificando..." : "Verificar time"}
          </button>
          {pendingRegistration ? (
            <button className="button button-secondary" type="button" onClick={handleRegister} disabled={registering}>
              <Save size={16} />
              {registering ? "Cadastrando..." : "Cadastrar e definir como meu time"}
            </button>
          ) : null}
          {message ? <span className="inline-message">{message}</span> : null}
        </div>
      </form>
    </section>
  );
}
