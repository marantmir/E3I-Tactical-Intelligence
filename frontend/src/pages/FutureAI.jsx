import { Activity, BrainCircuit, CheckCircle2, KeyRound, Save, SlidersHorizontal } from "lucide-react";
import { useEffect, useState } from "react";

import { api } from "../api/client.js";

const rows = [
  ["Busca de dados", "Ativo", "Consulta publica, base local e revisao de fonte"],
  ["Videos", "Ativo", "Mapa de calor, trilhas, eventos e recomendacoes por lance"],
  ["Dossie tatico", "Ativo", "Resumo por objetivo com evidencias e nivel de confianca"],
  ["Grafos taticos", "Ativo", "Conexoes entre jogadores, zonas, centralidade e densidade"],
  ["Visao computacional", "Ativo", "Leitura visual de ocupacao, pressao, profundidade e corredores"],
  ["LLM", "Parametrizavel", "Busca, pre-analise, leitura visual, identidade e explicacao tatica"],
  ["Pesquisa operacional", "Ativo", "Comparacao de formacoes, riscos, cenarios e plano de jogo"]
];

const initialForm = {
  enabled: false,
  provider: "openai_responses",
  model: "gpt-4.1-mini",
  timeout_seconds: 18,
  temperature: 0.2,
  max_output_tokens: 1400,
  language: "pt-BR",
  analysis_depth: "profunda",
  search_scope: "tactical_visual_only",
  identity_mode: "strict_visual_evidence",
  api_key: "",
  clear_api_key: false
};

