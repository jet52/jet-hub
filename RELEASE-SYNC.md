# jet-hub release pinning

jet-hub no longer tracks each plugin repo's default branch. Every entry in
`.claude-plugin/marketplace.json` now carries a `source.ref` pinned to that
repo's latest **stable** GitHub release tag, and a workflow keeps those pins
current.

## Why pinning, not `main`

Two problems with tracking `main`:

1. **Users got unreleased code.** At the time this was set up, `jetredline`'s
   `main` was at `4.14.0` while the newest tag was `v4.13.0`. Anyone installing
   from jet-hub received an untagged build.
2. **Nothing told Cowork to re-sync.** Cowork's GitHub marketplace sync watches
   *the connected repository's* default branch for a plugin version bump. When
   the six plugins live in six other repos and jet-hub only points at them,
   jet-hub's own default branch never changes — so the sync trigger could never
   fire. jet-hub's plugin versions sat frozen at whatever the last manual sync
   had picked up.

Pinning fixes both. Each release now produces a commit on jet-hub's default
branch, which is exactly what the sync is looking for.

## Files

| File | Role |
| --- | --- |
| `.claude-plugin/marketplace.json` | Six entries, each pinned via `source.ref` |
| `scripts/bump_refs.py` | Resolves each repo's latest stable release, rewrites `ref` |
| `.github/workflows/sync-plugin-releases.yml` | Runs the script every 30 min, lands the bump |

## How a release propagates

1. You tag and publish a release in, say, `jet52/jetcite`.
2. Within ~30 minutes the jet-hub workflow notices `v2.9.0` → `v2.10.0`.
3. It opens and merges a PR bumping that `ref` on jet-hub's default branch.
4. Cowork picks up the change; Claude Code users run `/plugin marketplace update
   jet-hub` then `/plugin update`.

`scripts/bump_refs.py` uses GitHub's `/releases/latest` endpoint, which by
definition excludes drafts and prereleases — so a `v5.0.0-rc1` tag will not be
shipped to users.

Failure is safe: if a lookup errors or a repo has no published release, the
existing pin is left untouched rather than reset to the default branch.

## One-time repo settings

- **Settings → Actions → General → Workflow permissions**: enable *Allow GitHub
  Actions to create and approve pull requests*. Without it, PR creation fails
  and the workflow falls back to pushing the bump straight to the default
  branch — functional, but a direct push may not satisfy Cowork's
  "version bump merged via pull request" auto-sync condition.
- If the default branch is protected, either exempt `github-actions[bot]` or
  add `--admin` to the `gh pr merge` call.
- GitHub disables `schedule:` triggers on repos with no commit activity for 60
  days. This workflow's own commits normally reset that clock; after a long
  quiet stretch, re-enable it from the Actions tab.

## Manual sync

Run the workflow by hand from the Actions tab (`workflow_dispatch`), or locally:

```sh
GH_TOKEN=$(gh auth token) python3 scripts/bump_refs.py
```

For instant propagation instead of waiting for the poll, add this to each plugin
repo's release job (needs a fine-grained PAT with `contents: write` on jet-hub):

```yaml
- run: gh api repos/jet52/jet-hub/dispatches -f event_type=plugin-released
  env:
    GH_TOKEN: ${{ secrets.JET_HUB_DISPATCH_TOKEN }}
```

## Do not add `version` to marketplace entries

Claude Code resolves a plugin's version from `plugin.json` first and uses it
without warning, so a `version` in the marketplace entry would be silently
masked. Each plugin's `plugin.json` already carries the right version at each
tag — leave the marketplace entries without one.

## Pins as of setup

| Plugin | Pinned tag |
| --- | --- |
| jetmemo | `v3.15.0` |
| jetredline | `v4.13.0` |
| jetpanel | `v1.0.2` |
| jetrehearing | `v1.3.0` |
| jetbriefcheck | `v2.2.0` |
| jetcite | `v2.9.0` |
