#!/usr/bin/env python3
"""Report what changed upstream in the RoboRacer / F1TENTH repositories.

Everything the course depends on - the simulator, the car stack, the rules, the
lab templates, and roboracer.ai itself (GitHub Pages out of f1tenth/roboracer-site)
- is a public GitHub repository, so one commit watch covers all of it.

The report is a time window, not a diff against stored state: there is nothing to
keep in sync and nothing to commit back, so the same command works from a laptop
or from a fresh scheduled run.

    python tools/upstream_watch/watch.py              # the last 7 days
    python tools/upstream_watch/watch.py --days 30    # catching up after a break
    python tools/upstream_watch/watch.py --quiet      # print nothing when nothing changed

Reads the GitHub API through `gh api` when the gh CLI is available, and falls back
to api.github.com with $GH_TOKEN / $GITHUB_TOKEN (or unauthenticated, which the
hourly rate limit makes tight for a list this size).
"""

import argparse
import json
import os
import shutil
import subprocess
import sys
import urllib.error
import urllib.request
from datetime import datetime, timedelta, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_CONFIG = os.path.join(HERE, "watchlist.json")

RATE_LIMIT_HINT = (
    "GitHub API rate limit reached - this report is incomplete. Unauthenticated access "
    "allows only 60 requests an hour; authenticate the gh CLI or set $GH_TOKEN for 5000."
)

warnings = []


def api(path):
    """GET an API path, returning parsed JSON, or None if the call failed."""
    if shutil.which("gh"):
        try:
            out = subprocess.run(
                ["gh", "api", path],
                capture_output=True, text=True, check=True,
            ).stdout
            return json.loads(out)
        except subprocess.CalledProcessError as exc:
            stderr = (exc.stderr or "").strip()
            if "rate limit" in stderr.lower():
                warnings.append(RATE_LIMIT_HINT)
            else:
                lines = stderr.splitlines()
                warnings.append("%s: %s" % (path, lines[-1] if lines else "gh api failed"))
            return None
        except json.JSONDecodeError:
            warnings.append("%s: unparseable response from gh" % path)
            return None

    req = urllib.request.Request(
        "https://api.github.com/" + path.lstrip("/"),
        headers={"Accept": "application/vnd.github+json", "User-Agent": "cs6300-upstream-watch"},
    )
    token = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN")
    if token:
        req.add_header("Authorization", "Bearer " + token)
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.load(resp)
    except urllib.error.HTTPError as exc:
        # 403/429 with the limit exhausted is the one failure worth calling out loudly:
        # every later repo in the run will fail too, and the report would look empty
        # rather than broken.
        if exc.code in (403, 429) and exc.headers.get("X-RateLimit-Remaining") == "0":
            if RATE_LIMIT_HINT not in warnings:
                warnings.append(RATE_LIMIT_HINT)
        else:
            warnings.append("%s: HTTP %s" % (path, exc.code))
        return None
    except (urllib.error.URLError, json.JSONDecodeError, TimeoutError) as exc:
        warnings.append("%s: %s" % (path, exc))
        return None


def first_line(message):
    line = (message or "").strip().splitlines()
    return line[0].strip() if line else "(no commit message)"


def commits_since(repo, branch, since, subpath=None):
    path = "repos/%s/commits?since=%s&per_page=100" % (repo, since)
    if branch:
        path += "&sha=" + branch
    if subpath:
        path += "&path=" + subpath
    data = api(path)
    if not isinstance(data, list):
        return []
    out = []
    for c in data:
        commit = c.get("commit") or {}
        author = (commit.get("author") or {}).get("name") or "?"
        out.append({
            "sha": (c.get("sha") or "")[:7],
            "subject": first_line(commit.get("message")),
            "author": author,
            "date": (commit.get("author") or {}).get("date", ""),
            "url": c.get("html_url", ""),
        })
    return out


def releases_since(repo, since):
    data = api("repos/%s/releases?per_page=20" % repo)
    if not isinstance(data, list):
        return []
    return [
        {"name": r.get("name") or r.get("tag_name"), "tag": r.get("tag_name"),
         "date": r.get("published_at", ""), "url": r.get("html_url", "")}
        for r in data
        if not r.get("draft") and (r.get("published_at") or "") >= since
    ]


def new_repos_since(org, since):
    data = api("orgs/%s/repos?sort=created&direction=desc&per_page=30" % org)
    if not isinstance(data, list):
        return []
    return [
        {"name": r.get("full_name"), "desc": r.get("description") or "",
         "date": r.get("created_at", ""), "url": r.get("html_url", "")}
        for r in data
        if (r.get("created_at") or "") >= since
    ]


