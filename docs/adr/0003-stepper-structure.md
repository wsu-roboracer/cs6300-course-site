# 0003. Stepper Structure

**Status:** Accepted
**Date:** 2026-11-21
**Deciders:** Scott

## Context

A stepper is a self-contained HTML page that walks a lab's code a line at a time, with the
theory for each line in a popup anchored to that line. Two existed when this was written,
for Lab 1 and Lab 2, and the course has nine labs to cover.

Neither was under version control, so neither carried any record of why it was built the
way it was. Both had nonetheless converged on the same shape - a setup mode, a run of code
modes, an integration mode, and a closing mode showing what is graded - and both opened on
a mode partway along that run rather than at its start: Lab 1 on mode 2 of 6, Lab 2 on
mode 3 of 6. Those defaults were not chosen for a reason; they were simply what the files
happened to say.

Fixing the structure now decides what eight more steppers look like, so it is worth
deciding rather than inheriting.

## Decision

Every stepper follows one skeleton: **orientation, then one mode per method or file the
student writes, then integration, then what is graded.** The orientation mode is accented
teal and the graded mode deep, and graded is always last.

Code modes are ordered **the way the student writes the code**, falling back to the order
the methods appear in the file when that is ambiguous.

`state.mode` is `MODES[0]`, expressed in exactly that way rather than as a repeated
string, so the page opens on orientation and the invariant cannot drift. The URL hash
still reaches any mode directly, which covers the student returning mid-lab.

There is **one stepper per lab**, not per lab part. A lab's simulator part and car part
share one page, with the car as a mode.

The standard lives in `.claude/skills/course-steppers/SKILL.md`, next to the checklist
that applies it.

## Options considered

### Order the modes to match the lab instructions

Mirror the section order of the lab's `SIM.md` or `CAR.md`.

* Pro: the stepper and the instructions would agree, section for section.
* Con: not available for every lab. `lab2/SIM.md` is organized by topic with no numbered
  parts, while `lab5` and `lab6` have numbered part tables, so the labs do not agree with
  each other about what a part is.
* Con: the instructions are organized for reading and the stepper is used while working.

### Open on the first mode where code gets written

Keep the behaviour both steppers already had, stated as a rule.

* Pro: saves a returning student two clicks.
* Con: a student arriving for the first time lands partway through with nothing telling
  them they skipped the setup.
* Con: "the first mode where code gets written" has to be decided per lab, so across nine
  steppers the landing mode is unpredictable.

### Remember the last mode visited

Persist the mode and restore it.

* Pro: serves the first-time and returning student at once.
* Con: adds persisted state to a page whose whole virtue is that it is a single file that
  runs from `file://`.
* Con: the URL hash already solves the returning case.

### One stepper per lab part

Give each part its own page, matching the Canvas assignments.

* Pro: one page per thing being graded.
* Con: sixteen pages instead of nine.
* Con: separates the simulator code from its port to the car, which is the comparison a
  student most needs to see side by side.

## Consequences

**Easier now:**

* A student who learns one stepper's layout can navigate all of them.
* The landing mode is the same everywhere, and it is structural rather than a convention
  somebody has to remember.
* The skeleton says what to build next for a lab that has no stepper yet.

**Harder now:**

* Lab 2's stepper has no orientation mode: it opens on `__init__`, which is a code mode.
  It needs one written before it conforms.
* Orientation has to be worth landing on, which is content that did not have to exist
  before.

**We should revisit this if:**

* Students are observed to skip orientation every time, which would mean it is not
  earning the landing.
* A lab turns out to need so many code modes that one page stops being navigable.
