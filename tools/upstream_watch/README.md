# Upstream watch

Reports what changed in the RoboRacer / F1TENTH repositories the course depends on.

Everything worth watching is a public GitHub repository — including `roboracer.ai`
itself, which is GitHub Pages served out of `f1tenth/roboracer-site`. So one commit
watch covers the simulator, the car stack, the competition rules, the upstream lab
templates and the `/learn` tutorials, with no Slack account involved.

```bash
python tools/upstream_watch/watch.py              # the last 7 days
python tools/upstream_watch/watch.py --days 30    # catching up after a break
python tools/upstream_watch/watch.py --quiet      # silent when nothing changed
python tools/upstream_watch/watch.py --out digest.md
```

No arguments, no setup: it reads the GitHub API through `gh api` when the gh CLI is
authenticated, and otherwise falls back to `api.github.com` with `$GH_TOKEN` /
`$GITHUB_TOKEN`.

## Why there is no state file

The report is a **time window**, not a diff against a stored baseline. Nothing is
cached, nothing has to be committed back, and a run from a fresh checkout gives the
same answer as a run from your laptop. The cost is that a window can overlap or
leave a gap if runs drift; `--days` is cheap, so overlap generously rather than
trying to make the windows meet exactly.

## Editing the watchlist

[`watchlist.json`](watchlist.json) holds the repositories, grouped into tiers that
order the report. Per entry:

| Key | Meaning |
| --- | --- |
| `repo` | `owner/name` |
| `branches` | branches to check; omit for the repo's default branch |
| `paths` | only report commits touching these paths — use it on busy repos |
| `note` | why we care; printed beside the repo name |

`paths` is what keeps the report readable. `roboracer-site` is an actively developed
front end that can produce two dozen commits a week about layout and blog tooling;
narrowing it to `public/data/learn-new` and `src/components/learn` leaves the learn
content and drops the chrome.

`new_repos_in_orgs` lists organizations to check for repositories created inside the
window — that is what catches a new lab template appearing upstream. It deliberately
watches `f1tenth` only: new `Weber-AGV` repositories are our own work, and reporting
them back to us is noise.

## Known gaps

- **Private discussion is invisible.** Anything decided in Slack and never committed
  will not show up here. This watches artifacts, not conversation.
- **Commit volume is not importance.** A one-line change to the simulator's collision
  handling matters more than thirty commits of website styling. The tiers in
  `watchlist.json` are the only prioritization; read the top tier first.
- **Force-pushes and rewritten history** can move commits outside the window.
