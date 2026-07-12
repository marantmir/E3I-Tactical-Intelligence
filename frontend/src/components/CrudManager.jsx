import { useEffect, useMemo, useState } from "react";
import { Pencil, Plus, RefreshCw, Save, Trash2, X } from "lucide-react";

/**
 * Gerenciador CRUD reutilizavel, dirigido por configuracao.
 *
 * Props:
 * - title, description
 * - columns: [{ key, label, render? }]
 * - fields: [{ name, label, type: text|textarea|number|select|tags, options?, required?, help? }]
 * - api: { list(), create(payload), update(id, payload), remove(id) }
 * - emptyLabel
 */
export default function CrudManager({ title, description, columns, fields, api, emptyLabel }) {
  const [records, setRecords] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [editing, setEditing] = useState(null); // null | "new" | record
  const [saving, setSaving] = useState(false);

  const blankForm = useMemo(() => {
    const base = {};
    fields.forEach((field) => {
      base[field.name] = field.type === "tags" ? [] : "";
    });
    return base;
  }, [fields]);

  const [form, setForm] = useState(blankForm);

  async function load() {
    setLoading(true);
    setError("");
    try {
      setRecords(await api.list());
    } catch (err) {
      setError(err.message || "Falha ao carregar os registros.");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    load();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [api]);

  function startCreate() {
    setForm(blankForm);
    setEditing("new");
    setError("");
  }

  function startEdit(record) {
    const next = {};
    fields.forEach((field) => {
      const value = record[field.name];
      next[field.name] = field.type === "tags" ? value || [] : value ?? "";
    });
    setForm(next);
    setEditing(record);
    setError("");
  }

  function cancel() {
    setEditing(null);
    setForm(blankForm);
    setError("");
  }

  function updateField(name, value) {
    setForm((current) => ({ ...current, [name]: value }));
  }

  async function submit(event) {
    event.preventDefault();
    setSaving(true);
    setError("");
    try {
      const payload = {};
      fields.forEach((field) => {
        payload[field.name] = form[field.name];
      });
      if (editing === "new") {
        await api.create(payload);
      } else {
        await api.update(editing.id, payload);
      }
      await load();
      cancel();
    } catch (err) {
      setError(err.message || "Falha ao salvar o registro.");
    } finally {
      setSaving(false);
    }
  }

  async function remove(record) {
    const label = record.name || record.title || record.formation || `#${record.id}`;
    if (!window.confirm(`Excluir "${label}"? Esta acao nao pode ser desfeita.`)) return;
    setError("");
    try {
      await api.remove(record.id);
      await load();
    } catch (err) {
      setError(err.message || "Falha ao excluir o registro.");
    }
  }

  return (
    <section className="crud-manager">
      <div className="section-heading">
        <div>
          <p className="eyebrow">Manutencao</p>
          <h3>{title}</h3>
          {description ? <p>{description}</p> : null}
        </div>
        <div className="action-row">
          <button className="button button-secondary" type="button" onClick={load} disabled={loading}>
            <RefreshCw size={16} />
            Atualizar
          </button>
          <button className="button button-primary" type="button" onClick={startCreate}>
            <Plus size={16} />
            Novo
          </button>
        </div>
      </div>

      {error ? <p className="error-text">{error}</p> : null}

      {editing ? (
        <form className="crud-form" onSubmit={submit}>
          <div className="crud-form-grid">
            {fields.map((field) => (
              <CrudField key={field.name} field={field} value={form[field.name]} onChange={updateField} />
            ))}
          </div>
          <div className="form-actions">
            <button className="button button-primary" type="submit" disabled={saving}>
              <Save size={16} />
              {saving ? "Salvando..." : editing === "new" ? "Criar" : "Salvar alteracoes"}
            </button>
            <button className="button button-secondary" type="button" onClick={cancel} disabled={saving}>
              <X size={16} />
              Cancelar
            </button>
          </div>
        </form>
      ) : null}

      {loading ? (
        <p>Carregando...</p>
      ) : records.length === 0 ? (
        <div className="empty-state">
          <h2>{emptyLabel || "Nenhum registro"}</h2>
          <p>Use o botao "Novo" para inserir o primeiro registro.</p>
        </div>
      ) : (
        <div className="table-wrap">
          <table>
            <thead>
              <tr>
                {columns.map((column) => (
                  <th key={column.key}>{column.label}</th>
                ))}
                <th aria-label="Acoes" />
              </tr>
            </thead>
            <tbody>
              {records.map((record) => (
                <tr key={record.id}>
                  {columns.map((column) => (
                    <td key={column.key}>{column.render ? column.render(record) : record[column.key]}</td>
                  ))}
                  <td>
                    <div className="row-actions">
                      <button className="icon-action" type="button" onClick={() => startEdit(record)} aria-label="Editar">
                        <Pencil size={16} />
                      </button>
                      <button
                        className="icon-action icon-action-danger"
                        type="button"
                        onClick={() => remove(record)}
                        aria-label="Excluir"
                      >
                        <Trash2 size={16} />
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </section>
  );
}

function CrudField({ field, value, onChange }) {
  const { name, label, type = "text", options = [], required, help } = field;

  if (type === "select") {
    return (
      <label className="crud-label">
        <span>
          {label}
          {required ? " *" : ""}
        </span>
        <select value={value ?? ""} onChange={(event) => onChange(name, event.target.value)}>
          <option value="">Selecione...</option>
          {options.map((option) => {
            const optionValue = typeof option === "object" ? option.value : option;
            const optionLabel = typeof option === "object" ? option.label : option;
            return (
              <option key={optionValue} value={optionValue}>
                {optionLabel}
              </option>
            );
          })}
        </select>
        {help ? <small>{help}</small> : null}
      </label>
    );
  }

  if (type === "textarea") {
    return (
      <label className="crud-label crud-label-wide">
        <span>
          {label}
          {required ? " *" : ""}
        </span>
        <textarea rows={3} value={value ?? ""} onChange={(event) => onChange(name, event.target.value)} />
        {help ? <small>{help}</small> : null}
      </label>
    );
  }

  if (type === "tags") {
    const selected = Array.isArray(value) ? value : [];
    return (
      <div className="crud-label crud-label-wide">
        <span>
          {label}
          {required ? " *" : ""}
        </span>
        <div className="tag-options">
          {options.map((option) => {
            const optionValue = typeof option === "object" ? option.value : option;
            const optionLabel = typeof option === "object" ? option.label : option;
            const checked = selected.includes(optionValue);
            return (
              <label key={optionValue} className={`tag-option ${checked ? "tag-option-on" : ""}`}>
                <input
                  type="checkbox"
                  checked={checked}
                  onChange={() =>
                    onChange(
                      name,
                      checked ? selected.filter((item) => item !== optionValue) : [...selected, optionValue]
                    )
                  }
                />
                {optionLabel}
              </label>
            );
          })}
        </div>
        {help ? <small>{help}</small> : null}
      </div>
    );
  }

  return (
    <label className="crud-label">
      <span>
        {label}
        {required ? " *" : ""}
      </span>
      <input
        type={type === "number" ? "number" : "text"}
        step={type === "number" ? "any" : undefined}
        value={value ?? ""}
        onChange={(event) => onChange(name, event.target.value)}
      />
      {help ? <small>{help}</small> : null}
    </label>
  );
}
