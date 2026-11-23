# CS 6300 course site

## Writing

**Use American spelling, never British.** This is a US university course; students, Canvas,
and the course site all read American English. The rule covers everything in this
repository: lab instructions, Canvas page and assignment text, tutorials, lectures, README
files, code comments, docstrings, identifiers, and commit messages.

The ones that come up here:

| Write | Not |
| --- | --- |
| behavior, behaviors | behaviour, behaviours |
| color | colour |
| center | centre |
| meter, meters | metre, metres |
| neighbor, neighbors | neighbour, neighbours |
| organization | organisation |
| localization, localize | localisation, localise |
| minimize, maximize, optimize, normalize, initialize, visualize, prioritize, summarize | minimise, maximise, optimise, normalise, initialise, visualise, prioritise, summarise |
| analyze | analyse |
| modeling, labeled, canceled, traveling | modelling, labelled, cancelled, travelling |
| tire, tires | tyre, tyres |
| gray | grey |
| defense, license | defence, licence |
| judgment | judgement |
| while | whilst |

The `-ize`/`-yze` endings are the general case: prefer them over `-ise`/`-yse`. Doubled
consonants before a suffix are the other recurring trap - American English keeps a single
`l` in *traveling*, *modeling*, *labeled*, *canceled*.

Leave quoted material alone. Upstream F1TENTH and RoboRacer text, paper titles, library and
API names, and anything inside a quotation keep their original spelling even when it is
British - `LaserScan` fields, a cited paper's title, or a dependency's parameter name are
not ours to correct.

## Canvas and the course site

`canvas/` describes the Canvas course. The lab content itself lives in `docs/` and is
published to the course site, so a lab part is written once and read from both.

Run `python canvas/tools/check_sync.py` after editing either. It is the gate the push
already enforces, and it checks the things that are easy to get wrong: a rubric whose
points disagree with its assignment, a site page no assignment points at, a date outside
the semester.

### Three identities stay put

A lab part's file name, title, and lab number all change freely. These do not, so that a
rename stays a local edit - `docs/adr/0002` has the reasoning:

- **`canvas_key`** is the part's identity in Canvas. Its assignment, rubric, and module
  placement are remembered under this key, so it outlives every rename.
- **`repo_task`** names a GitHub repo under `Weber-AGV` and a registration in the faculty
  course-data repo, so it keeps its original number. Computer Vision is Lab 9 and its task
  is still `lab7-computer-vision`.
- **`repo_folder`** follows `repo_task` for the same reason: Lab 9's content is in
  `docs/weber_assignments/labs/lab7/`.

### Deadlines are semester weeks

A lab part carries `due_week`, a week of the semester. The due date and the lock derive
from it, and the semester itself is set once in `calendar` in `canvas/course.yml` - which
is the only thing to change when the course runs again.

`GLOSSARY.md` holds the vocabulary this repo uses for all of it: lab part, sim part, car
part, car day, assignment key, repo task, semester week.