export default function FutureAI() {
  const [form, setForm] = useState(initialForm);
  const [options, setOptions] = useState({});
  const [status, setStatus] = useState(null);
  const [keyMask, setKeyMask] = useState("");
  const [hasKey, setHasKey] = useState(false);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [testing, setTesting] = useState(false);
  const [message, setMessage] = useState("");
  const [testResult, setTestResult] = useState(null);

  useEffect(() => {
    loadConfig();
  }, []);

  async function loadConfig() {
    setLoading(true);
    setMessage("");
    try {
      const result = await api.llmConfig();
      applyConfigResponse(result);
    } catch (err) {
      setMessage(err.message || "Nao foi possivel carregar a configuracao da LLM.");
    } finally {
      setLoading(false);
    }
  }

  function applyConfigResponse(result) {
    const config = result.config || {};
    setForm((current) => ({
      ...current,
      ...config,
      api_key: "",
      clear_api_key: false
    }));
    setOptions(result.options || {});
    setStatus(result.status || null);
    setHasKey(Boolean(config.has_api_key));
    setKeyMask(config.api_key_mask || "");
  }

  function updateField(event) {
    const { checked, name, type, value } = event.target;
    setForm((current) => {
      const next = { ...current, [name]: type === "checkbox" ? checked : value };
      if (name === "provider") {
        // Cada provedor tem seus proprios modelos; ao trocar, sugere o
        // primeiro modelo conhecido do novo provedor em vez de manter o
        // modelo do provedor anterior (ex.: "gpt-4.1-mini" ao trocar para
        // Anthropic/Gemini).
        const suggestions = options.models_by_provider?.[value] || [];
        if (suggestions.length && !suggestions.some((item) => item.value === current.model)) {
          next.model = suggestions[0].value;
        }
      }
      return next;
    });
    setMessage("");
    setTestResult(null);
  }

  async function saveConfig(event) {
    event.preventDefault();
    setSaving(true);
    setMessage("");
    try {
      const payload = {
        ...form,
        timeout_seconds: Number(form.timeout_seconds),
        temperature: Number(form.temperature),
        max_output_tokens: Number(form.max_output_tokens)
      };
      if (!payload.api_key) delete payload.api_key;
      const result = await api.saveLlmConfig(payload);
      applyConfigResponse(result);
      setMessage("Configuracao da LLM salva. As proximas buscas e analises ja usam estes parametros.");
    } catch (err) {
      setMessage(err.message || "Nao foi possivel salvar a configuracao da LLM.");
    } finally {
      setSaving(false);
    }
  }

  async function testConfig() {
    setTesting(true);
    setMessage("");
    setTestResult(null);
    try {
      const result = await api.testLlmConfig();
      setStatus(result.status || null);
      setTestResult(result);
      setMessage(
        result.ok
          ? "Teste concluido com LLM ativa."
          : "Teste concluido em fallback local. Verifique chave, modelo e rede."
      );
    } catch (err) {
      setMessage(err.message || "Nao foi possivel testar a LLM.");
    } finally {
      setTesting(false);
    }
  }

  const selectedProvider = (options.providers || []).find((item) => item.value === form.provider);
  const modelOptions = options.models_by_provider?.[form.provider] || [];

  return (
    <section className="page-grid">
      <div className="section-heading">
        <div>
          <p className="eyebrow">Inteligencia avancada</p>
          <h2>Parametrizacao da LLM</h2>
        </div>
        <span className={status?.enabled ? "badge badge-high" : "badge badge-medium"}>
          {status?.enabled ? "LLM ativa" : "Fallback local"}
        </span>
      </div>

      <div className="notice-strip">
        Configure a LLM para enriquecer busca, pre-analise, leitura visual do video, identidade de jogadores e
        explicacoes taticas. Sem chave valida, o fluxo continua no modo local.
      </div>

      <form className="analysis-form llm-config-form" onSubmit={saveConfig}>
        <label className="toggle-row">
          <span>
            <BrainCircuit size={17} />
            Usar LLM nas analises
          </span>
          <input name="enabled" type="checkbox" checked={Boolean(form.enabled)} onChange={updateField} />
        </label>

        <label>
          Provedor
          <select name="provider" value={form.provider} onChange={updateField}>
            {(options.providers || [{ value: "openai_responses", label: "OpenAI (Responses API)" }]).map((item) => (
              <option key={item.value} value={item.value}>
                {item.label}
              </option>
            ))}
          </select>
          <small>Troque livremente entre provedores; cada um usa sua propria chave de API.</small>
        </label>

        <label>
          Modelo
          <input
            list="llm-model-options"
            name="model"
            value={form.model}
            onChange={updateField}
            placeholder={modelOptions[0]?.value || "modelo do provedor"}
          />
          <datalist id="llm-model-options">
            {modelOptions.map((item) => (
              <option key={item.value} value={item.value}>
                {item.label}
              </option>
            ))}
          </datalist>
        </label>

        <label>
          API key ({selectedProvider?.label || "provedor selecionado"})
          <input
            name="api_key"
            type="password"
            value={form.api_key}
            onChange={updateField}
            placeholder={
              hasKey
                ? `Chave salva: ${keyMask}`
                : `Cole a chave ou defina ${selectedProvider?.env_api_key || "a variavel de ambiente"} no servidor`
            }
          />
        </label>

        <label>
          Timeout (segundos)
          <input
            max="90"
            min="3"
            name="timeout_seconds"
            type="number"
            value={form.timeout_seconds}
            onChange={updateField}
          />
        </label>

        <label>
          Temperatura
          <input
            max="1"
            min="0"
            name="temperature"
            step="0.05"
            type="number"
            value={form.temperature}
            onChange={updateField}
          />
        </label>

        <label>
          Maximo de tokens
          <input
            max="6000"
            min="200"
            name="max_output_tokens"
            step="100"
            type="number"
            value={form.max_output_tokens}
            onChange={updateField}
          />
        </label>

        <label>
          Idioma
          <select name="language" value={form.language} onChange={updateField}>
            {(options.languages || []).map((item) => (
              <option key={item.value} value={item.value}>
                {item.label}
              </option>
            ))}
          </select>
        </label>

        <label>
          Profundidade da analise
          <select name="analysis_depth" value={form.analysis_depth} onChange={updateField}>
            {(options.analysis_depth || []).map((item) => (
              <option key={item.value} value={item.value}>
                {item.label}
              </option>
            ))}
          </select>
        </label>

        <label>
          Escopo de busca
          <select name="search_scope" value={form.search_scope} onChange={updateField}>
            {(options.search_scope || []).map((item) => (
              <option key={item.value} value={item.value}>
                {item.label}
              </option>
            ))}
          </select>
        </label>

        <label>
          Identificacao de jogador
          <select name="identity_mode" value={form.identity_mode} onChange={updateField}>
            {(options.identity_mode || []).map((item) => (
              <option key={item.value} value={item.value}>
                {item.label}
              </option>
            ))}
          </select>
        </label>

        <label className="toggle-row">
          <span>
            <KeyRound size={17} />
            Remover chave salva
          </span>
          <input name="clear_api_key" type="checkbox" checked={Boolean(form.clear_api_key)} onChange={updateField} />
        </label>

        <div className="form-actions">
          <button className="button button-primary" type="submit" disabled={saving || loading}>
            <Save size={16} />
            {saving ? "Salvando..." : "Salvar parametros"}
          </button>
          <button className="button button-secondary" type="button" onClick={testConfig} disabled={testing || loading}>
            <Activity size={16} />
            {testing ? "Testando..." : "Testar LLM"}
          </button>
          {message ? <span className="inline-message">{message}</span> : null}
        </div>
      </form>

      <section className="three-column">
        <article>
          <CheckCircle2 size={18} />
          <h3>Status</h3>
          <p>{status?.enabled ? "As chamadas da LLM estao ativas." : "A aplicacao esta usando fallback local."}</p>
          <strong>{status?.provider || "local_fallback"}</strong>
        </article>
        <article>
          <SlidersHorizontal size={18} />
          <h3>Modelo ativo</h3>
          <p>{status?.model || form.model}</p>
          <strong>{hasKey ? `Chave: ${keyMask}` : "Sem chave configurada"}</strong>
        </article>
        <article>
          <BrainCircuit size={18} />
          <h3>Ultimo teste</h3>
          <p>{testResult?.sample?.summary || "Use o teste para validar chave, modelo e resposta JSON."}</p>
          <strong>{testResult ? (testResult.ok ? "LLM respondeu" : "Fallback local validado") : "Aguardando teste"}</strong>
        </article>
      </section>

      <div className="table-wrap">
        <table>
          <thead>
            <tr>
              <th>Area</th>
              <th>Status</th>
              <th>Aplicacao</th>
            </tr>
          </thead>
          <tbody>
            {rows.map(([area, rowStatus, application]) => (
              <tr key={area}>
                <td>
                  <strong>{area}</strong>
                </td>
                <td>{rowStatus}</td>
                <td>{application}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  );
}
