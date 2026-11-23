# 0002. Stable Identities For Lab Parts

**Status:** Accepted
**Date:** 2026-11-21
**Deciders:** Scott

## Context

Labs are named for the student. A lab with two graded submissions labels them by what the
student is actually doing - `Lab 2 Sim - Automatic Emergency Braking` and `Lab 2 Car -
Automatic Emergency Braking` - rather than by a `2a`/`2b` code the student has to decode.
An earlier `a`/`b` scheme was dropped because it could not survive Lab 6, whose two parts
divide by topic rather than by simulator versus car, so the same suffix meant two
different things in the same course.

Labels of that kind change. Dropping `a`/`b` renames every lab part once. Promoting Lab 6's
two topics to labs of their own renumbers everything after them, and moving Computer
Vision to the end of the course renumbers it again.

Two identities used to track those labels, and both cross a boundary this repository does
not control:

* The **assignment key** was the filename stem of a file in `canvas/assignments/`. It is
  the key under which `canvas/canvas_ids.json` remembers a part's Canvas assignment,
  rubric, and module placement. `push_to_canvas.py` looks items up by that key and has no
  prune step, so a key with no matching file is simply never visited again.
* The **repo task** is both the name of the GitHub repository under the `Weber-AGV`
  organization and the key registered with the student repo creator in the faculty
  course-data repository.

The cost is not hypothetical. The `a`/`b` rename alone abandoned four assignments -
Canvas ids 913, 914, 915, and 919 - which still exist in the course, still sit in the
state file, and are referenced by no module. The restructure that prompted this decision
would have abandoned ten more. On an unpublished course that is untidy. On a live course
it means students losing submissions and grades attached to an assignment nothing points
at any more.

## Decision

Identities that cross a system boundary do not track display labels.

* Every lab part declares an explicit `canvas_key` in its front matter. Renaming the file
  or renumbering the lab leaves it untouched.
* Repo task values are frozen at their current spelling and are not renumbered. Motion
  Planning keeps `lab8-motion-planning`, which still matches its label. Computer Vision
  keeps `lab7-computer-vision` even though it is now Lab 9.
* The four abandoned assignments are deleted and `canvas_ids.json` is reset before the
  renames, while the course is unpublished and no student has seen any of it.

## Options considered

### Renumber the external identities to match the labels

Rename the GitHub repositories, update the faculty course-data registration, and let every
identity read consistently.

* Pro: No mismatch for a future reader to explain.
* Con: One label change becomes a coordinated edit across three systems, two of which live
  outside this repository.
* Con: Breaks the repo creator links for any student who already has them.

### Add a prune step instead of explicit keys

Keep deriving the key from the filename and teach `push_to_canvas.py` to report or delete
state entries with no source file.

* Pro: No new front matter field.
* Con: Makes orphans visible but still creates them. Every rename still abandons a live
  assignment and its grades.

## Consequences

**Easier now:**

* Lab parts can be renamed, renumbered, and reordered without touching Canvas.
* The remaining mismatch is confined to one place and one lab.

**Harder now:**

* `repo_task: lab7-computer-vision` on Lab 9 reads like a mistake to anyone who has not
  read this ADR. The glossary entry for Repo task says so explicitly.
* `canvas_key` is a second thing to get right when a lab part is added, and a duplicate
  silently retargets an existing Canvas assignment.

**We should revisit this if:**

* Lab labels become stable enough that the indirection costs more than it saves.
* The repo creator gains a way to alias a task, which would make renumbering repo tasks
  cheap.
