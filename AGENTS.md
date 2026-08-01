# Repository guidance

- Run all validation commands from the repository root.
- Keep backend tests hermetic: do not require credentials, paid APIs, or network access.
- Use `make validate` as the complete local quality gate before committing.
- Update `docs/evaluation-evidence.md` with results produced in the current run; never copy historical results as if they were current.
