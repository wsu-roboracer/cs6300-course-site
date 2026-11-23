# Lab 3 Car - Wall Following

> **SKELETON.** Every section below is a TODO. The structure matches Lab 2 Car
> (`docs/weber_assignments/labs/lab2/CAR.md`), which is the worked example to
> copy from.

## I. Learning Goals

- TODO: what moving this node to real hardware teaches that the simulator cannot
- TODO: what the real sensor does that the simulated one does not

## II. Overview

In Lab 3 Sim you built and tuned wall following in the simulator. In this lab your team runs
that work on a real RoboRacer in the CAE hallway.

| Part | Task | What You Learn |
| --- | --- | --- |
| 1 | Port the node to the car | TODO |
| 2 | Bench test before driving | TODO |
| 3 | Tune against real sensors | TODO |
| 4 | Record the demonstration | TODO |

**This lab is done in teams, in class** (Mon Feb 1). There is no new repository: you work in
the Lab 3 Sim repository of whichever team member's node your team runs.

## III. Prerequisites

- Lab 3 Sim passing in the simulator. Do not bring unfinished code to the car.
- You can bring the car up and drive it with the controller.

## IV. Part 1 - Port the Node to the Car

TODO. What changes between the simulator and the car for this lab:
`/scan` only - this one ports to the car without a topic change.

Remember the command chain: your node publishes on `/drive` at mux priority 10, while the
joystick sits at priority 100 and always outranks it. The person holding the controller is
the emergency stop. The mux also drops any input that goes quiet for more than 0.2 s.

## V. Part 2 - Bench Test First

TODO. Wheels off the ground, verify the behavior, and only then put the car down.

## VI. Part 3 - Tune in the Hallway

TODO. Start slow and work up. Name the two failures you expect students to hit, the way
Lab 2 Car does - that section is what makes the difference between a lab and a checklist.

**Safety procedure for every run:** TODO.

## VII. Part 4 - The Demonstration, Recorded

TODO: list exactly what the video must show.

Upload it to YouTube as **unlisted**, then **paste the link into the text box on the Canvas
assignment**, along with your repository URL. The link goes on the Canvas submission, not in
`SUBMISSION.md`.

**YouTube only, and unlisted.** Not Google Drive, not a file: a video that has to be
downloaded before it can be watched does not get graded.

## VIII. Submitting

1. Commit your ported node and any launch or parameter file you used on the car.
2. Fill in the **Lab 3 Car** section of `SUBMISSION.md`. The video link does not go in there.
3. Commit and push, and check on github.com that your latest commit is there.
4. One team member submits on Canvas, pasting **both** the repository URL and the video link
   into the text box.

## IX. Grading Rubric

> TODO: replace these placeholders. The points must still total 100, or no Canvas rubric is
> built from this file and `check_sync.py` will say so.

| Item | What is graded | Points |
| --- | --- | --- |
| Ported and connected | TODO: the node runs on the car against the real topics | 15 |
| Bench test | TODO | 10 |
| Works on the car | TODO: the main behavior, demonstrated | 50 |
| Handles the hard case | TODO: the case the simulator never produced | 15 |
| Write-up | The **Lab 3 Car** section of `SUBMISSION.md` | 10 |

**Total: 100 Points**

Everything but the write-up is graded from your team's video.
