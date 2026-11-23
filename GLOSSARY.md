# CS 6300 Course Site

The repository behind the CS 6300 (RoboRacer) course site and the Canvas course built
from it. Content is authored once under `docs/`, published to the Sphinx site, and pushed
into Canvas by the tools in `canvas/tools/`.

## Language

### Labs

**Lab**:
One unit of the course's practical work, numbered 1 through 9 and tied to an area of the
curriculum. A lab is a single body of work, even when students submit it in more than one
piece.
_Avoid_: Assignment (that is the Canvas object, not the unit of work), project

**Lab part**:
One graded submission within a lab. A split lab has two parts; an unsplit lab is one part
that is simply the lab itself. Both parts of a split lab share one lab repo and one
rubric source folder, and the second part builds on the first.
_Avoid_: Half, sub-lab, a/b

**Sim part**:
The part of a lab a student completes alone in the simulator, before the car day it
prepares them for. Submitting it late is allowed and penalized, not refused.
_Avoid_: Part a, first half

**Car part**:
The part of a lab a team completes on a physical RoboRacer and demonstrates live on a car
day.
_Avoid_: Part b, second half, hardware lab

**Semester week**:
The unit lab deadlines are expressed in. Week 1 is the week the term starts, and a lab
part is due at the end of the week it names, so the whole schedule moves when the term
does and only the semester itself is restated each time the course runs.
_Avoid_: Due date (a week is not a date until the semester is known), week number

**Car day**:
A class meeting where teams run their work on the physical cars. It is the deadline the
sim part exists to meet: a student who arrives without working code has nothing to port.
_Avoid_: Lab day, in-class day

**Lab team**:
The group of students who share one car and one submission for a car part. Teams are
defined by a single Canvas group set for the whole course, not per lab.
_Avoid_: Group (that is Canvas's word for the object), pair

**Demonstration video**:
An unlisted YouTube recording of the student's code actually running - in the simulator
for a sim part, on the car for a car part. Every lab part requires one, and its URL is
submitted in Canvas rather than committed to the repo, so that grading it is one click
and nothing has to be downloaded to be watched.
_Avoid_: Demo, screencast, recording

**Lab repo**:
The per-student (or per-team) GitHub repository a lab's work lives in, copied by the repo
creator from a template that this repository publishes. A lab repo is never split across
a lab's parts, but one may carry across consecutive labs when the later lab builds
directly on the earlier one's code - Waypoint Logger and Pure Pursuit share theirs.
_Avoid_: Starter repo (that is the template this repo pushes, not the student's copy)

**Rubric source**:
The Markdown file whose content is both the lab part's instructions on the site and the
rubric pushed into Canvas. A split lab keeps both parts' rubric sources in the same lab
folder.

### Steppers

**Stepper**:
A self-contained HTML page that walks one lab's code a line at a time, with the theory for
a line in a popup anchored to it. There is one per lab, covering every part of that lab.
_Avoid_: Walkthrough (that is the public repo a stepper is built in), tutorial, demo

**Mode**:
One section of a stepper, shown as a tab and reachable by URL hash. A stepper's modes run
orientation, then one per method or file the student writes, then integration, then what
is graded.
_Avoid_: Tab (what it looks like, not what it is), section, page

**Frame**:
One step within a mode: the line being walked, the values in play at that moment, and what
the student is being shown about it.
_Avoid_: Slide, state

**Preset**:
A named scenario a stepper runs its frames against, so the same code can be walked with
different inputs.
_Avoid_: Scenario, example, fixture

### Canvas

**Area**:
A topic of the curriculum - automatic emergency braking, wall following, SLAM - that gets
one Canvas module containing its tutorial page and its labs. Areas, not labs, set the
order students see.
_Avoid_: Unit, topic, week

**Assignment key**:
The identity under which a lab part's Canvas assignment, rubric, and module placement are
remembered, declared explicitly in the part's front matter so that renaming files or
renumbering labs leaves it untouched. Changing a key abandons the Canvas assignment it
used to name.
_Avoid_: Assignment id (that is Canvas's own numeric id), filename, slug

**Repo task**:
The identity of a lab repo outside this repository - the GitHub repo it is published to
and the key registered with the repo creator. Like an assignment key it is deliberately
stable, so it may carry a number that no longer matches the lab's label.
_Avoid_: Lab id, task name
