# Local Hermes docs audit

Conclusion: Hermes docs are installed locally.

## Answers

### 1. Are Hermes docs installed locally?
Yes.

Verified local paths that exist:
- `/home/LENOVO/.hermes/hermes-agent`
- `/home/LENOVO/.hermes/hermes-agent/website/docs`
- `/home/LENOVO/.hermes/hermes-agent/docs`
- `/home/LENOVO/.hermes/hermes-agent/README.md`
- `/home/LENOVO/.hermes/hermes-agent/AGENTS.md`

Evidence checked by reading files:
- `README.md`
- `AGENTS.md`
- `website/docs/index.md`
- `website/docs/getting-started/quickstart.md`
- `website/docs/user-guide/configuration.md`
- `website/docs/user-guide/messaging/index.md`
- `website/docs/reference/cli-commands.md`
- `website/docs/reference/slash-commands.md`
- `website/docs/integrations/providers.md`
- `website/docs/developer-guide/architecture.md`
- `docs/acp-setup.md`

Local docs inventory at audit time:
- Main docs tree: `website/docs` with 113 Markdown/MDX files.
- Supplementary repo docs: `docs` with 5 Markdown files.

### 2. Which local paths are useful for future lookup?
Primary canonical local docs:
- `~/.hermes/hermes-agent/website/docs/index.md`
- `~/.hermes/hermes-agent/website/docs/getting-started/`
- `~/.hermes/hermes-agent/website/docs/user-guide/`
- `~/.hermes/hermes-agent/website/docs/reference/`
- `~/.hermes/hermes-agent/website/docs/integrations/`
- `~/.hermes/hermes-agent/website/docs/developer-guide/`

High-signal single files:
- `~/.hermes/hermes-agent/README.md`
- `~/.hermes/hermes-agent/AGENTS.md`
- `~/.hermes/hermes-agent/website/docs/getting-started/quickstart.md`
- `~/.hermes/hermes-agent/website/docs/user-guide/configuration.md`
- `~/.hermes/hermes-agent/website/docs/user-guide/messaging/index.md`
- `~/.hermes/hermes-agent/website/docs/reference/cli-commands.md`
- `~/.hermes/hermes-agent/website/docs/reference/slash-commands.md`
- `~/.hermes/hermes-agent/website/docs/reference/tools-reference.md`
- `~/.hermes/hermes-agent/website/docs/reference/environment-variables.md`
- `~/.hermes/hermes-agent/website/docs/integrations/providers.md`
- `~/.hermes/hermes-agent/website/docs/developer-guide/architecture.md`

Supplementary, but not primary:
- `~/.hermes/hermes-agent/docs/`
  - useful for ACP setup, migration notes, and internal specs/plans
  - not the main end-user docs tree

### 3. Is scraping/installing any extra local cache necessary right now?
No.

Reason:
- The main Hermes docs site source is already present locally under `~/.hermes/hermes-agent/website/docs`.
- The repo also includes `README.md`, `AGENTS.md`, and a smaller supplementary `docs/` tree.
- Creating a quick local index is enough to make native lookup easier right now.

## Actions completed
- Verified the suspected local docs locations exist.
- Read representative files from the repo root docs, main docs tree, reference pages, integration docs, and developer docs.
- Created a concise local reference index at:
  - `~/.hermes/references/hermes-docs/index.md`

## Notes
- `website/docs` is the best local lookup root for future Hermes documentation queries.
- `docs/` appears supplementary/internal rather than the canonical website docs source.
