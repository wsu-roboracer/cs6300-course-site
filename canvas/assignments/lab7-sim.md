---
canvas_key: lab7-sim            # Canvas identity; never changes. See docs/adr/0002.
site_page: weber_assignments/labs/lab7-sim
rubric_source: docs/weber_assignments/labs/lab6/PURSUIT-SIM.md
repo_task: lab6-pure-pursuit
repo_folder: docs/weber_assignments/labs/lab6
repo_continues: lab6-sim     # same repo as the part before it: no new repo
assignment_group: Labs
points: 100
due_week: 9             # see calendar in canvas/course.yml; the lock is two weeks later
notes: due the Sunday the break ends
team: false
submission_types: [online_text_entry]   # repo URL plus the demonstration video URL
---

Write a Pure Pursuit node that reads the waypoints you recorded in Lab 6 and drives the path autonomously in the simulator. It finds the point on the path one lookahead distance ahead, transforms it into the car's frame, and steers along the arc that reaches it.

You do this half by yourself, in the simulator, and you tune it there: the lookahead distance and speed you settle on are what your team starts from when it runs this on a real RoboRacer in Lab 7 Car. Take your pose from the particle filter on `/pf/pose/odom`, the same topic you logged against.

There is no new repository. You keep working in the one you already have from Lab 6, and you drive the CSV you recorded there. The full instructions, deliverables, and rubric are on the course site.

**Submit here**, in the text box:

1. The URL of your repository.
2. The link to your video (YouTube, unlisted).

Paste both into the box as plain links. The video link belongs here, not in `SUBMISSION.md` - putting it here is what makes it one click to open while your work is being graded. A video that has to be downloaded to watch is not graded, so YouTube unlisted only.
