#!/usr/bin/env python3
"""Pin every jet-hub marketplace entry to its repo's latest stable release tag.

Reads .claude-plugin/marketplace.json, asks GitHub for each plugin repo's
latest *published, non-draft, non-prerelease* release, and rewrites
``source.ref`` when it has moved.

Exits 0 whether or not anything changed. Writes ``changed=true|false`` and a
markdown ``summary`` to $GITHUB_OUTPUT when running under Actions.

Set RELEASES_FIXTURE=<path to json> to run offline against canned data
({"owner/repo": "v1.2.3"}); used by the self-test.
"""

from __future__ import annotations

import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path

MARKETPLACE = Path(".claude-plugin/marketplace.json")
API = "https://api.github.com"
GIT_SOURCES = {"github", "url", "git-subdir"}


def repo_slug(source: object) -> str | None:
    """Return 'owner/repo' for a git-backed plugin source, else None."""
    if not isinstance(source, dict) or source.get("source") not in GIT_SOURCES:
        return None
    if source.get("source") == "github":
        return source.get("repo")
    url = source.get("url", "")
    if "github.com" not in url:
        return None
    tail = url.split("github.com", 1)[1].lstrip(":/")
    if tail.endswith(".git"):
        tail = tail[:-4]
    parts = [p for p in tail.split("/") if p]
    return "/".join(parts[:2]) if len(parts) >= 2 else None


def latest_release(slug: str, fixture: dict | None) -> str | None:
    """Latest stable release tag for a repo.

    The /releases/latest endpoint already excludes drafts and prereleases,
    which is exactly the 'stable releases only' policy we want.
    """
    if fixture is not None:
        return fixture.get(slug)

    req = urllib.request.Request(
        f"{API}/repos/{slug}/releases/latest",
        headers={
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": "jet-hub-release-sync",
        },
    )
    token = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN")
    if token:
        req.add_header("Authorization", f"Bearer {token}")

    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.load(resp)
    except urllib.error.HTTPError as exc:
        if exc.code == 404:
            print(f"  ! {slug}: no published release yet — leaving ref alone")
            return None
        print(f"  ! {slug}: HTTP {exc.code} — leaving ref alone", file=sys.stderr)
        return None
    except Exception as exc:  # network hiccup: never clobber a good pin
        print(f"  ! {slug}: {exc} — leaving ref alone", file=sys.stderr)
        return None

    return data.get("tag_name")


def main() -> int:
    fixture_path = os.environ.get("RELEASES_FIXTURE")
    fixture = json.loads(Path(fixture_path).read_text()) if fixture_path else None

    doc = json.loads(MARKETPLACE.read_text())
    changes: list[tuple[str, str | None, str]] = []
    failures = 0

    for entry in doc.get("plugins", []):
        name = entry.get("name", "?")
        slug = repo_slug(entry.get("source"))
        if not slug:
            print(f"  - {name}: not a git source, skipped")
            continue

        tag = latest_release(slug, fixture)
        if not tag:
            failures += 1
            continue

        current = entry["source"].get("ref")
        if current == tag:
            print(f"  = {name}: {tag}")
            continue

        entry["source"]["ref"] = tag
        changes.append((name, current, tag))
        print(f"  + {name}: {current or 'default branch'} -> {tag}")

    if changes:
        # ensure_ascii=False keeps em dashes readable instead of — escapes.
        MARKETPLACE.write_text(
            json.dumps(doc, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
        )

    lines = [f"- **{n}**: `{o or 'default branch'}` → `{t}`" for n, o, t in changes]
    body = "\n".join(lines) or "no changes"

    # Written to a file rather than interpolated into the workflow's shell, so
    # upstream tag names can never be spliced into a command line.
    Path(os.environ.get("BODY_FILE", "/tmp/release-sync-body.md")).write_text(
        body + "\n", encoding="utf-8"
    )

    out = os.environ.get("GITHUB_OUTPUT")
    if out:
        with open(out, "a") as fh:
            fh.write(f"changed={'true' if changes else 'false'}\n")

    # A lookup failure is worth surfacing, but only after good pins are written.
    return 1 if failures and not changes else 0


if __name__ == "__main__":
    raise SystemExit(main())