def scan(config, since):
    """Walk the watchlist and collect everything that moved inside the window."""
    findings = []
    for tier in config.get("tiers", []):
        tier_rows = []
        for entry in tier.get("repos", []):
            repo = entry["repo"]
            branches = entry.get("branches") or [None]
            # `paths` narrows a busy repo to the directories we actually care about.
            subpaths = entry.get("paths") or [None]

            # One commit can reach us by several branches or paths; report it once.
            seen, commits = {}, []
            for branch in branches:
                for subpath in subpaths:
                    for c in commits_since(repo, branch, since, subpath):
                        label = branch or "default"
                        if c["sha"] in seen:
                            if label not in seen[c["sha"]]["branches"]:
                                seen[c["sha"]]["branches"].append(label)
                        else:
                            c["branches"] = [label]
                            seen[c["sha"]] = c
                            commits.append(c)

            # Releases cost a request per repo, which matters against the 60/hour
            # unauthenticated ceiling, so only the repos that actually cut releases
            # are asked. Set "releases": true in the watchlist to opt one in.
            releases = releases_since(repo, since) if entry.get("releases") else []
            if commits or releases:
                tier_rows.append({
                    "repo": repo, "note": entry.get("note", ""),
                    "commits": commits, "releases": releases,
                })
        if tier_rows:
            findings.append({"tier": tier["name"], "why": tier.get("why", ""), "rows": tier_rows})

    fresh = []
    for org in config.get("new_repos_in_orgs", []):
        fresh.extend(new_repos_since(org, since))
    return findings, fresh


def render(findings, fresh, days, since_human, max_commits):
    out = []
    total = sum(len(r["commits"]) for f in findings for r in f["rows"])
    repos = sum(len(f["rows"]) for f in findings)
    releases = sum(len(r["releases"]) for f in findings for r in f["rows"])

    out.append("# Upstream watch - last %d days (since %s)" % (days, since_human))
    out.append("")
    headline = "%d commit%s across %d repositor%s" % (
        total, "" if total == 1 else "s", repos, "y" if repos == 1 else "ies")
    if releases:
        headline += ", %d release%s" % (releases, "" if releases == 1 else "s")
    if fresh:
        headline += ", %d new repositor%s" % (len(fresh), "y" if len(fresh) == 1 else "ies")
    out.append(headline + ".")
    out.append("")

    for f in findings:
        out.append("## %s" % f["tier"])
        if f["why"]:
            out.append("")
            out.append("*%s*" % f["why"])
        out.append("")
        for row in f["rows"]:
            label = "**[%s](https://github.com/%s)**" % (row["repo"], row["repo"])
            if row["note"]:
                label += " - %s" % row["note"]
            out.append("### %s" % label)
            out.append("")
            for rel in row["releases"]:
                out.append("- **Release %s** (%s) - [%s](%s)" % (
                    rel["tag"], (rel["date"] or "")[:10], rel["name"] or rel["tag"], rel["url"]))
            shown = row["commits"][:max_commits]
            for c in shown:
                branches = "/".join(dict.fromkeys(c["branches"]))
                out.append("- `%s` %s - %s, %s [%s](%s)" % (
                    branches, c["subject"], c["author"], (c["date"] or "")[:10], c["sha"], c["url"]))
            if len(row["commits"]) > len(shown):
                out.append("- ... and %d more commit%s" % (
                    len(row["commits"]) - len(shown),
                    "" if len(row["commits"]) - len(shown) == 1 else "s"))
            out.append("")

    if fresh:
        out.append("## New repositories")
        out.append("")
        for r in fresh:
            desc = " - %s" % r["desc"] if r["desc"] else ""
            out.append("- **[%s](%s)** created %s%s" % (r["name"], r["url"], (r["date"] or "")[:10], desc))
        out.append("")

    if warnings:
        out.append("## Could not be checked")
        out.append("")
        for w in warnings:
            out.append("- %s" % w)
        out.append("")

    return "\n".join(out).rstrip() + "\n"


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--days", type=int, default=7, help="size of the window (default 7)")
    ap.add_argument("--config", default=DEFAULT_CONFIG, help="watchlist JSON")
    ap.add_argument("--max-commits", type=int, default=10,
                    help="commits listed per repository before truncating (default 10)")
    ap.add_argument("--quiet", action="store_true",
                    help="print nothing when nothing changed (for scheduled runs)")
    ap.add_argument("--out", help="write the report here as well as to stdout")
    args = ap.parse_args()

    with open(args.config, encoding="utf-8") as fh:
        config = json.load(fh)

    cutoff = datetime.now(timezone.utc) - timedelta(days=args.days)
    since = cutoff.strftime("%Y-%m-%dT%H:%M:%SZ")

    findings, fresh = scan(config, since)

    if not findings and not fresh:
        if not args.quiet:
            print("No upstream changes in the last %d days." % args.days)
            for w in warnings:
                print("warning: %s" % w, file=sys.stderr)
        return 0

    report = render(findings, fresh, args.days, since[:10], args.max_commits)
    print(report, end="")
    if args.out:
        with open(args.out, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(report)
    return 0


if __name__ == "__main__":
    sys.exit(main())
