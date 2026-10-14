# Canvas course items

This folder defines the CS 6300 Canvas course and holds the tools that push it to a Canvas server.

## How Canvas and the site fit together

- **The course site (`docs/`) owns the content.** Tutorials, lab instructions, deliverables, and rubrics are written there and nowhere else.
- **Canvas owns the logistics.** Due dates, points, submissions, grades, and announcements.
- **Canvas items are thin.** A Canvas page gives a short overview of an area and links into the site tutorial. A Canvas assignment links to the lab on the site and to the student's repository. Nothing is copied from the site, so there is only one copy to keep current.

Canvas has one module per area covered on the site. Each module has the area's page first, then its lab.

## Layout

| Path | What it holds |
|------|---------------|
| `course.yml` | Term, Canvas server, site URL, repo creator, assignment groups |
| `modules.yml` | Canvas modules and the order of their items |
| `pages/` | One file per Canvas page |
| `assignments/` | One file per Canvas assignment |
| `tools/check_sync.py` | Checks this folder against the site |
| `tools/push_to_canvas.py` | Creates or updates the Canvas course |
| `tools/sync_lab_repo.py` | Pushes a lab folder to its student-facing GitHub repo |
| `canvas_ids.json` | Canvas IDs from earlier pushes, written by the push script |

## Page files

Each file in `pages/` has settings at the top and a short overview below.

```markdown
---
site_page: tutorials/ModuleC/slam/index     # area index page under docs/, without .rst
---

Two or three sentences about the area.
```

The push script adds a button that opens the tutorial and a list of the tutorial's pages, read from the site. The Canvas title is the heading of the site page unless you add a `title:` line.

## Assignment files

The file name is the assignment's ID (`lab6a.md` is `lab6a` in `modules.yml`).

```markdown
---
site_page: weber_assignments/labs/lab5       # page under docs/, without .rst
rubric_source: docs/weber_assignments/labs/lab5/README.md   # optional
repo_task: lab5-slam                          # task name in the repo creator, and the lab repo's name
repo_folder: docs/weber_assignments/labs/lab5 # lab folder in this repo that the lab repo is built from
assignment_group: Labs                        # must exist in course.yml
points: 100
due: 2027-03-05 23:59                         # course time zone; null while TBD
team: true
submission_types: [online_url, online_upload] # Canvas submission types, or [none]
---

Short description shown in Canvas.
```

The push script adds a button that opens the lab on the site and a button that opens the repo creator for `repo_task`. Team assignments are assigned to the group set named in `course.yml`.

If `rubric_source` is set and that file contains a `Total: N Points` line, `points` must match it.

## Lab repositories

There are no submodules. Each lab's starter files live in a plain folder in this repo, named by the assignment's `repo_folder`. That folder is the source of truth. `sync_lab_repo.py` pushes it to the lab's own GitHub repo, `<org>/<repo_task>`, which is the template students get a copy of. This is the same arrangement CS 1400 uses.

```sh
python canvas/tools/sync_lab_repo.py lab1                      # dry run: show what would change
python canvas/tools/sync_lab_repo.py lab1 --push               # push main
python canvas/tools/sync_lab_repo.py lab1 --push --solutions   # push main and the solutions branch
python canvas/tools/sync_lab_repo.py --all                     # dry run for every lab
```

A dry run is the default. The lab repo's `main` branch is made identical to the folder, so a file deleted here is deleted there. Folders named `solution` or `solutions` are never pushed to `main`.

Never edit a lab repo directly. Edit the folder here and sync.

The org is `lab_repos.org` in `course.yml`. A lab repo must already exist on GitHub; the script prints the commands to create one as a private template.

### Solutions

This repo is public, so solutions are not kept in it. Each lab's solution lives in `<solutions_dir>/<repo_task>/` (`lab_repos.solutions_dir` in `course.yml`, by default the `solutions` folder beside the course folder). It is laid out like the lab repo and holds only the solved copy of each file that differs from the starter.

`--solutions` rebuilds the lab repo's `solutions` branch as `main` plus those files, so a change to the starter reaches the solutions branch without copying anything by hand.

Keep lab repos private. A solutions branch is visible to anyone who can read the repo.

## Student repositories

Students get their own copy of each lab repository through the GitHub repo creator, the same tool CS 1400 and CS 2420 use. The link on each assignment is built from `repo_creator` in `course.yml` and the assignment's `repo_task`:

```text
https://hadzikcs.netlify.app/gh?course=sh/CS6300&task=lab5-slam
```

The course and every task must be registered in the faculty course-data repo before the links work. Team labs need `"mode": "group"` on the task and a `groups` list on the course there.

## Setup

```sh
pip install -r canvas/requirements.txt
```

Copy `canvas/.env.example` to `.env` at the repository root and fill in the server URL, an access token, and the course ID. `.env` is ignored by git.

## Checking

```sh
python canvas/tools/check_sync.py --list
```

It fails when:

- a lab page on the site has no Canvas assignment, or a tutorial area has no Canvas page
- a page, assignment, or module item points at a site page that does not exist
- an assignment's points disagree with the total in its rubric
- a page or assignment is missing from `modules.yml`, or `modules.yml` names something that does not exist
- assignment group weights do not total 100

It warns about anything still marked TBD. The same check runs on every pull request.

## Pushing

```sh
python canvas/tools/push_to_canvas.py --dry-run     # write the HTML to canvas/_build/, no network
python canvas/tools/push_to_canvas.py --test        # check the token, list courses and their IDs
python canvas/tools/push_to_canvas.py               # push everything
python canvas/tools/push_to_canvas.py --only lab3   # push one page or assignment
```

A push runs the check first and stops if it finds errors. It then creates or updates the assignment groups, the team group set, the pages, the assignments, and the modules.

Pushing again updates the same items. The script remembers Canvas IDs in `canvas_ids.json`, kept separately for each server and course, so a test server and the real course do not collide. If an item was deleted in Canvas, the next push recreates it.

With `publish: false` in `course.yml`, new items are created unpublished and the script never publishes or unpublishes anything. Set it to `true` to publish everything on push.

Module items added by hand in Canvas are left in place, below the items listed in `modules.yml`.

## Common changes

**Add a lab:** add the page under `docs/`, add a file in `assignments/`, and add it to `modules.yml`. The check fails until all three are done.

**Add an area:** add the tutorial under `docs/tutorials/`, add a file in `pages/`, and add a module to `modules.yml`.

**Rename or move a site page:** update `site_page` in the matching file. The check reports the ones that broke.

**Change points or a due date:** edit the assignment file and push.

## What not to put here

Do not commit `.env`, quiz answer keys, solutions, or student data.
