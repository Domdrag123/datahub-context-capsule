# Devpost submission sheet

## Listing copy

**Title:** DataHub Context Capsule

**Tagline:** Evidence-addressed DataHub context for agents, with prompt-injection quarantine and hard size bounds.

**Category:** MCP Tools & Agents

**Inspiration:** Catalog metadata is valuable context, but descriptions, fields, and queries are untrusted text. Directly pasting them into an agent prompt creates injection, overflow, and provenance risks.

**What it does:** Context Capsule uses five official DataHub MCP read tools to build a compact Markdown evidence pack for an agent. It hashes the complete source evidence, quarantines instruction-like values, caps entity count, lineage depth, input bytes, and output characters, and emits a minimal manifest without raw catalog data.

**How it was built:** Python 3.11, `mcp-server-datahub`, a local read-only allow-list, deterministic canonical JSON hashing, and a synthetic catalog containing a deliberate prompt injection. MCP mutation support is explicitly disabled.

**Challenges:** Injection can enter through both catalog fields and the operator's search phrase. The final design sanitizes both, validates DataHub URNs, never includes raw historical SQL, and fails closed when no valid entity is found.

**Accomplishments:** Stable evidence/context hashes, explicit quarantine markers, configurable budget truncation, minimized output, and seven passing tests spanning deterministic, malicious, missing, and refusal cases.

**What we learned:** An MCP tool is not automatically a trust boundary. Agent-ready context needs provenance, minimization, and deterministic filtering after retrieval.

**What's next:** Add signed capsule attestations, organization-specific field classification, and context-drift alerts between agent runs.

## 90-second demonstration

1. Show the fixture's two customer datasets and malicious description.
2. Run `context-capsule --fixture demo/catalog.json --query customer`.
3. Open the Markdown capsule and show the SHA-addressed quarantine marker.
4. Open the manifest and explain evidence hash, context hash, entity count, and raw-evidence omission.
5. Demonstrate a 500-character budget and the explicit truncation marker.
6. Run the seven tests and show mutation-tool and malicious-query refusal coverage.

## Publication fields still required

- Public GitHub repository URL
- Public demonstration video URL under three minutes
- Final screenshots
- Entrant/account details supplied through Devpost

