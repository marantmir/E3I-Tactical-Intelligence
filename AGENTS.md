# Repository guidance

- Run all validation commands from the repository root.
- Keep backend tests hermetic: do not require credentials, paid APIs, or network access.
- Use `make validate` as the complete local quality gate before committing.
- Update `docs/evaluation-evidence.md` with results produced in the current run; never copy historical results as if they were current.
- Keep credentials in environment variables; never commit `.env` or private runtime configuration.
- Route new outbound HTTP integrations through the public-network guard and add hermetic DNS/redirect tests.
- Register new LLM tools explicitly with closed schemas, bounded input/output, timeout, sanitized errors, and metadata-only logs.
