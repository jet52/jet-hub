# jet-hub

A Claude **plugin marketplace** for the JET legal tools — install and stay current
with the bench-memo, opinion-editing, interpretive-panel, rehearing, citation, and
brief-compliance skills from one place, in Claude Cowork or Claude Code.

> **Not an Official Court Product.** These are independent, open-source tools published
> by an individual in a personal capacity as legal-educational software, consistent with
> Rule 3.1 of the North Dakota Code of Judicial Conduct. They are not authorized,
> endorsed, or maintained by the North Dakota Supreme Court or the state court system.
> Each tool's output is machine-generated and is not legal advice. See each plugin's own
> README for its specific disclaimer.

## What's in it

| Plugin | What it does |
|---|---|
| `jetmemo` | ND Supreme Court bench memos from publicly filed appellate briefs and record documents |
| `jetredline` | Edit/proofread ND appellate opinions, orders, and bench memos (tracked changes; Redbook/Bluebook checks) |
| `jetpanel` | Multi-perspective interpretive analysis for close statutory/constitutional questions |
| `jetrehearing` | Analyze petitions for rehearing (N.D.R.App.P. 40) and draft a cross-check memo |
| `jetbriefcheck` | Check ND appellate brief PDFs for Rules of Appellate Procedure compliance |
| `jetcite` | Parse legal citations and link to official government sources |

Several tools (notably `jetmemo` and `jetredline`) work best with the **ND Courts MCP
server** for citation and precedent lookups. That is distributed separately — see
[ND Courts MCP](#nd-courts-mcp-citation--precedent-lookups) below — because it requires
a password that must not live in this public repository.

---

## For organization admins (Team / Enterprise) — recommended

A GitHub-synced organization marketplace pushes these tools to every member's **Cowork**
(and Chat) automatically, and keeps them current (~30-minute sync), with no per-user setup.

1. In your organization settings, open the plugins/marketplace management area and add a
   marketplace **synced from GitHub**, pointing at this repository: `jet52/jet-hub`.
2. Choose which of the six plugins to make available to members.
3. Members see them in Cowork → **Customize**; updates propagate automatically on the sync.

See Anthropic's guide: <https://support.claude.com/en/articles/13837433-manage-claude-cowork-plugins-for-your-organization>

## For individual users

**Claude Cowork / Desktop:** add this marketplace in the Cowork pane's **Customize →
plugins/skills** directory (use `jet52/jet-hub`), then enable the plugins you want.
Note: the Cowork and Code panes have **separate** plugin lists — add the marketplace in
whichever pane you actually work in (for most users, Cowork).

**Claude Code (CLI/IDE):**
```bash
/plugin marketplace add jet52/jet-hub
/plugin install jetmemo@jet-hub
```
Update later with `/plugin marketplace update jet-hub`.

---

## ND Courts MCP (citation & precedent lookups)

`jetmemo` and `jetredline` call the `ndcourts` MCP server to verify citations and look up
precedent. It is **not** bundled in this marketplace because it sits behind a password.
Distribute it one of two ways:

- **Per user (now):** have each member install the one-click bundle
  [`ndcourts.mcpb`](https://github.com/jet52/ndcourts-mcp/raw/main/deploy/ndcourts.mcpb)
  and enter the server URL, username, and password you provide. Requires Node.js on the
  machine. See [ndcourts-mcp/deploy/CLIENTS.md](https://github.com/jet52/ndcourts-mcp/blob/main/deploy/CLIENTS.md).
- **Org connector (cleaner, once auth is improved):** provision `ndcourts` as a managed
  connector so members don't handle the password directly.

The skills degrade gracefully (web lookups) if the MCP isn't present, so it's recommended
but not strictly required.

---

## Maintainer notes

- Each tool repo carries its own `.claude-plugin/plugin.json` (the marketplace is a thin
  index; the tool repos are the source of truth). The `skills` path points at each repo's
  existing skill directory (`./skill`, or `./skills/jetredline`).
- Marketplace entries currently track each repo's **default branch**. For controlled
  releases, pin each entry to a tag — add a `source.ref` (e.g. `"ref": "v3.7.0"`) once a
  release tag includes the `plugin.json`. Bump the tag to ship an update.
- Validate after changes: `claude plugin validate .` (marketplace) and
  `claude plugin validate ../<tool-repo>` (each plugin).
