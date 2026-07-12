import { ArrowRight, Save, ShieldCheck, UserCog, Users } from "lucide-react";
import { useState } from "react";

import CategoryBadge from "../components/CategoryBadge.jsx";
import ConfidenceBadge from "../components/ConfidenceBadge.jsx";
import { useTeamSelection } from "../context/TeamSelectionContext.jsx";
import { findExistingTeamByName, registerTeamFromOnlineSearch } from "../api/teamRegistration.js";

const PROFESSIONAL_PROFILES = [
  "Administrador",
  "Scout",
  "Treinador",
  "Analista de desempenho",
  "Coordenador técnico",
  "Gestor esportivo"
];

export default function Login() {
  const { options, ownTeam, setOwnTeam, refreshOptions, setLastSearchedName, professionalProfile, setProfessionalProfile } =
    useTeamSelection();
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
    } catch (err) {
      setMessage(err.message || "Nao foi possivel definir o seu time.");
    }
  }

  const profileReady = Boolean(professionalProfile);
  const teamReady = Boolean(ownTeam);

  return (
    <div className="login-screen">
      <div className="login-card">
        <div className="login-brand">
          <img src="/logo-e3i.png" alt="E3I Solucoes" />
          <div>
            <p className="eyebrow">Inteligencia aplicada ao futebol</p>
            <h1>E3I Tactical Intelligence</h1>
          </div>
        </div>

        <p className="login-intro">
          Antes de acessar a ferramenta, informe quem esta analisando e qual e o seu time. Essas informacoes valem
          para tudo o que for feito na ferramenta a partir de agora.
        </p>

        <article className={`login-step ${profileReady ? "login-step-done" : ""}`}>
          <h3>
            <UserCog size={17} />
            Quem esta usando a ferramenta?
          </h3>
          <label>
            Perfil profissional
            <select value={professionalProfile} onChange={(event) => setProfessionalProfile(event.target.value)}>
              <option value="">Selecione seu perfil</option>
              {PROFESSIONAL_PROFILES.map((profile) => (
                <option key={profile} value={profile}>
                  {profile}
                </option>
              ))}
            </select>
          </label>
        </article>

        <article className={`login-step ${teamReady ? "login-step-done" : ""}`}>
          <h3>
            <ShieldCheck size={17} />
            Qual e o seu time?
          </h3>

          {ownTeam ? (
            <div className="team-hero" style={{ padding: 0, boxShadow: "none", border: "none" }}>
              <div>
                <p className="eyebrow">{ownTeam.league}</p>
                <h2>{ownTeam.name}</h2>
              </div>
              <div className="hero-actions">
                <CategoryBadge category={ownTeam.category} />
                <ConfidenceBadge level={ownTeam.confidence} />
              </div>
            </div>
          ) : (
            <p>Selecione um time existente ou cadastre um abaixo.</p>
          )}

          {options.length > 0 ? (
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
          ) : null}

          <form onSubmit={handleCheck}>
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
                <button
                  className="button button-secondary"
                  type="button"
                  onClick={handleRegister}
                  disabled={registering}
                >
                  <Save size={16} />
                  {registering ? "Cadastrando..." : "Cadastrar e definir como meu time"}
                </button>
              ) : null}
            </div>
            {message ? <span className="inline-message">{message}</span> : null}
          </form>
        </article>

        <div className="login-status">
          {profileReady && teamReady
            ? "Tudo pronto! Entrando na ferramenta..."
            : "Complete as duas etapas acima para entrar na ferramenta."}
          <ArrowRight size={16} />
        </div>
      </div>
    </div>
  );
}
