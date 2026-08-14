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
| `jetbriefcheck` | Check ND appellate brief PDFs for Rules of Appellate Procedure compliance; also scans each filing for concealed text — white-on-white, sub-legible, off-page, or otherwise invisible to a reader |
| `jetcite` | Parse legal citations and link to official government sources |

Several tools (notably `jetmemo` and `jetredline`) work best with the **ndlaw MCP
server** for citation and authority lookups across ND primary law. That is distributed
separately — see [ndlaw MCP](#ndlaw-mcp-citation--authority-lookups) below — because it
requires a password that must not live in this public repository.

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

## ndlaw MCP (citation & authority lookups)

`jetmemo` and `jetredline` call the `ndlaw` MCP server to verify citations and look up ND
primary law — opinions (1889–present), the Constitution, N.D.C.C. statutes, court rules,
and the Administrative Code. It is **not** bundled in this marketplace because it sits behind a password.
Distribute it one of two ways:

- **Per user (now):** have each member install the one-click bundle
  [`ndlaw.mcpb`](https://github.com/jet52/ndlaw/raw/main/deploy/ndlaw.mcpb)
  and enter the server URL, username, and password you provide. Requires Node.js on the
  machine. See [ndlaw/deploy/CLIENTS.md](https://github.com/jet52/ndlaw/blob/main/deploy/CLIENTS.md).
- **Org connector (cleaner, once auth is improved):** provision `ndlaw` as a managed
  connector so members don't handle the password directly.

The skills degrade gracefully (web lookups) if the MCP isn't present, so it's recommended
but not strictly required.

---

## Strongly recommended: tell Claude how to handle legal work

These tools are far more reliable when Claude operates under explicit instructions to
**verify before it cites** and to **flag uncertainty instead of smoothing it over**.
Large language models will otherwise produce fluent, confident, and occasionally
fabricated citations — exactly the failure mode that matters most in legal work.

Add instructions like the following to your global Claude config (`~/.claude/CLAUDE.md`
for Claude Code, or your Cowork/Chat custom instructions). The retrieval rule is the
important one; the rest set a useful default posture. Adapt them to your role and
practice:

```markdown
- Accuracy over fluency. If a complete answer requires saying "I don't know" or
  "I need to look this up," do that instead of guessing. Never fabricate citations,
  case names, statutes, dates, or quotations — verify before including them. Flag
  uncertainty rather than smoothing it over.

- Label confidence as high / moderate / low / unknown when making factual claims,
  legal predictions, or empirical estimates. Distinguish what you know from what
  you're inferring. When confidence is low or unknown, briefly say what would move it.

- When citing legal authority, follow Bluebook for citations and Garner's Redbook for
  prose style. Before citing an authority — opinion, statute, regulation,
  constitutional provision, or court rule — or asserting its rule, exact words,
  status, or date, retrieve the text from an approved source (the ndlaw MCP for
  North Dakota primary law, the CourtListener MCP, the relevant jurisdiction's
  official site, or a fallback web fetch of Justia or Google Scholar — treating the
  last two as below primary and official sources) and disclose where it came from,
  with a link where one exists. Retrieval confirms the authority and its wording are
  real, not that they were read correctly — keep a confidence label on any
  interpretation even when the text was retrieved. If retrieval fails, say so
  explicitly; only then rely on memory, and only for authority you are highly
  confident about, naming which element you are confident on (e.g., the holding) and
  which you are not (e.g., the pinpoint or verbatim quotation).

- Separate empirical, conceptual, and normative claims. Flag when a disagreement is
  really about one of these masquerading as another.

- Be direct, not sycophantic. If I'm wrong, say so and lead with why. Give the
  strongest arguments on both sides; when we disagree, identify the crux — the
  specific point where, if you changed your mind, the conclusion would flip.

- Ask before sharing potentially sensitive information (e.g., confidential client,
  case, or matter details) in commits, public queries, or anywhere it could reach
  unapproved recipients.

- Match length to the question. Brief questions get brief answers; complex ones get
  the detail they need. Don't pad.
```

The `jetmemo` and `jetredline` skills already enforce retrieval-before-citation
internally, but a global instruction extends that discipline to everything else you ask
Claude to do.

---

## Maintainer notes

- Each tool repo carries its own `.claude-plugin/plugin.json` (the marketplace is a thin
  index; the tool repos are the source of truth). The `skills` path points at each repo's
  existing skill directory (`./skill`, or `./skills/jetredline`).
- Marketplace entries are **pinned to release tags**, not to any default branch — every
  entry carries a `source.ref`, and `.github/workflows/sync-plugin-releases.yml` bumps it
  to each repo's latest stable release every 30 minutes. **A tool ships to users when you
  publish a GitHub release, not when you push `main`.** Do not hand-edit a `ref`; the
  sync owns that field. See [RELEASE-SYNC.md](RELEASE-SYNC.md) for how a release
  propagates and how to force a sync.
- Validate after changes: `claude plugin validate .` (marketplace) and
  `claude plugin validate ../<tool-repo>` (each plugin).
