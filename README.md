# DataHub Context Capsule

DataHub Context Capsule turns live DataHub metadata into bounded, deterministic context packs for AI agents. It uses the official open-source DataHub MCP server, refuses mutation tools, hashes the full evidence set, and quarantines instruction-like catalog text before it can enter an agent prompt.

This is an entry for the **MCP Tools & Agents** category of the DataHub Agent Hackathon. It is intentionally distinct from Lineage Sentinel (production risk monitoring) and DAG Forge (metadata-aware Airflow code generation).

## Why it matters

Data catalogs contain useful schema and lineage facts, but their descriptions, tags, field names, and historical queries are untrusted input. Copying that material directly into an AI agent's context creates prompt-injection and context-overflow risks. Context Capsule creates an evidence-addressed boundary between the catalog and the agent.

## DataHub integration

The live mode launches `mcp-server-datahub@latest` over stdio and requires these official read-only tools:

- `search`
- `get_entities`
- `list_schema_fields`
- `get_lineage`
- `get_dataset_queries`

`TOOLS_IS_MUTATION_ENABLED=false` is forced in the child environment. Any unsupported or mutation tool is rejected locally.

## Quick demonstration

Python 3.11 or later is required.

```bash
python -m venv .venv
./.venv/Scripts/activate
pip install -e .
context-capsule --fixture demo/catalog.json --query customer --output output
```

The fixture contains a deliberate prompt injection in a dataset description. The produced Markdown replaces it with a SHA-addressed quarantine marker while retaining useful structural metadata.

Live DataHub MCP usage:

```bash
set DATAHUB_GMS_URL=https://your-datahub.example/api/gms
set DATAHUB_GMS_TOKEN=your-token
context-capsule --query "customer revenue" --output output
```

Credentials are read by the official MCP server and are never written to the capsule.

## Safety properties

- Read-only MCP allow-list and disabled mutation environment flag.
- Five-entity, two-hop, 4 MB evidence, and configurable character bounds.
- Fail-closed behavior for missing valid URNs or malformed queries.
- Prompt-injection quarantine with one-way hashes instead of echoing malicious text.
- Deterministic evidence and context hashes for reproducible agent runs.
- Raw catalog evidence is intentionally excluded from the compact output manifest.

## Tests

```bash
python -m unittest discover -s tests -v
```

The tests cover injection quarantine, determinism, budget truncation, missing search results, mutation refusal, and output minimization.

## License

Apache-2.0.
