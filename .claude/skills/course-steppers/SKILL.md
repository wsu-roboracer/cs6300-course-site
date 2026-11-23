---
name: course-steppers
description: Stepper standard for CS 6300 - how a lab's stepper under docs/_static/steppers/ is built. Use when building or editing a stepper, ordering its modes, choosing which mode opens first, or deciding what gets a stepper of its own. Triggers on "stepper", "walkthrough".
---

# Course steppers

A **stepper** is one self-contained HTML page under `docs/_static/steppers/` that walks a
lab's code a line at a time, with the theory for a line in a popup anchored to it.
Students use it while writing the lab, so it is organized around the work.

One stepper per **lab**, covering every part of that lab. A lab's simulator part and car
part share the page, with the car as a mode, because the port from simulator to car is the
comparison a student needs side by side.

## Build from the nearest existing stepper

`lab1.html` and `lab2.html` are the reference implementations. Copy whichever is closer to
the lab at hand and replace its content.

Their structures are the contract: `MODES`, `state`, one `build<Mode>()` per mode
returning frames, `info()` for a line's popup, and `L()` to locate a line by a needle. The
frame machinery, keyboard handling, and layout already work.

## The skeleton

Every stepper carries these modes, in this order:

1. **Orientation** - the package, the files, and why the code is shaped this way. Accent
   `--teal`.
2. **Code** - one mode per method or file the student writes. As many as the lab needs.
3. **Integration** - running it for real: on the car, or reading the ROS graph.
4. **Graded** - the rubric. Accent `--deep`. Always last.

## Mode order

Order the code modes **the way the student writes them**, falling back to the order the
methods appear in the file where that is ambiguous. Lab 2 runs `__init__` →
`odom_callback` → `scan_callback` → brake on that rule.

`docs/adr/0003` records why the lab instructions' own section order is not the rule.

## The first mode opens

`state.mode` is `MODES[0]`, written that way rather than as a repeated string, so the
invariant holds as the modes change. A student arriving sees what the lab is before its
code; the URL hash reaches any mode directly (`lab2.html#scan`) for one returning mid-lab.

Keep orientation short enough to earn the landing.

## Renames reach the stepper

A stepper links back into the site using `site_page` names from `canvas/assignments/`, so
renaming a lab part breaks it. The steppers are untracked, which keeps them out of a
`git status` sweep: check them by hand whenever a lab part is renamed or renumbered.

## Done when every line is true

- `MODES` lists the modes in skeleton order, and `state.mode` is `MODES[0]`
- orientation is first, graded is last, integration sits immediately before graded
- every code mode names a method or file the student writes
- the points in the graded mode match `Total: N Points` in the lab part's `rubric_source`,
  so the stepper and Canvas agree
- each mode has its own accent colour, `--teal` on orientation and `--deep` on graded
- `location.hash` reaches every mode in `MODES`
- links into the site match the current page names (`lab2-sim.html`, not `lab2.html`)
- the page runs from `file://` with no build step, and no external CSS, JS, font, or image

## Workflow

A stepper iterates in its own public repo, `cs6300-lab<N>-walkthrough`, published to
GitHub Pages and linked from the lab's Canvas module in `canvas/modules.yml`. Build and
review it there, then copy the finished page into `docs/_static/steppers/`.
